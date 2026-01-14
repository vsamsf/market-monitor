"""CLI interface for reminder management."""

import click
from datetime import datetime
from tabulate import tabulate
from colorama import Fore, Style, init
from reminders import ReminderManager
from utils.logger import setup_logger
from config import get_settings

# Initialize colorama
init(autoreset=True)

# Setup
settings = get_settings()
logger = setup_logger('reminders_cli', settings.app.log_file, settings.app.log_level)
manager = ReminderManager()


@click.group()
def cli():
    """Reminder Management CLI."""
    pass


@cli.command()
@click.option('--title', '-t', required=True, help='Reminder title')
@click.option('--datetime', '-d', 'datetime_str', required=True, help='Reminder datetime (e.g., "2024-01-15 14:30" or "tomorrow 3pm")')
@click.option('--description', '-desc', default='', help='Reminder description')
@click.option('--recurring', '-r', type=click.Choice(['daily', 'weekly', 'monthly']), help='Recurring type')
def add(title, datetime_str, description, recurring):
    """Add a new reminder."""
    try:
        reminder = manager.create_reminder(title, datetime_str, description, recurring)
        click.echo(f"{Fore.GREEN}✓ Reminder created successfully!")
        click.echo(f"{Fore.CYAN}ID: {reminder.id}")
        click.echo(f"Title: {reminder.title}")
        click.echo(f"DateTime: {reminder.datetime}")
        if recurring:
            click.echo(f"Recurring: {recurring}")
    except Exception as e:
        click.echo(f"{Fore.RED}✗ Error creating reminder: {e}")


@cli.command()
@click.option('--all', '-a', 'show_all', is_flag=True, help='Show all reminders including inactive')
def list(show_all):
    """List all reminders."""
    reminders = manager.get_all_reminders(active_only=not show_all)
    
    if not reminders:
        click.echo(f"{Fore.YELLOW}No reminders found.")
        return
    
    # Prepare table data
    table_data = []
    for reminder in reminders:
        status = "✓" if reminder.is_active else "✗"
        recurring = reminder.recurring_type or "-"
        
        table_data.append([
            reminder.id,
            status,
            reminder.title,
            reminder.datetime.strftime('%Y-%m-%d %H:%M'),
            recurring,
            reminder.description[:30] + "..." if len(reminder.description) > 30 else reminder.description
        ])
    
    # Print table
    headers = ["ID", "Active", "Title", "DateTime", "Recurring", "Description"]
    click.echo("\n" + tabulate(table_data, headers=headers, tablefmt="grid"))
    click.echo(f"\n{Fore.CYAN}Total: {len(reminders)} reminder(s)")


@cli.command()
@click.argument('reminder_id', type=int)
def show(reminder_id):
    """Show detailed information about a reminder."""
    reminder = manager.get_reminder(reminder_id)
    
    if not reminder:
        click.echo(f"{Fore.RED}✗ Reminder {reminder_id} not found.")
        return
    
    click.echo(f"\n{Fore.CYAN}{'=' * 60}")
    click.echo(f"Reminder ID: {reminder.id}")
    click.echo(f"{'=' * 60}")
    click.echo(f"Title: {reminder.title}")
    click.echo(f"DateTime: {reminder.datetime}")
    click.echo(f"Description: {reminder.description or '(none)'}")
    click.echo(f"Recurring: {reminder.recurring_type or 'No'}")
    click.echo(f"Active: {'Yes' if reminder.is_active else 'No'}")
    click.echo(f"Created: {reminder.created_at}")
    if reminder.last_notified:
        click.echo(f"Last Notified: {reminder.last_notified}")
    click.echo(f"{'=' * 60}\n")


@cli.command()
@click.argument('reminder_id', type=int)
@click.option('--title', '-t', help='New title')
@click.option('--datetime', '-d', 'datetime_str', help='New datetime')
@click.option('--description', '-desc', help='New description')
@click.option('--recurring', '-r', type=click.Choice(['daily', 'weekly', 'monthly', 'none']), help='Recurring type')
def update(reminder_id, title, datetime_str, description, recurring):
    """Update a reminder."""
    if recurring == 'none':
        recurring = None
    
    try:
        updated = manager.update_reminder(reminder_id, title, datetime_str, description, recurring)
        
        if updated:
            click.echo(f"{Fore.GREEN}✓ Reminder {reminder_id} updated successfully!")
        else:
            click.echo(f"{Fore.RED}✗ Reminder {reminder_id} not found.")
    except Exception as e:
        click.echo(f"{Fore.RED}✗ Error updating reminder: {e}")


@cli.command()
@click.argument('reminder_id', type=int)
@click.confirmation_option(prompt='Are you sure you want to delete this reminder?')
def delete(reminder_id):
    """Delete a reminder."""
    success = manager.delete_reminder(reminder_id)
    
    if success:
        click.echo(f"{Fore.GREEN}✓ Reminder {reminder_id} deleted successfully!")
    else:
        click.echo(f"{Fore.RED}✗ Reminder {reminder_id} not found.")


@cli.command()
@click.argument('reminder_id', type=int)
def deactivate(reminder_id):
    """Deactivate a reminder (soft delete)."""
    success = manager.deactivate_reminder(reminder_id)
    
    if success:
        click.echo(f"{Fore.GREEN}✓ Reminder {reminder_id} deactivated!")
    else:
        click.echo(f"{Fore.RED}✗ Reminder {reminder_id} not found.")


@cli.command()
def due():
    """Show reminders that are due now."""
    from utils.helpers import get_ist_now
    
    due_reminders = manager.get_due_reminders(advance_minutes=5)
    
    if not due_reminders:
        click.echo(f"{Fore.GREEN}No reminders due right now.")
        return
    
    click.echo(f"{Fore.YELLOW}⏰ Due Reminders:\n")
    
    for reminder in due_reminders:
        click.echo(f"{Fore.RED}🔔 {reminder.title}")
        click.echo(f"   Due: {reminder.datetime.strftime('%Y-%m-%d %H:%M')}")
        if reminder.description:
            click.echo(f"   {reminder.description}")
        click.echo()


if __name__ == '__main__':
    cli()
