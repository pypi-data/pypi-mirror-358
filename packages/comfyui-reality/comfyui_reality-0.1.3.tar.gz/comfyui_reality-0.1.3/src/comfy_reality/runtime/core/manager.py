"""Async task manager for runtime system."""

import asyncio
from collections import defaultdict
from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from contextvars import ContextVar
from datetime import datetime
from typing import Any, TypeVar

import structlog

from comfy_reality.runtime.core.exceptions import TaskError
from comfy_reality.runtime.models.tasks import Task, TaskEvent, TaskMetrics, TaskPriority, TaskStatus, TaskType

# Type aliases
TaskCallback = Callable[[TaskEvent], None]
AsyncTaskCallback = Callable[[TaskEvent], asyncio.Future[None]]
T = TypeVar("T")

# Context variables
current_task_var: ContextVar[Task | None] = ContextVar("current_task", default=None)


class AsyncTaskManager:
    """Manages async task execution with event-driven updates."""

    def __init__(self):
        self._tasks: dict[str, Task] = {}
        self._subscribers: list[TaskCallback | AsyncTaskCallback] = []
        self._lock = asyncio.Lock()
        self._task_queues: dict[TaskPriority, asyncio.Queue[Task]] = defaultdict(asyncio.Queue)
        self._running_tasks: set[str] = set()
        self.logger = structlog.get_logger(__name__)

    async def create_task(
        self,
        name: str,
        type: TaskType = TaskType.NODE,
        parent_id: str | None = None,
        priority: TaskPriority = TaskPriority.NORMAL,
        **metadata: Any,
    ) -> Task:
        """Create a new task."""
        async with self._lock:
            task = Task(type=type, name=name, parent_id=parent_id, priority=priority, metadata=metadata)
            self._tasks[task.id] = task

            await self._emit_event(TaskEvent(task_id=task.id, event_type="created", message=f"Task '{name}' created"))

            self.logger.info("task_created", task_id=task.id, task_name=name, task_type=type.value, parent_id=parent_id)

            return task

    @asynccontextmanager
    async def task_context(self, name: str, type: TaskType = TaskType.NODE, **metadata: Any) -> AsyncIterator[Task]:
        """Async context manager for task execution with automatic status updates."""
        task = await self.create_task(name, type, **metadata)
        token = current_task_var.set(task)

        try:
            # Mark as running
            async with self._lock:
                task.status = TaskStatus.RUNNING
                task.metrics.start_time = datetime.utcnow()
                self._running_tasks.add(task.id)

            await self._emit_event(TaskEvent(task_id=task.id, event_type="started", message=f"Task '{name}' started"))

            self.logger.info("task_started", task_id=task.id, task_name=name)

            yield task

            # Mark as completed
            async with self._lock:
                task.status = TaskStatus.COMPLETED
                task.metrics.end_time = datetime.utcnow()
                task.progress = 1.0
                self._running_tasks.discard(task.id)

            await self._emit_event(
                TaskEvent(task_id=task.id, event_type="completed", message=f"Task '{name}' completed in {task.duration:.2f}s")
            )

            self.logger.info("task_completed", task_id=task.id, task_name=name, duration_seconds=task.duration)

        except asyncio.CancelledError:
            async with self._lock:
                task.status = TaskStatus.CANCELLED
                task.metrics.end_time = datetime.utcnow()
                self._running_tasks.discard(task.id)

            await self._emit_event(TaskEvent(task_id=task.id, event_type="cancelled", message=f"Task '{name}' cancelled"))

            self.logger.warning("task_cancelled", task_id=task.id, task_name=name)
            raise

        except Exception as e:
            async with self._lock:
                task.status = TaskStatus.FAILED
                task.metrics.end_time = datetime.utcnow()
                task.error = str(e)
                task.error_type = type(e).__name__
                self._running_tasks.discard(task.id)

            await self._emit_event(
                TaskEvent(
                    task_id=task.id,
                    event_type="failed",
                    message=f"Task '{name}' failed: {e}",
                    data={"error": str(e), "type": type(e).__name__},
                )
            )

            self.logger.error("task_failed", task_id=task.id, task_name=name, error=str(e), error_type=type(e).__name__, exc_info=True)
            raise

        finally:
            current_task_var.reset(token)

    async def update_progress(self, task_id: str, progress: float, message: str | None = None) -> None:
        """Update task progress."""
        async with self._lock:
            if task := self._tasks.get(task_id):
                task.progress = max(0.0, min(1.0, progress))
                if message:
                    task.progress_message = message
                task.touch()

        await self._emit_event(TaskEvent(task_id=task_id, event_type="progress", data={"progress": progress}, message=message))

        self.logger.debug("task_progress", task_id=task_id, progress=progress, message=message)

    async def get_task(self, task_id: str) -> Task | None:
        """Get task by ID."""
        async with self._lock:
            return self._tasks.get(task_id)

    async def get_tasks(
        self, status: TaskStatus | None = None, type: TaskType | None = None, parent_id: str | None = None
    ) -> list[Task]:
        """Get tasks matching criteria."""
        async with self._lock:
            tasks = list(self._tasks.values())

        if status:
            tasks = [t for t in tasks if t.status == status]
        if type:
            tasks = [t for t in tasks if t.type == type]
        if parent_id is not None:
            tasks = [t for t in tasks if t.parent_id == parent_id]

        return tasks

    async def retry_task(self, task_id: str) -> bool:
        """Retry a failed task."""
        async with self._lock:
            task = self._tasks.get(task_id)
            if not task or not task.can_retry:
                return False

            task.status = TaskStatus.RETRYING
            task.retry_count += 1
            task.error = None
            task.error_type = None
            task.metrics = TaskMetrics()

        await self._emit_event(
            TaskEvent(task_id=task_id, event_type="retrying", message=f"Retrying task (attempt {task.retry_count}/{task.max_retries})")
        )

        self.logger.info("task_retry", task_id=task_id, retry_count=task.retry_count, max_retries=task.max_retries)

        return True

    def subscribe(self, callback: TaskCallback | AsyncTaskCallback) -> None:
        """Subscribe to task events."""
        self._subscribers.append(callback)

    def unsubscribe(self, callback: TaskCallback | AsyncTaskCallback) -> None:
        """Unsubscribe from task events."""
        if callback in self._subscribers:
            self._subscribers.remove(callback)

    async def _emit_event(self, event: TaskEvent) -> None:
        """Emit event to all subscribers."""
        # Notify subscribers
        for callback in self._subscribers:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(event)
                else:
                    callback(event)
            except Exception as e:
                self.logger.error("subscriber_error", error=str(e), event_type=event.event_type, task_id=event.task_id, exc_info=True)

    @property
    def stats(self) -> dict[str, Any]:
        """Get task statistics."""
        total = len(self._tasks)
        by_status = defaultdict(int)
        by_type = defaultdict(int)

        for task in self._tasks.values():
            by_status[task.status.value] += 1
            by_type[task.type.value] += 1

        return {"total": total, "running": len(self._running_tasks), "by_status": dict(by_status), "by_type": dict(by_type)}

    async def wait_for_completion(self, task_ids: list[str] | None = None, timeout: float | None = None) -> list[Task]:
        """Wait for tasks to complete."""
        if task_ids is None:
            task_ids = list(self._tasks.keys())

        async def check_complete():
            while True:
                async with self._lock:
                    tasks = [self._tasks.get(tid) for tid in task_ids if tid in self._tasks]
                    if all(t.is_complete for t in tasks if t):
                        return tasks
                await asyncio.sleep(0.1)

        try:
            return await asyncio.wait_for(check_complete(), timeout=timeout)
        except TimeoutError:
            raise TaskError(f"Timeout waiting for tasks: {task_ids}") from None
