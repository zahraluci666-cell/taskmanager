"""
Task Manager CLI — the "phase 1" of the project.

Usage examples:
    python -m app.cli.main add "Write report" --priority high --due 2026-08-01
    python -m app.cli.main list --status todo
    python -m app.cli.main done 3
    python -m app.cli.main delete 3
"""
import datetime as dt
import click

from app.core.database import SessionLocal, init_db
from app.core.service import TaskService, TaskNotFoundError
from app.core.models import TaskStatus, TaskPriority


def get_service() -> TaskService:
    init_db()
    db = SessionLocal()
    return TaskService(db)


@click.group()
def cli():
    """Simple task manager — command line interface."""
    pass


@cli.command()
@click.argument("title")
@click.option("--description", "-d", default="", help="Task description")
@click.option(
    "--priority", "-p",
    type=click.Choice([p.value for p in TaskPriority]),
    default="medium",
)
@click.option("--due", help="Due date, format YYYY-MM-DD")
def add(title, description, priority, due):
    """Add a new task."""
    service = get_service()
    due_date = dt.datetime.strptime(due, "%Y-%m-%d") if due else None
    task = service.create_task(
        title=title,
        description=description,
        priority=TaskPriority(priority),
        due_date=due_date,
    )
    click.echo(f"✔ Created task #{task.id}: {task.title}")


@cli.command(name="list")
@click.option("--status", type=click.Choice([s.value for s in TaskStatus]), default=None)
@click.option("--priority", type=click.Choice([p.value for p in TaskPriority]), default=None)
def list_tasks(status, priority):
    """List tasks, optionally filtered by status/priority."""
    service = get_service()
    tasks = service.list_tasks(
        status=TaskStatus(status) if status else None,
        priority=TaskPriority(priority) if priority else None,
    )
    if not tasks:
        click.echo("No tasks found.")
        return
    for t in tasks:
        due = t.due_date.strftime("%Y-%m-%d") if t.due_date else "-"
        click.echo(f"#{t.id:<4} [{t.status.value:<11}] {t.priority.value:<6} due:{due:<10} {t.title}")


@cli.command()
@click.argument("task_id", type=int)
def done(task_id):
    """Mark a task as done."""
    service = get_service()
    try:
        task = service.mark_done(task_id)
        click.echo(f"✔ Task #{task.id} marked as done")
    except TaskNotFoundError as e:
        click.echo(f"✘ {e}", err=True)


@cli.command()
@click.argument("task_id", type=int)
@click.option("--title")
@click.option("--description")
@click.option("--priority", type=click.Choice([p.value for p in TaskPriority]))
@click.option("--status", type=click.Choice([s.value for s in TaskStatus]))
def update(task_id, title, description, priority, status):
    """Update fields on an existing task."""
    service = get_service()
    try:
        task = service.update_task(
            task_id,
            title=title,
            description=description,
            priority=TaskPriority(priority) if priority else None,
            status=TaskStatus(status) if status else None,
        )
        click.echo(f"✔ Task #{task.id} updated")
    except TaskNotFoundError as e:
        click.echo(f"✘ {e}", err=True)


@cli.command()
@click.argument("task_id", type=int)
def delete(task_id):
    """Delete a task."""
    service = get_service()
    try:
        service.delete_task(task_id)
        click.echo(f"✔ Task #{task_id} deleted")
    except TaskNotFoundError as e:
        click.echo(f"✘ {e}", err=True)


if __name__ == "__main__":
    cli()
