"""Main application entry point."""

import sys
import signal
import time
from pathlib import Path
import click
from config import get_settings
from utils.logger import setup_logger, get_logger
from database import get_db_manager
from scheduler import get_scheduler_service

# Setup logger
logger = None


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    logger.info(f"Received signal {signum}, shutting down...")
    shutdown()
    sys.exit(0)


def shutdown():
    """Shutdown the application gracefully."""
    if logger:
        logger.info("Shutting down application")
    
    # Stop scheduler
    try:
        scheduler_service = get_scheduler_service()
        scheduler_service.stop()
    except Exception as e:
        if logger:
            logger.error(f"Error stopping scheduler: {e}")


def initialize():
    """Initialize application components."""
    global logger
    
    # Load settings
    settings = get_settings()
    
    # Setup logger
    logger = setup_logger(
        name='market_monitor',
        log_file=settings.app.log_file,
        level=settings.app.log_level
    )
    
    logger.info("=" * 60)
    logger.info(f"Starting {settings.app.name}")
    logger.info("=" * 60)
    
    # Initialize database
    logger.info("Initializing database...")
    db_manager = get_db_manager()
    logger.info("Database initialized successfully")
    
    return settings


@click.group()
def cli():
    """Market Monitor & Productivity System CLI."""
    pass


@cli.command()
@click.option('--test', is_flag=True, help='Run a test notification immediately')
def daemon(test):
    """Run the application as a daemon (background service)."""
    settings = initialize()
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start scheduler
    logger.info("Starting scheduler service...")
    scheduler_service = get_scheduler_service()
    scheduler_service.start()
    
    # Print registered jobs
    jobs = scheduler_service.get_jobs()
    logger.info(f"Registered {len(jobs)} scheduled jobs:")
    for job in jobs:
        logger.info(f"  • {job.name} (next run: {job.next_run_time})")
    
    # Run test notification if requested
    if test:
        logger.info("Running test notification...")
        from scheduler.jobs import test_notification
        test_notification()
    
    logger.info("Application running. Press Ctrl+C to stop.")
    
    try:
        # Keep the application running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    finally:
        shutdown()


@cli.command()
def status():
    """Show the status of scheduled jobs."""
    settings = initialize()
    
    scheduler_service = get_scheduler_service()
    scheduler_service.start()
    
    jobs = scheduler_service.get_jobs()
    
    click.echo("\n📊 Scheduled Jobs Status\n" + "=" * 60)
    
    if not jobs:
        click.echo("No jobs scheduled.")
    else:
        for job in jobs:
            click.echo(f"\n🔹 {job.name}")
            click.echo(f"   ID: {job.id}")
            click.echo(f"   Next Run: {job.next_run_time}")
            click.echo(f"   Trigger: {job.trigger}")
    
    click.echo("\n" + "=" * 60 + "\n")
    
    scheduler_service.stop()


@cli.command()
@click.argument('job_id')
def run_job(job_id):
    """Run a specific job immediately."""
    settings = initialize()
    
    scheduler_service = get_scheduler_service()
    scheduler_service.start()
    
    click.echo(f"Running job: {job_id}")
    success = scheduler_service.run_job_now(job_id)
    
    if success:
        click.echo(f"✓ Job {job_id} triggered successfully")
        time.sleep(2)  # Wait for job to complete
    else:
        click.echo(f"✗ Failed to trigger job {job_id}")
    
    scheduler_service.stop()


@cli.command()
def market_summary():
    """Generate and display market summary."""
    initialize()
    
    from market_monitor import SummaryGenerator
    
    generator = SummaryGenerator()
    settings = get_settings()
    
    summary = generator.generate_daily_summary(
        indices=settings.market.indices,
        include_sectors=True
    )
    
    click.echo(summary)


@cli.command()
def task_summary():
    """Display task summary."""
    initialize()
    
    from todos import TaskManager
    
    manager = TaskManager()
    summary = manager.generate_daily_summary()
    
    click.echo(summary)


@cli.command()
def setup():
    """Setup the application (create directories, initialize database)."""
    click.echo("🔧 Setting up Market Monitor & Productivity System...\n")
    
    # Create necessary directories
    dirs = ['data', 'logs']
    for dir_name in dirs:
        path = Path(dir_name)
        if not path.exists():
            path.mkdir(parents=True)
            click.echo(f"✓ Created directory: {dir_name}")
        else:
            click.echo(f"  Directory already exists: {dir_name}")
    
    # Initialize database
    click.echo("\n📊 Initializing database...")
    settings = initialize()
    click.echo("✓ Database initialized successfully")
    
    click.echo("\n✅ Setup complete!")
    click.echo("\nNext steps:")
    click.echo("  1. Configure notifications in config/config.yaml")
    click.echo("  2. Run 'python main.py daemon --test' to test the system")
    click.echo("  3. Run 'python main.py daemon' to start the service")


if __name__ == '__main__':
    cli()
