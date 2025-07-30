# ComfyReality Async Runtime Architecture

## Overview

This document outlines the design for a modern, production-ready async runtime system for ComfyReality that integrates ComfyUI workflows with best-in-class Python async patterns inspired by FastAPI, FastHTML, and 2025 best practices.

## Architecture Goals

1. **Async-First**: All I/O operations use async/await patterns
2. **Type-Safe**: Full Pydantic validation for all data models
3. **Observable**: Real-time task status updates with structured logging
4. **Testable**: Dependency injection and clean separation of concerns
5. **Production-Ready**: Follows patterns approved by FastAPI/FastHTML teams
6. **Developer-Friendly**: Clean API with excellent error messages

## Core Components

### 1. Task Models (Pydantic)

```python
from pydantic import BaseModel, Field, ConfigDict
from typing import Literal, Optional, Any
from datetime import datetime
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskType(str, Enum):
    WORKFLOW = "workflow"
    NODE = "node"
    SYSTEM = "system"

class TaskEvent(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    task_id: str
    event_type: Literal["created", "started", "progress", "completed", "failed", "cancelled"]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    data: Optional[dict[str, Any]] = None
    message: Optional[str] = None

class Task(BaseModel):
    id: str
    type: TaskType
    status: TaskStatus = TaskStatus.PENDING
    name: str
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress: float = Field(default=0.0, ge=0.0, le=1.0)
    parent_id: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
    
    @property
    def duration(self) -> Optional[float]:
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

class WorkflowExecution(BaseModel):
    id: str
    workflow_id: str
    status: TaskStatus = TaskStatus.PENDING
    tasks: list[Task] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)
```

### 2. Async Task Manager

```python
import asyncio
from contextlib import asynccontextmanager
from typing import AsyncIterator, Callable, Optional
from contextvars import ContextVar
import structlog

# Context for current task
current_task_var: ContextVar[Optional[Task]] = ContextVar('current_task', default=None)

class AsyncTaskManager:
    def __init__(self):
        self._tasks: dict[str, Task] = {}
        self._subscribers: list[Callable[[TaskEvent], None]] = []
        self._lock = asyncio.Lock()
        self.logger = structlog.get_logger()
        
    async def create_task(
        self, 
        name: str, 
        type: TaskType = TaskType.NODE,
        parent_id: Optional[str] = None,
        **metadata
    ) -> Task:
        async with self._lock:
            task = Task(
                id=f"{type.value}_{asyncio.current_task().get_name()}_{len(self._tasks)}",
                type=type,
                name=name,
                parent_id=parent_id,
                metadata=metadata
            )
            self._tasks[task.id] = task
            
            await self._emit_event(TaskEvent(
                task_id=task.id,
                event_type="created",
                message=f"Task '{name}' created"
            ))
            
            return task
    
    @asynccontextmanager
    async def task_context(
        self, 
        name: str, 
        type: TaskType = TaskType.NODE,
        **metadata
    ) -> AsyncIterator[Task]:
        """Async context manager for task execution with automatic status updates"""
        task = await self.create_task(name, type, **metadata)
        token = current_task_var.set(task)
        
        try:
            # Mark as running
            async with self._lock:
                task.status = TaskStatus.RUNNING
                task.started_at = datetime.utcnow()
                
            await self._emit_event(TaskEvent(
                task_id=task.id,
                event_type="started",
                message=f"Task '{name}' started"
            ))
            
            yield task
            
            # Mark as completed
            async with self._lock:
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.utcnow()
                task.progress = 1.0
                
            await self._emit_event(TaskEvent(
                task_id=task.id,
                event_type="completed",
                message=f"Task '{name}' completed in {task.duration:.2f}s"
            ))
            
        except asyncio.CancelledError:
            async with self._lock:
                task.status = TaskStatus.CANCELLED
                task.completed_at = datetime.utcnow()
                
            await self._emit_event(TaskEvent(
                task_id=task.id,
                event_type="cancelled",
                message=f"Task '{name}' cancelled"
            ))
            raise
            
        except Exception as e:
            async with self._lock:
                task.status = TaskStatus.FAILED
                task.completed_at = datetime.utcnow()
                task.error = str(e)
                
            await self._emit_event(TaskEvent(
                task_id=task.id,
                event_type="failed",
                message=f"Task '{name}' failed: {e}",
                data={"error": str(e), "type": type(e).__name__}
            ))
            raise
            
        finally:
            current_task_var.reset(token)
    
    async def update_progress(self, task_id: str, progress: float, message: Optional[str] = None):
        async with self._lock:
            if task := self._tasks.get(task_id):
                task.progress = max(0.0, min(1.0, progress))
                
        await self._emit_event(TaskEvent(
            task_id=task_id,
            event_type="progress",
            data={"progress": progress},
            message=message
        ))
    
    def subscribe(self, callback: Callable[[TaskEvent], None]):
        self._subscribers.append(callback)
    
    async def _emit_event(self, event: TaskEvent):
        # Log structured event
        self.logger.info(
            event.event_type,
            task_id=event.task_id,
            message=event.message,
            data=event.data
        )
        
        # Notify subscribers
        for callback in self._subscribers:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(event)
                else:
                    callback(event)
            except Exception as e:
                self.logger.error(f"Subscriber error: {e}")
```

### 3. ComfyUI Async Runtime

```python
import httpx
import websockets
import json
from typing import AsyncIterator, Any

class ComfyUIAsyncRuntime:
    def __init__(self, server_url: str = "http://127.0.0.1:8188"):
        self.server_url = server_url
        self.ws_url = server_url.replace("http", "ws")
        self.task_manager = AsyncTaskManager()
        self.client = httpx.AsyncClient(timeout=30.0)
        
    @asynccontextmanager
    async def session(self):
        """Managed ComfyUI session with cleanup"""
        try:
            yield self
        finally:
            await self.client.aclose()
    
    async def execute_workflow(
        self, 
        workflow: dict[str, Any],
        client_id: Optional[str] = None
    ) -> WorkflowExecution:
        """Execute a ComfyUI workflow with real-time progress tracking"""
        
        if client_id is None:
            client_id = str(uuid.uuid4())
            
        execution = WorkflowExecution(
            id=client_id,
            workflow_id=workflow.get("id", "unknown"),
            metadata={"workflow": workflow}
        )
        
        async with self.task_manager.task_context(
            f"Workflow: {execution.workflow_id}",
            TaskType.WORKFLOW
        ) as main_task:
            # Queue the workflow
            response = await self.client.post(
                f"{self.server_url}/prompt",
                json={"prompt": workflow, "client_id": client_id}
            )
            response.raise_for_status()
            
            prompt_id = response.json()["prompt_id"]
            
            # Track execution via WebSocket
            async with websockets.connect(
                f"{self.ws_url}/ws?clientId={client_id}"
            ) as websocket:
                async for message in self._track_execution(
                    websocket, prompt_id, main_task.id
                ):
                    # Process real-time updates
                    if message["type"] == "progress":
                        await self.task_manager.update_progress(
                            main_task.id,
                            message["value"] / message["max"],
                            f"Processing: {message.get('node', 'Unknown')}"
                        )
                    elif message["type"] == "executed":
                        # Node completed
                        pass
                        
            # Fetch results
            results = await self._get_results(prompt_id)
            execution.status = TaskStatus.COMPLETED
            
        return execution
    
    async def _track_execution(
        self, 
        websocket, 
        prompt_id: str,
        parent_task_id: str
    ) -> AsyncIterator[dict]:
        """Track workflow execution via WebSocket"""
        node_tasks = {}
        
        async for message in websocket:
            data = json.loads(message)
            
            if data["type"] == "executing":
                node_id = data["data"]["node"]
                
                if node_id and node_id not in node_tasks:
                    # Create task for node
                    task = await self.task_manager.create_task(
                        f"Node: {node_id}",
                        TaskType.NODE,
                        parent_id=parent_task_id
                    )
                    node_tasks[node_id] = task
                    
            elif data["type"] == "progress":
                yield {
                    "type": "progress",
                    "node": data.get("data", {}).get("node"),
                    "value": data["data"]["value"],
                    "max": data["data"]["max"]
                }
                
            elif data["type"] == "executed":
                node_id = data["data"]["node"]
                if task := node_tasks.get(node_id):
                    task.status = TaskStatus.COMPLETED
                    task.completed_at = datetime.utcnow()
                    
                yield {"type": "executed", "node": node_id}
                
            elif data["type"] == "execution_complete":
                break
```

### 4. Task Printer (Rich Terminal UI)

```python
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
import asyncio

class RichTaskPrinter:
    def __init__(self):
        self.console = Console()
        self.tasks: dict[str, dict] = {}
        self._lock = asyncio.Lock()
        
    async def start(self, task_manager: AsyncTaskManager):
        """Start the live task display"""
        task_manager.subscribe(self._handle_event)
        
        with Live(self._render(), console=self.console, refresh_per_second=10) as live:
            self.live = live
            while True:
                await asyncio.sleep(0.1)
                live.update(self._render())
    
    async def _handle_event(self, event: TaskEvent):
        """Handle task events and update display"""
        async with self._lock:
            if event.event_type == "created":
                self.tasks[event.task_id] = {
                    "name": event.message.split("'")[1],
                    "status": "⏳ Pending",
                    "progress": 0.0,
                    "start_time": None
                }
            elif event.event_type == "started":
                self.tasks[event.task_id]["status"] = "🚀 Running"
                self.tasks[event.task_id]["start_time"] = event.timestamp
            elif event.event_type == "progress":
                if event.data:
                    self.tasks[event.task_id]["progress"] = event.data.get("progress", 0)
                if event.message:
                    self.tasks[event.task_id]["status"] = f"🚀 {event.message}"
            elif event.event_type == "completed":
                self.tasks[event.task_id]["status"] = "✅ Completed"
                self.tasks[event.task_id]["progress"] = 1.0
            elif event.event_type == "failed":
                self.tasks[event.task_id]["status"] = f"❌ Failed: {event.data.get('error', 'Unknown')}"
            elif event.event_type == "cancelled":
                self.tasks[event.task_id]["status"] = "🚫 Cancelled"
    
    def _render(self) -> Panel:
        """Render the current task state"""
        table = Table(title="ComfyReality Task Status", expand=True)
        table.add_column("Task", style="cyan", no_wrap=True)
        table.add_column("Status", style="magenta")
        table.add_column("Progress", justify="right", style="green")
        table.add_column("Duration", justify="right")
        
        for task_id, info in self.tasks.items():
            progress_bar = self._make_progress_bar(info["progress"])
            
            duration = ""
            if info["start_time"]:
                elapsed = (datetime.utcnow() - info["start_time"]).total_seconds()
                duration = f"{elapsed:.1f}s"
                
            table.add_row(
                info["name"],
                info["status"],
                progress_bar,
                duration
            )
            
        return Panel(table, title="🎨 ComfyReality Runtime", border_style="blue")
    
    def _make_progress_bar(self, progress: float) -> str:
        """Create a simple progress bar"""
        filled = int(progress * 20)
        return f"[{'█' * filled}{'░' * (20 - filled)}] {progress*100:.0f}%"
```

### 5. Integration with UV/Poe Tasks

Add to `pyproject.toml`:

```toml
[tool.poe.tasks]
# Async runtime tasks
serve = "python -m comfy_reality.runtime.server"
worker = "python -m comfy_reality.runtime.worker"
process = "python -m comfy_reality.runtime.processor"

# Development with live reload
dev-serve = "python -m comfy_reality.runtime.server --reload"
dev-worker = "python -m comfy_reality.runtime.worker --debug"

# Workflow execution
run-workflow = "python -m comfy_reality.runtime.cli run"
validate-workflow = "python -m comfy_reality.runtime.cli validate"

# Task monitoring
monitor = "python -m comfy_reality.runtime.monitor"
logs = "tail -f logs/comfy_reality.log | jq"

[tool.poe.tasks.test-async]
cmd = "pytest tests/test_async_runtime.py -v"
help = "Test async runtime components"

[tool.poe.tasks.benchmark]
shell = """
echo "Running async benchmark..."
python -m comfy_reality.runtime.benchmark
"""
help = "Benchmark async performance"
```

## Usage Example

```python
# cli.py
import asyncio
import click
from comfy_reality.runtime import ComfyUIAsyncRuntime, RichTaskPrinter

@click.command()
@click.argument('workflow_file', type=click.Path(exists=True))
async def run_workflow(workflow_file: str):
    """Execute a ComfyUI workflow with real-time progress"""
    
    # Load workflow
    with open(workflow_file) as f:
        workflow = json.load(f)
    
    # Create runtime
    runtime = ComfyUIAsyncRuntime()
    printer = RichTaskPrinter()
    
    # Execute with live updates
    async with runtime.session():
        # Start printer in background
        printer_task = asyncio.create_task(
            printer.start(runtime.task_manager)
        )
        
        try:
            # Execute workflow
            result = await runtime.execute_workflow(workflow)
            printer.console.print(
                f"[green]✅ Workflow completed successfully![/green]"
            )
            
        except Exception as e:
            printer.console.print(
                f"[red]❌ Workflow failed: {e}[/red]"
            )
            raise
            
        finally:
            printer_task.cancel()

if __name__ == "__main__":
    asyncio.run(run_workflow())
```

## Testing Strategy

```python
# tests/test_async_runtime.py
import pytest
import asyncio
from comfy_reality.runtime import AsyncTaskManager, TaskStatus

@pytest.mark.asyncio
async def test_task_lifecycle():
    manager = AsyncTaskManager()
    
    async with manager.task_context("Test Task") as task:
        assert task.status == TaskStatus.RUNNING
        await manager.update_progress(task.id, 0.5, "Half way")
        
    assert task.status == TaskStatus.COMPLETED
    assert task.progress == 1.0
    assert task.duration is not None

@pytest.mark.asyncio
async def test_concurrent_tasks():
    manager = AsyncTaskManager()
    
    async def worker(name: str, delay: float):
        async with manager.task_context(name) as task:
            await asyncio.sleep(delay)
            
    # Run tasks concurrently
    async with asyncio.TaskGroup() as tg:
        for i in range(5):
            tg.create_task(worker(f"Task {i}", 0.1))
            
    # Verify all completed
    assert len(manager._tasks) == 5
    assert all(t.status == TaskStatus.COMPLETED for t in manager._tasks.values())
```

## Benefits of This Architecture

1. **Type Safety**: Full Pydantic validation ensures data integrity
2. **Observability**: Real-time task tracking with structured logging
3. **Scalability**: Async-first design handles concurrent workflows efficiently
4. **Testability**: Clean separation of concerns and dependency injection
5. **Developer Experience**: Rich terminal UI and clear error messages
6. **Production Ready**: Follows patterns from FastAPI/FastHTML
7. **Extensible**: Easy to add new task types and monitoring capabilities