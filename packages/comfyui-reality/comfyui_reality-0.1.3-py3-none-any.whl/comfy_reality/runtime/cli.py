"""CLI for ComfyReality runtime."""

import asyncio
import json
import sys

import click
import structlog
from rich.console import Console

from comfy_reality.runtime import AsyncTaskManager, ComfyUIAsyncRuntime, RichTaskPrinter
from comfy_reality.runtime.models.config import RuntimeConfig
from comfy_reality.runtime.models.workflows import WorkflowDefinition

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.dev.ConsoleRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

console = Console()


@click.group()
@click.option("--config", type=click.Path(exists=True), help="Config file path")
@click.pass_context
def cli(ctx, config: str | None):
    """ComfyReality Runtime CLI."""
    if config:
        with open(config) as f:
            config_data = json.load(f)
        ctx.obj = RuntimeConfig(**config_data)
    else:
        ctx.obj = RuntimeConfig.from_env()


@cli.command()
@click.argument("workflow_file", type=click.Path(exists=True))
@click.option("--timeout", type=float, help="Execution timeout in seconds")
@click.option("--no-ui", is_flag=True, help="Disable UI output")
@click.option("--output", "-o", type=click.Path(), help="Output file for results")
@click.pass_obj
def run(config: RuntimeConfig, workflow_file: str, timeout: float | None, no_ui: bool, output: str | None):
    """Execute a ComfyUI workflow with real-time progress."""

    async def _run():
        # Load workflow
        with open(workflow_file) as f:
            workflow_data = json.load(f)

        # Create runtime components
        task_manager = AsyncTaskManager()
        runtime = ComfyUIAsyncRuntime(config, task_manager)

        if not no_ui:
            printer = RichTaskPrinter()
            printer_task = asyncio.create_task(printer.start(task_manager))

        try:
            # Execute workflow
            async with runtime.session():
                result = await runtime.execute_workflow(workflow_data, timeout=timeout)

            if not no_ui:
                console.print("\n[green]✅ Workflow completed successfully![/green]")
                console.print(f"Duration: {result.total_duration_seconds:.2f}s")
                console.print(f"Tasks: {result.completed_tasks}/{result.total_tasks}")

            # Save output if requested
            if output:
                output_data = {
                    "execution_id": result.id,
                    "workflow_id": result.workflow_id,
                    "status": result.status.value,
                    "duration_seconds": result.total_duration_seconds,
                    "outputs": result.outputs,
                    "artifacts": result.artifacts,
                    "metrics": {node_id: metrics.model_dump() for node_id, metrics in result.node_metrics.items()},
                }

                with open(output, "w") as f:
                    json.dump(output_data, f, indent=2)

                console.print(f"[dim]Results saved to: {output}[/dim]")

        except Exception as e:
            console.print(f"[red]❌ Workflow failed: {e}[/red]")
            sys.exit(1)

        finally:
            if not no_ui:
                await printer.stop()
                printer_task.cancel()
                try:
                    await printer_task
                except asyncio.CancelledError:
                    pass

    asyncio.run(_run())


@cli.command()
@click.argument("workflow_file", type=click.Path(exists=True))
@click.pass_obj
def validate(config: RuntimeConfig, workflow_file: str):
    """Validate a workflow file."""
    try:
        with open(workflow_file) as f:
            data = json.load(f)

        # Try to parse as WorkflowDefinition
        workflow = WorkflowDefinition.from_comfy_format(data)

        console.print("[green]✅ Workflow is valid[/green]")
        console.print(f"Name: {workflow.name}")
        console.print(f"Nodes: {len(workflow.nodes)}")
        console.print(f"Edges: {len(workflow.edges)}")

    except Exception as e:
        console.print(f"[red]❌ Invalid workflow: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.pass_obj
def status(config: RuntimeConfig):
    """Check ComfyUI server status."""

    async def _status():
        runtime = ComfyUIAsyncRuntime(config)

        try:
            async with runtime.session():
                stats = await runtime.get_system_stats()

            console.print("[green]✅ Server is running[/green]")
            console.print(f"URL: {config.server.url}")

            # Display system stats
            if stats:
                console.print("\n[bold]System Statistics:[/bold]")
                for key, value in stats.items():
                    console.print(f"  {key}: {value}")

        except Exception as e:
            console.print(f"[red]❌ Server error: {e}[/red]")
            sys.exit(1)

    asyncio.run(_status())


@cli.command()
@click.option("--example", type=click.Choice(["simple", "complex"]), default="simple")
@click.option("--output", "-o", type=click.Path(), default="example_workflow.json")
def generate(example: str, output: str):
    """Generate example workflow files."""

    examples = {
        "simple": {
            "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "model.safetensors"}},
            "2": {"class_type": "EmptyLatentImage", "inputs": {"width": 512, "height": 512, "batch_size": 1}},
            "3": {
                "class_type": "KSampler",
                "inputs": {
                    "model": ["1", 0],
                    "positive": ["1", 1],
                    "negative": ["1", 2],
                    "latent_image": ["2", 0],
                    "seed": 42,
                    "steps": 20,
                    "cfg": 8.0,
                    "sampler_name": "euler",
                    "scheduler": "normal",
                    "denoise": 1.0,
                },
            },
        },
        "complex": {
            # Add more complex example here
        },
    }

    workflow = examples[example]

    with open(output, "w") as f:
        json.dump(workflow, f, indent=2)

    console.print(f"[green]✅ Generated {example} workflow: {output}[/green]")


if __name__ == "__main__":
    cli()
