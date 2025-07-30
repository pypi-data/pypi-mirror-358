"""Tests for async runtime components."""

import asyncio

import pytest

from comfy_reality.runtime import (
    AsyncTaskManager,
    Task,
    TaskStatus,
    TaskType,
)
from comfy_reality.runtime.models.tasks import TaskEvent
from comfy_reality.runtime.models.workflows import WorkflowExecution


@pytest.mark.asyncio
async def test_task_lifecycle():
    """Test basic task lifecycle."""
    manager = AsyncTaskManager()

    async with manager.task_context("Test Task") as task:
        assert task.status == TaskStatus.RUNNING
        assert task.metrics.start_time is not None
        await manager.update_progress(task.id, 0.5, "Half way")

    assert task.status == TaskStatus.COMPLETED
    assert task.progress == 1.0
    assert task.duration is not None


@pytest.mark.asyncio
async def test_task_failure():
    """Test task failure handling."""
    manager = AsyncTaskManager()

    with pytest.raises(ValueError):
        async with manager.task_context("Failing Task") as task:
            raise ValueError("Test error")

    # Check task was marked as failed
    failed_task = await manager.get_task(task.id)
    assert failed_task is not None
    assert failed_task.status == TaskStatus.FAILED
    assert failed_task.error == "Test error"
    assert failed_task.error_type == "ValueError"


@pytest.mark.asyncio
async def test_task_cancellation():
    """Test task cancellation."""
    manager = AsyncTaskManager()

    async def long_running_task():
        async with manager.task_context("Long Task") as task:
            await asyncio.sleep(10)  # Will be cancelled

    task_coro = asyncio.create_task(long_running_task())
    await asyncio.sleep(0.1)  # Let it start

    task_coro.cancel()

    with pytest.raises(asyncio.CancelledError):
        await task_coro

    # Check task was marked as cancelled
    tasks = await manager.get_tasks(status=TaskStatus.CANCELLED)
    assert len(tasks) == 1
    assert tasks[0].status == TaskStatus.CANCELLED


@pytest.mark.asyncio
async def test_concurrent_tasks():
    """Test concurrent task execution."""
    manager = AsyncTaskManager()

    async def worker(name: str, delay: float):
        async with manager.task_context(name) as task:
            await asyncio.sleep(delay)
            return task.id

    # Run tasks concurrently
    async with asyncio.TaskGroup() as tg:
        tasks = []
        for i in range(5):
            tasks.append(tg.create_task(worker(f"Task {i}", 0.1)))

    # Verify all completed
    all_tasks = await manager.get_tasks()
    assert len(all_tasks) == 5
    assert all(t.status == TaskStatus.COMPLETED for t in all_tasks)


@pytest.mark.asyncio
async def test_task_hierarchy():
    """Test parent-child task relationships."""
    manager = AsyncTaskManager()

    # Create parent task
    parent = await manager.create_task("Parent Task", TaskType.WORKFLOW)

    # Create child tasks
    child1 = await manager.create_task("Child 1", parent_id=parent.id)
    child2 = await manager.create_task("Child 2", parent_id=parent.id)

    # Get children
    children = await manager.get_tasks(parent_id=parent.id)
    assert len(children) == 2
    assert {c.id for c in children} == {child1.id, child2.id}


@pytest.mark.asyncio
async def test_task_retry():
    """Test task retry functionality."""
    manager = AsyncTaskManager()

    # Create failed task
    task = await manager.create_task("Retry Task", max_retries=3)
    async with manager._lock:
        task.status = TaskStatus.FAILED
        task.error = "Initial failure"

    # Retry task
    success = await manager.retry_task(task.id)
    assert success is True

    retried = await manager.get_task(task.id)
    assert retried is not None
    assert retried.status == TaskStatus.RETRYING
    assert retried.retry_count == 1
    assert retried.error is None


@pytest.mark.asyncio
async def test_task_events():
    """Test task event emission."""
    manager = AsyncTaskManager()
    events: list[TaskEvent] = []

    # Subscribe to events
    manager.subscribe(lambda e: events.append(e))

    # Create and complete task
    async with manager.task_context("Event Task") as task:
        await manager.update_progress(task.id, 0.5)

    # Check events
    event_types = [e.event_type for e in events]
    assert "created" in event_types
    assert "started" in event_types
    assert "progress" in event_types
    assert "completed" in event_types


@pytest.mark.asyncio
async def test_task_timeout():
    """Test task timeout handling."""
    manager = AsyncTaskManager()

    with pytest.raises(asyncio.TimeoutError):
        await manager.wait_for_completion(timeout=0.1)


@pytest.mark.asyncio
async def test_task_stats():
    """Test task statistics."""
    manager = AsyncTaskManager()

    # Create tasks with different statuses
    async with manager.task_context("Running") as t1:
        await manager.create_task("Pending")

        async with manager.task_context("Completed") as t2:
            pass

        # Check stats while running
        stats = manager.stats
        assert stats["total"] >= 3
        assert stats["running"] >= 1

    # Final stats
    final_stats = manager.stats
    assert final_stats["by_status"]["completed"] >= 2


@pytest.mark.asyncio
async def test_workflow_execution():
    """Test workflow execution tracking."""
    execution = WorkflowExecution(workflow_id="test-workflow", client_id="test-client")

    # Add tasks
    task1 = Task(name="Node 1", type=TaskType.NODE, status=TaskStatus.COMPLETED)
    task2 = Task(name="Node 2", type=TaskType.NODE, status=TaskStatus.FAILED)

    execution.add_task(task1)
    execution.add_task(task2)

    # Check metrics
    assert execution.total_tasks == 2
    assert execution.completed_tasks == 1
    assert execution.failed_tasks == 1

    # Update progress
    execution.update_progress()
    assert execution.progress == 0.5


@pytest.mark.asyncio
async def test_async_event_handler():
    """Test async event handler."""
    manager = AsyncTaskManager()
    processed_events: list[str] = []

    async def async_handler(event: TaskEvent):
        await asyncio.sleep(0.01)  # Simulate async work
        processed_events.append(event.event_type)

    manager.subscribe(async_handler)

    # Create task
    async with manager.task_context("Async Event Test"):
        pass

    # Wait for async processing
    await asyncio.sleep(0.1)

    assert "created" in processed_events
    assert "completed" in processed_events


@pytest.mark.asyncio
async def test_progress_validation():
    """Test progress value validation."""
    manager = AsyncTaskManager()

    task = await manager.create_task("Progress Test")

    # Test clamping
    await manager.update_progress(task.id, 1.5)  # Should clamp to 1.0
    updated = await manager.get_task(task.id)
    assert updated is not None
    assert updated.progress == 1.0

    await manager.update_progress(task.id, -0.5)  # Should clamp to 0.0
    updated = await manager.get_task(task.id)
    assert updated is not None
    assert updated.progress == 0.0
