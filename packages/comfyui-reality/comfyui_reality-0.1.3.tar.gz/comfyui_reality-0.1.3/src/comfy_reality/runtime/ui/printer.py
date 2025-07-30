"""Rich terminal UI for task tracking."""

import asyncio
from collections import OrderedDict
from datetime import datetime
from typing import Any

from rich import box
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

from comfy_reality.runtime.core.manager import AsyncTaskManager
from comfy_reality.runtime.models.tasks import TaskEvent, TaskStatus


class RichTaskPrinter:
    """Rich terminal UI for displaying task progress."""

    def __init__(self, refresh_rate: float = 0.5):
        self.console = Console()
        self.tasks: OrderedDict[str, dict[str, Any]] = OrderedDict()
        self._lock = asyncio.Lock()
        self.refresh_rate = refresh_rate
        self._running = False
        self._start_time = datetime.utcnow()

    async def start(self, task_manager: AsyncTaskManager):
        """Start the live task display."""
        task_manager.subscribe(self._handle_event)
        self._running = True

        with Live(self._render(), console=self.console, refresh_per_second=1 / self.refresh_rate, screen=False) as live:
            self.live = live
            while self._running:
                await asyncio.sleep(self.refresh_rate)
                live.update(self._render())

    async def stop(self):
        """Stop the display."""
        self._running = False

    async def _handle_event(self, event: TaskEvent):
        """Handle task events and update display."""
        async with self._lock:
            task_data = self.tasks.setdefault(
                event.task_id,
                {
                    "name": "Unknown",
                    "status": TaskStatus.PENDING,
                    "progress": 0.0,
                    "start_time": None,
                    "end_time": None,
                    "message": "",
                    "parent_id": None,
                    "children": [],
                },
            )

            if event.event_type == "created":
                task_data["name"] = event.message.split("'")[1] if "'" in event.message else event.task_id
                task_data["status"] = TaskStatus.PENDING
                task_data["parent_id"] = event.data.get("parent_id")

                # Add to parent's children if applicable
                if task_data["parent_id"] and task_data["parent_id"] in self.tasks:
                    self.tasks[task_data["parent_id"]]["children"].append(event.task_id)

            elif event.event_type == "started":
                task_data["status"] = TaskStatus.RUNNING
                task_data["start_time"] = event.timestamp

            elif event.event_type == "progress":
                if event.data:
                    task_data["progress"] = event.data.get("progress", 0)
                if event.message:
                    task_data["message"] = event.message

            elif event.event_type == "completed":
                task_data["status"] = TaskStatus.COMPLETED
                task_data["progress"] = 1.0
                task_data["end_time"] = event.timestamp

            elif event.event_type == "failed":
                task_data["status"] = TaskStatus.FAILED
                task_data["end_time"] = event.timestamp
                if event.data and "error" in event.data:
                    task_data["message"] = f"Error: {event.data['error']}"

            elif event.event_type == "cancelled":
                task_data["status"] = TaskStatus.CANCELLED
                task_data["end_time"] = event.timestamp

    def _render(self) -> Panel:
        """Render the current task state."""
        layout = Layout()

        # Header
        header = self._render_header()

        # Task tree or table
        if self._has_hierarchy():
            content = self._render_tree()
        else:
            content = self._render_table()

        # Stats
        stats = self._render_stats()

        # Combine into layout
        layout.split_column(Layout(header, size=3), Layout(content), Layout(stats, size=4))

        return Panel(layout, title="🎨 ComfyReality Runtime", title_align="left", border_style="blue", box=box.ROUNDED)

    def _render_header(self) -> Panel:
        """Render header with runtime info."""
        elapsed = (datetime.utcnow() - self._start_time).total_seconds()
        elapsed_str = f"{int(elapsed // 60):02d}:{int(elapsed % 60):02d}"

        header_text = Text()
        header_text.append("Runtime: ", style="bold cyan")
        header_text.append(elapsed_str, style="bold white")
        header_text.append(" | ", style="dim")
        header_text.append("Tasks: ", style="bold cyan")
        header_text.append(str(len(self.tasks)), style="bold white")

        return Panel(header_text, box=box.SIMPLE)

    def _render_table(self) -> Table:
        """Render tasks as a table."""
        table = Table(title="Task Status", expand=True, show_header=True, header_style="bold cyan", box=box.ROUNDED)

        table.add_column("Task", style="cyan", no_wrap=True)
        table.add_column("Status", style="magenta")
        table.add_column("Progress", justify="right", style="green")
        table.add_column("Duration", justify="right")
        table.add_column("Message", style="dim")

        for _task_id, info in self.tasks.items():
            status_icon = self._get_status_icon(info["status"])
            progress_bar = self._make_progress_bar(info["progress"])
            duration = self._calculate_duration(info)

            table.add_row(
                info["name"],
                f"{status_icon} {info['status'].value}",
                progress_bar,
                duration,
                info["message"][:50] + "..." if len(info["message"]) > 50 else info["message"],
            )

        return table

    def _render_tree(self) -> Tree:
        """Render tasks as a tree."""
        tree = Tree("📋 Task Hierarchy", style="cyan", guide_style="dim")

        # Build tree for root tasks
        for task_id, info in self.tasks.items():
            if not info["parent_id"]:
                self._add_tree_node(tree, task_id, info)

        return tree

    def _add_tree_node(self, parent: Tree, task_id: str, info: dict[str, Any]):
        """Add a task node to the tree."""
        status_icon = self._get_status_icon(info["status"])
        progress = f"{info['progress'] * 100:.0f}%"
        duration = self._calculate_duration(info)

        label = Text()
        label.append(f"{status_icon} ", style="bold")
        label.append(info["name"], style="cyan")
        label.append(f" [{progress}]", style="green")
        if duration:
            label.append(f" ({duration})", style="dim")

        node = parent.add(label)

        # Add children
        for child_id in info["children"]:
            if child_id in self.tasks:
                self._add_tree_node(node, child_id, self.tasks[child_id])

    def _render_stats(self) -> Panel:
        """Render task statistics."""
        stats = self._calculate_stats()

        stats_text = Text()
        stats_text.append("Statistics\n", style="bold underline")
        stats_text.append(f"Total: {stats['total']} | ", style="dim")
        stats_text.append(f"✅ {stats['completed']} | ", style="green")
        stats_text.append(f"🚀 {stats['running']} | ", style="yellow")
        stats_text.append(f"⏳ {stats['pending']} | ", style="blue")
        stats_text.append(f"❌ {stats['failed']}", style="red")

        return Panel(stats_text, box=box.SIMPLE)

    def _get_status_icon(self, status: TaskStatus) -> str:
        """Get icon for task status."""
        icons = {
            TaskStatus.PENDING: "⏳",
            TaskStatus.QUEUED: "📋",
            TaskStatus.RUNNING: "🚀",
            TaskStatus.COMPLETED: "✅",
            TaskStatus.FAILED: "❌",
            TaskStatus.CANCELLED: "🚫",
            TaskStatus.RETRYING: "🔄",
        }
        return icons.get(status, "❓")

    def _make_progress_bar(self, progress: float) -> str:
        """Create a simple progress bar."""
        filled = int(progress * 20)
        bar = "█" * filled + "░" * (20 - filled)
        percentage = f"{progress * 100:>3.0f}%"
        return f"[{bar}] {percentage}"

    def _calculate_duration(self, info: dict[str, Any]) -> str:
        """Calculate task duration."""
        if info["start_time"]:
            if info["end_time"]:
                duration = (info["end_time"] - info["start_time"]).total_seconds()
            else:
                duration = (datetime.utcnow() - info["start_time"]).total_seconds()
            return f"{duration:.1f}s"
        return ""

    def _has_hierarchy(self) -> bool:
        """Check if tasks have parent-child relationships."""
        return any(info["parent_id"] for info in self.tasks.values())

    def _calculate_stats(self) -> dict[str, int]:
        """Calculate task statistics."""
        stats = {"total": len(self.tasks), "pending": 0, "running": 0, "completed": 0, "failed": 0}

        for info in self.tasks.values():
            status = info["status"]
            if status == TaskStatus.PENDING:
                stats["pending"] += 1
            elif status in (TaskStatus.RUNNING, TaskStatus.RETRYING):
                stats["running"] += 1
            elif status == TaskStatus.COMPLETED:
                stats["completed"] += 1
            elif status == TaskStatus.FAILED:
                stats["failed"] += 1

        return stats
