"""ComfyUI async runtime implementation."""

import asyncio
import json
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any

import httpx
import structlog
import websockets

from comfy_reality.runtime.core.exceptions import RuntimeError, WorkflowError
from comfy_reality.runtime.core.manager import AsyncTaskManager
from comfy_reality.runtime.models.config import RuntimeConfig
from comfy_reality.runtime.models.tasks import TaskStatus, TaskType
from comfy_reality.runtime.models.workflows import WorkflowDefinition, WorkflowExecution


class ComfyUIAsyncRuntime:
    """Async runtime for executing ComfyUI workflows."""

    def __init__(self, config: RuntimeConfig | None = None, task_manager: AsyncTaskManager | None = None):
        self.config = config or RuntimeConfig()
        self.server_config = self.config.server
        self.task_manager = task_manager or AsyncTaskManager()
        self.client = httpx.AsyncClient(timeout=self.server_config.timeout_seconds)
        self.logger = structlog.get_logger(__name__)

    @asynccontextmanager
    async def session(self):
        """Managed ComfyUI session with cleanup."""
        try:
            yield self
        finally:
            await self.close()

    async def close(self):
        """Close the runtime and cleanup resources."""
        await self.client.aclose()

    async def execute_workflow(
        self, workflow: str | dict[str, Any] | WorkflowDefinition, client_id: str | None = None, timeout: float | None = None
    ) -> WorkflowExecution:
        """Execute a ComfyUI workflow with real-time progress tracking."""

        if client_id is None:
            client_id = str(uuid.uuid4())

        # Convert workflow to dict if needed
        if isinstance(workflow, WorkflowDefinition):
            workflow_data = self._workflow_to_comfy_format(workflow)
            workflow_id = workflow.id
        elif isinstance(workflow, str):
            # Assume it's a workflow ID, load it
            workflow_data = await self._load_workflow(workflow)
            workflow_id = workflow
        else:
            workflow_data = workflow
            workflow_id = workflow.get("id", "unknown")

        execution = WorkflowExecution(workflow_id=workflow_id, client_id=client_id, metadata={"workflow": workflow_data})

        async with self.task_manager.task_context(f"Workflow: {execution.workflow_id}", TaskType.WORKFLOW) as main_task:
            execution.root_task_id = main_task.id

            try:
                # Queue the workflow
                prompt_id = await self._queue_workflow(workflow_data, client_id)

                # Track execution via WebSocket
                await self._track_execution(prompt_id, client_id, execution, main_task.id, timeout)

                # Fetch results
                results = await self._get_results(prompt_id)
                execution.outputs = results
                execution.status = TaskStatus.COMPLETED
                execution.total_duration_seconds = main_task.duration

            except Exception as e:
                execution.status = TaskStatus.FAILED
                raise WorkflowError(f"Workflow execution failed: {e}", workflow_id=execution.workflow_id) from e

        return execution

    async def _queue_workflow(self, workflow: dict[str, Any], client_id: str) -> str:
        """Queue workflow for execution."""
        self.logger.info("queueing_workflow", client_id=client_id, node_count=len(workflow))

        response = await self.client.post(
            f"{self.server_config.url}/prompt", json={"prompt": workflow, "client_id": client_id}, headers=self._get_headers()
        )

        if response.status_code != 200:
            raise RuntimeError(f"Failed to queue workflow: {response.status_code} {response.text}")

        data = response.json()
        prompt_id = data.get("prompt_id")

        if not prompt_id:
            raise RuntimeError("No prompt_id returned from server")

        self.logger.info("workflow_queued", prompt_id=prompt_id, client_id=client_id)

        return prompt_id

    async def _track_execution(
        self, prompt_id: str, client_id: str, execution: WorkflowExecution, parent_task_id: str, timeout: float | None = None
    ) -> None:
        """Track workflow execution via WebSocket."""
        ws_url = f"{self.server_config.websocket_url}/ws?clientId={client_id}"

        self.logger.info("connecting_websocket", url=ws_url, prompt_id=prompt_id)

        node_tasks = {}
        start_time = asyncio.get_event_loop().time()

        async with websockets.connect(ws_url) as websocket:
            async for message in websocket:
                # Check timeout
                if timeout and (asyncio.get_event_loop().time() - start_time) > timeout:
                    raise TimeoutError(f"Workflow execution timed out after {timeout}s")

                data = json.loads(message)
                event_type = data.get("type")

                if event_type == "executing":
                    node_id = data.get("data", {}).get("node")

                    if node_id and node_id not in node_tasks:
                        # Create task for node
                        task = await self.task_manager.create_task(f"Node: {node_id}", TaskType.NODE, parent_id=parent_task_id)
                        node_tasks[node_id] = task
                        execution.add_task(task)

                        # Start node execution
                        async with self.task_manager._lock:
                            task.status = TaskStatus.RUNNING
                            task.metrics.start_time = datetime.utcnow()

                elif event_type == "progress":
                    node_id = data.get("data", {}).get("node")
                    value = data.get("data", {}).get("value", 0)
                    max_value = data.get("data", {}).get("max", 100)

                    if node_id in node_tasks:
                        progress = value / max_value if max_value > 0 else 0
                        await self.task_manager.update_progress(node_tasks[node_id].id, progress, f"Processing: {value}/{max_value}")

                elif event_type == "executed":
                    node_id = data.get("data", {}).get("node")
                    output = data.get("data", {}).get("output")

                    if node_id in node_tasks:
                        task = node_tasks[node_id]
                        async with self.task_manager._lock:
                            task.status = TaskStatus.COMPLETED
                            task.metrics.end_time = datetime.utcnow()
                            task.result = output
                            task.progress = 1.0

                        # Store node metrics
                        execution.node_metrics[node_id] = task.metrics

                elif event_type == "execution_error":
                    node_id = data.get("data", {}).get("node")
                    error = data.get("data", {}).get("error")

                    if node_id in node_tasks:
                        task = node_tasks[node_id]
                        async with self.task_manager._lock:
                            task.status = TaskStatus.FAILED
                            task.metrics.end_time = datetime.utcnow()
                            task.error = str(error)

                    raise WorkflowError(f"Node {node_id} failed: {error}")

                elif event_type == "execution_complete":
                    self.logger.info("execution_complete", prompt_id=prompt_id, node_count=len(node_tasks))
                    break

                # Update execution progress
                execution.update_progress()
                await self.task_manager.update_progress(
                    parent_task_id, execution.progress, f"Nodes: {execution.completed_tasks}/{execution.total_tasks}"
                )

    async def _get_results(self, prompt_id: str) -> dict[str, Any]:
        """Fetch execution results."""
        response = await self.client.get(f"{self.server_config.url}/history/{prompt_id}", headers=self._get_headers())

        if response.status_code != 200:
            raise RuntimeError(f"Failed to fetch results: {response.status_code} {response.text}")

        history = response.json()

        # Extract outputs from history
        if prompt_id in history:
            return history[prompt_id].get("outputs", {})

        return {}

    async def _load_workflow(self, workflow_id: str) -> dict[str, Any]:
        """Load workflow by ID."""
        # This would typically load from a database or file
        # For now, raise an error
        raise NotImplementedError(f"Loading workflow by ID not implemented: {workflow_id}")

    def _workflow_to_comfy_format(self, workflow: WorkflowDefinition) -> dict[str, Any]:
        """Convert WorkflowDefinition to ComfyUI format."""
        result = {}

        for node_id, node in workflow.nodes.items():
            result[node_id] = {"class_type": node.type, "inputs": node.inputs}

        return result

    def _get_headers(self) -> dict[str, str]:
        """Get request headers."""
        headers = {}

        if self.server_config.api_key:
            headers["Authorization"] = f"Bearer {self.server_config.api_key}"
        elif self.server_config.auth_header:
            headers["Authorization"] = self.server_config.auth_header

        return headers

    async def get_system_stats(self) -> dict[str, Any]:
        """Get ComfyUI system statistics."""
        response = await self.client.get(f"{self.server_config.url}/system_stats", headers=self._get_headers())

        if response.status_code != 200:
            raise RuntimeError(f"Failed to get system stats: {response.status_code}")

        return response.json()

    async def interrupt_execution(self) -> bool:
        """Interrupt current execution."""
        response = await self.client.post(f"{self.server_config.url}/interrupt", headers=self._get_headers())

        return response.status_code == 200
