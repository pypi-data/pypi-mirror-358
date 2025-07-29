import json
from datetime import datetime

import click
from rich import box
from rich.console import Console
from rich.syntax import Syntax
from rich.table import Table

from doteval.models import EvaluationSummary
from doteval.sessions import SessionManager, SessionStatus
from doteval.storage.json import serialize

console = Console()


@click.group()
def cli():
    """doteval CLI to manager evaluation sessions."""


@cli.command()
@click.option("--name", help="Filter sessions by name.")
@click.option(
    "--status",
    type=click.Choice(["Running", "Completed", "Failed"]),
    help="Filter by session status.",
)
@click.option("--storage", default="json://.doteval", help="Storage backend path")
def list(name, status, storage):
    """List available session"""
    manager = SessionManager(storage)
    session_names = manager.list_sessions()

    if not session_names:
        console.print(f"[yellow]No sessions found at {storage}.[/yellow]")
        return

    table = Table(title="Available sessions", box=box.SIMPLE)
    table.add_column("Session Name")
    table.add_column("Status")
    table.add_column("Created")

    for session_name in session_names:
        session = manager.get_session(session_name)
        session_status = session.status.value

        # Determine the actual session state for CLI display
        if session.status == SessionStatus.running:
            if manager.storage.is_locked(session_name):
                session_status = "Running"
            else:
                session_status = "Interrupted"  # Process died without calling finish()
        elif session.status == SessionStatus.failed:
            session_status = "Has errors"
        # SessionStatus.completed stays as "Completed"

        if name and name not in session_name:
            continue
        if status and session_status != status:
            continue

        session = manager.get_session(session_name)
        created_at = datetime.fromtimestamp(session.created_at).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        table.add_row(session_name, session_status, created_at)

    console.print(table)


@cli.command()
@click.argument("session_name")
@click.option("--storage", default="json://.doteval", help="Storage backend path")
@click.option("--full", is_flag=True, help="Show full details.")
@click.option("--errors", is_flag=True, help="Show detailed error information.")
def show(session_name, storage, full, errors):
    """Show results of a session."""
    manager = SessionManager(storage)
    session = manager.get_session(session_name)

    if not session:
        console.print(f"[red]Session '{session_name}' not found.[/red]")
        return

    if full:
        with console.pager():
            serialized_session = serialize(session)
            content = json.dumps(serialized_session, indent=2)
            syntax = Syntax(content, "json", theme="monokai", line_numbers=True)
            console.print(syntax)
        return

    results = {eval_name: results for eval_name, results in session.results.items()}
    summaries = {
        eval_name: EvaluationSummary(results).summary
        for eval_name, results in results.items()
    }

    for eval_name, evaluation_results in results.items():
        table = Table(title=f"Summary of Session '{session_name}'", box=box.SIMPLE)
        table.add_column("Evaluator")
        table.add_column("Metric")
        table.add_column("Score", justify="right")
        table.add_column("Errors", justify="right")

        # Count errors
        total_items = len(evaluation_results)
        error_count = sum(
            1 for result in evaluation_results if result.error is not None
        )
        error_percentage = (error_count / total_items * 100) if total_items > 0 else 0

        evaluation_summary = summaries.get(eval_name, {})
        for evaluator, metrics in evaluation_summary.items():
            for metric_name, score in metrics.items():
                error_display = f"{error_count}/{total_items} ({error_percentage:.1f}%)"
                if error_count > 0:
                    error_display = f"[red]{error_display}[/red]"
                    # Calculate metric excluding errors
                    successful_results = [
                        r for r in evaluation_results if r.error is None
                    ]
                    if successful_results:
                        # Recompute metric for successful results only
                        successful_summary = EvaluationSummary(
                            successful_results
                        ).summary
                        score_without_errors = successful_summary.get(
                            evaluator, {}
                        ).get(metric_name, 0)
                        score_display = (
                            f"{score:.2f} ({score_without_errors:.2f} excluding errors)"
                        )
                    else:
                        score_display = f"{score:.2f}"
                else:
                    score_display = f"{score:.2f}"
                table.add_row(evaluator, metric_name, score_display, error_display)

        console.print(f"::{session_name}:{eval_name}")
        console.print(table)

        # Show error summary if there are errors
        if error_count > 0:
            console.print("\n[bold]Error Summary:[/bold]")
            console.print(
                f"Total errors: [red]{error_count}[/red] out of {total_items} items ({error_percentage:.1f}%)"
            )

            # Group errors by type
            error_types = {}
            for result in evaluation_results:
                if result.error:
                    # Extract error type from the error message
                    error_type = (
                        result.error.split(":")[0] if ":" in result.error else "Unknown"
                    )
                    error_types[error_type] = error_types.get(error_type, 0) + 1

            if error_types:
                console.print("\nError Types:")
                for error_type, count in sorted(
                    error_types.items(), key=lambda x: x[1], reverse=True
                ):
                    console.print(
                        f" • {error_type}: {count} occurrence{'s' if count > 1 else ''}"
                    )

        # Show detailed errors if --errors flag is used
        if errors and error_count > 0:
            console.print(f"\n[bold]Error Details ({error_count} errors):[/bold]\n")
            error_idx = 0
            for result in evaluation_results:
                if result.error:
                    error_idx += 1
                    console.print(
                        f"[bold][{error_idx}] Item ID: {result.item_id}[/bold]"
                    )
                    console.print(f"    Error: [red]{result.error}[/red]")

                    # Display dataset row (truncated if too long)
                    dataset_str = str(result.dataset_row)
                    if len(dataset_str) > 100:
                        dataset_str = dataset_str[:97] + "..."
                    console.print(f"    Dataset: {dataset_str}")

                    # Display timestamp
                    timestamp = datetime.fromtimestamp(result.timestamp).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                    console.print(f"    Time: {timestamp}\n")


@cli.command()
@click.argument("old_name")
@click.argument("new_name")
@click.option("--storage", default="json://.doteval", help="Storage backend path")
def rename(old_name: str, new_name: str, storage: str):
    """Rename a session."""
    manager = SessionManager(storage)
    old_session = manager.get_session(old_name)

    if not old_session:
        console.print(f"[red]Session '{old_name}' not found.[/red]")
        return

    old_session.name = new_name
    manager.storage.save(old_session)
    manager.storage.rename(old_name, new_name)

    console.print(f"[green]Session '{old_name}' renamed to '{new_name}'[/green]")


@cli.command()
@click.argument("session_name")
@click.option("--storage", default="json://.doteval", help="Storage backend path")
def delete(session_name, storage):
    """Delete a session."""
    manager = SessionManager(storage)

    try:
        manager.delete_session(session_name)
        console.print(f"[green]Deleted session '{session_name}'[/green]")
    except ValueError:
        console.print(
            f"[red]Session '{session_name}' not found. Run 'doteval list' to list the available sessions.[/red]"
        )


if __name__ == "__main__":
    cli()
