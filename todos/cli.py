"""CLI interface for task/to-do management."""

import click
from datetime import datetime
from tabulate import tabulate
from colorama import Fore, Style, init
from todos import TaskManager
from utils.logger import setup_logger
from config import get_settings

# Initialize colorama
init(autoreset=True)

# Setup
settings = get_settings()
logger = setup_logger('tasks_cli', settings.app.log_file, settings.app.log_level)
manager = TaskManager()


@click.group()
def cli():
    """Task/To-Do Management CLI."""
    pass


@cli.command()
@click.option('--title', '-t', required=True, help='Task title')
@click.option('--description', '-desc', default='', help='Task description')
@click.option('--due', '-d', help='Due date (e.g., "2024-01-15" or "tomorrow")')
@click.option('--priority', '-p', type=click.Choice(['low', 'medium', 'high']), default='medium', help='Priority level')
def add(title, description, due, priority):
    """Add a new task."""
    try:
        task = manager.create_task(title, description, due, priority)
        click.echo(f"{Fore.GREEN}✓ Task created successfully!")
        click.echo(f"{Fore.CYAN}ID: {task.id}")
        click.echo(f"Title: {task.title}")
        click.echo(f"Priority: {task.priority}")
        if due:
            click.echo(f"Due: {task.due_date}")
    except Exception as e:
        click.echo(f"{Fore.RED}✗ Error creating task: {e}")


@cli.command()
@click.option('--all', '-a', 'show_all', is_flag=True, help='Show all tasks including completed')
@click.option('--priority', '-p', type=click.Choice(['low', 'medium', 'high']), help='Filter by priority')
def list(show_all, priority):
    """List all tasks."""
    if priority:
        tasks = manager.get_tasks_by_priority(priority)
    else:
        tasks = manager.get_all_tasks(include_completed=show_all)
    
    if not tasks:
        click.echo(f"{Fore.YELLOW}No tasks found.")
        return
    
    # Prepare table data
    table_data = []
    for task in tasks:
        # Status icon
        status = "✓" if task.is_completed else "○"
        
        # Priority color
        priority_colors = {
            'high': Fore.RED,
            'medium': Fore.YELLOW,
            'low': Fore.BLUE
        }
        priority_icon = {
            'high': '🔴',
            'medium': '🟡',
            'low': '🔵'
        }
        
        # Due date formatting
        due = task.due_date.strftime('%Y-%m-%d') if task.due_date else '-'
        
        # Check if overdue
        if task.due_date and not task.is_completed:
            from utils.helpers import get_ist_now
            if task.due_date < get_ist_now():
                due = f"{Fore.RED}{due} (OVERDUE){Style.RESET_ALL}"
        
        table_data.append([
            task.id,
            status,
            priority_icon[task.priority],
            task.title,
            due,
            task.description[:40] + "..." if len(task.description) > 40 else task.description
        ])
    
    # Print table
    headers = ["ID", "✓", "P", "Title", "Due Date", "Description"]
    click.echo("\n" + tabulate(table_data, headers=headers, tablefmt="grid"))
    click.echo(f"\n{Fore.CYAN}Total: {len(tasks)} task(s)")


@cli.command()
def today():
    """Show tasks due today."""
    tasks = manager.get_today_tasks()
    
    if not tasks:
        click.echo(f"{Fore.GREEN}No tasks due today! 🎉")
        return
    
    click.echo(f"{Fore.CYAN}📅 Tasks Due Today:\n")
    
    for task in tasks:
        priority_icon = {'high': '🔴', 'medium': '🟡', 'low': '🔵'}
        click.echo(f"{priority_icon[task.priority]} {task.title}")
        if task.description:
            click.echo(f"   {task.description}")
        click.echo()


@cli.command()
def overdue():
    """Show overdue tasks."""
    tasks = manager.get_overdue_tasks()
    
    if not tasks:
        click.echo(f"{Fore.GREEN}No overdue tasks! 🎉")
        return
    
    click.echo(f"{Fore.RED}⚠️  Overdue Tasks:\n")
    
    for task in tasks:
        priority_icon = {'high': '🔴', 'medium': '🟡', 'low': '🔵'}
        click.echo(f"{priority_icon[task.priority]} {task.title}")
        click.echo(f"   Due: {task.due_date.strftime('%Y-%m-%d')}")
        if task.description:
            click.echo(f"   {task.description}")
        click.echo()


@cli.command()
@click.argument('task_id', type=int)
def show(task_id):
    """Show detailed information about a task."""
    task = manager.get_task(task_id)
    
    if not task:
        click.echo(f"{Fore.RED}✗ Task {task_id} not found.")
        return
    
    click.echo(f"\n{Fore.CYAN}{'=' * 60}")
    click.echo(f"Task ID: {task.id}")
    click.echo(f"{'=' * 60}")
    click.echo(f"Title: {task.title}")
    click.echo(f"Description: {task.description or '(none)'}")
    click.echo(f"Priority: {task.priority}")
    click.echo(f"Due Date: {task.due_date.strftime('%Y-%m-%d %H:%M') if task.due_date else 'Not set'}")
    click.echo(f"Status: {'Completed' if task.is_completed else 'Pending'}")
    click.echo(f"Created: {task.created_at.strftime('%Y-%m-%d %H:%M')}")
    if task.completed_at:
        click.echo(f"Completed: {task.completed_at.strftime('%Y-%m-%d %H:%M')}")
    click.echo(f"{'=' * 60}\n")


@cli.command()
@click.argument('task_id', type=int)
@click.option('--title', '-t', help='New title')
@click.option('--description', '-desc', help='New description')
@click.option('--due', '-d', help='New due date')
@click.option('--priority', '-p', type=click.Choice(['low', 'medium', 'high']), help='New priority')
def update(task_id, title, description, due, priority):
    """Update a task."""
    try:
        updated = manager.update_task(task_id, title, description, due, priority)
        
        if updated:
            click.echo(f"{Fore.GREEN}✓ Task {task_id} updated successfully!")
        else:
            click.echo(f"{Fore.RED}✗ Task {task_id} not found.")
    except Exception as e:
        click.echo(f"{Fore.RED}✗ Error updating task: {e}")


@cli.command()
@click.argument('task_id', type=int)
def complete(task_id):
    """Mark a task as completed."""
    success = manager.complete_task(task_id)
    
    if success:
        click.echo(f"{Fore.GREEN}✓ Task {task_id} marked as completed! 🎉")
    else:
        click.echo(f"{Fore.RED}✗ Task {task_id} not found.")


@cli.command()
@click.argument('task_id', type=int)
def uncomplete(task_id):
    """Mark a task as not completed."""
    success = manager.uncomplete_task(task_id)
    
    if success:
        click.echo(f"{Fore.YELLOW}Task {task_id} marked as incomplete.")
    else:
        click.echo(f"{Fore.RED}✗ Task {task_id} not found.")


@cli.command()
@click.argument('task_id', type=int)
@click.confirmation_option(prompt='Are you sure you want to delete this task?')
def delete(task_id):
    """Delete a task."""
    success = manager.delete_task(task_id)
    
    if success:
        click.echo(f"{Fore.GREEN}✓ Task {task_id} deleted successfully!")
    else:
        click.echo(f"{Fore.RED}✗ Task {task_id} not found.")


@cli.command()
def summary():
    """Display task summary."""
    summary = manager.generate_daily_summary()
    click.echo(summary)


if __name__ == '__main__':
    cli()
