"""Scheduled job definitions."""

from config import get_settings
from utils.logger import get_logger
from utils.helpers import get_ist_now
from market_monitor import SummaryGenerator
from reminders import ReminderManager
from todos import TaskManager
from notifications import NotificationManager
from database import get_db_manager

logger = get_logger(__name__)

# Global instances
settings = get_settings()
notification_manager = NotificationManager.from_settings(settings)
summary_generator = SummaryGenerator()
reminder_manager = ReminderManager()
task_manager = TaskManager()


def daily_market_summary():
    """
    Generate and send daily market summary.
    Runs at 7:00 AM IST.
    """
    try:
        logger.info("Starting daily market summary job")
        
        # Generate market summary
        market_summary = summary_generator.generate_daily_summary(
            indices=settings.market.indices,
            include_sectors=True
        )
        
        # Generate task summary
        task_summary = task_manager.generate_daily_summary()
        
        # Combine summaries
        full_summary = f"{market_summary}\n{task_summary}"
        
        # Send notification
        notification_manager.send_notification(
            title="📊 Daily Market & Task Summary",
            message=full_summary,
            priority="normal"
        )
        
        logger.info("Daily market summary job completed successfully")
        
    except Exception as e:
        logger.error(f"Error in daily market summary job: {e}")


def live_market_monitor():
    """
    Monitor market indices during market hours.
    Runs every 30 minutes from 9:15 AM to 3:30 PM IST.
    """
    try:
        logger.info("Starting live market monitor job")
        
        # Generate live update
        update = summary_generator.generate_live_update(
            indices=settings.market.indices
        )
        
        # Send notification (desktop only for frequent updates)
        notification_manager.send_notification(
            title="📈 Market Update",
            message=update,
            priority="low",
            channels=['desktop']
        )
        
        logger.info("Live market monitor job completed")
        
    except Exception as e:
        logger.error(f"Error in live market monitor job: {e}")


def check_reminders():
    """
    Check for due reminders and send notifications.
    Runs every minute.
    """
    try:
        advance_minutes = settings.reminders.advance_notification_minutes
        due_reminders = reminder_manager.get_due_reminders(advance_minutes)
        
        for reminder in due_reminders:
            logger.info(f"Processing due reminder: {reminder.title}")
            
            # Format message
            message = f"Reminder: {reminder.title}"
            if reminder.description:
                message += f"\n\n{reminder.description}"
            
            if reminder.recurring_type:
                message += f"\n\n🔁 Recurring: {reminder.recurring_type}"
            
            # Send notification
            notification_manager.send_notification(
                title="⏰ Reminder",
                message=message,
                priority="high"
            )
            
            # Mark as notified
            reminder_manager.mark_notified(reminder.id)
        
        if due_reminders:
            logger.info(f"Processed {len(due_reminders)} due reminders")
            
    except Exception as e:
        logger.error(f"Error checking reminders: {e}")


def cleanup_old_data():
    """
    Clean up old data from database.
    Runs daily at midnight.
    """
    try:
        logger.info("Starting cleanup job")
        
        # Archive old completed tasks
        archived_count = task_manager.archive_old_tasks(
            days=settings.tasks.auto_archive_completed_days
        )
        
        logger.info(f"Cleanup completed: archived {archived_count} old tasks")
        
    except Exception as e:
        logger.error(f"Error in cleanup job: {e}")


def test_notification():
    """Test notification - for testing purposes."""
    try:
        notification_manager.send_notification(
            title="Test Notification",
            message="This is a test notification from the Market Monitor system.",
            priority="normal"
        )
        logger.info("Test notification sent")
    except Exception as e:
        logger.error(f"Error sending test notification: {e}")
