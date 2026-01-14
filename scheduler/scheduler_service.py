"""Scheduler service using APScheduler."""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
import pytz
from config import get_settings
from utils.logger import get_logger
from scheduler import jobs

logger = get_logger(__name__)


class SchedulerService:
    """Scheduler service to manage all scheduled jobs."""
    
    def __init__(self):
        """Initialize scheduler service."""
        self.settings = get_settings()
        self.scheduler = None
        self.timezone = pytz.timezone(self.settings.scheduler.timezone)
    
    def start(self):
        """Start the scheduler and register all jobs."""
        if self.scheduler is not None:
            logger.warning("Scheduler already running")
            return
        
        logger.info("Initializing scheduler service")
        
        # Create scheduler
        self.scheduler = BackgroundScheduler(
            timezone=self.timezone,
            job_defaults={
                'coalesce': self.settings.scheduler.job_defaults.coalesce,
                'max_instances': self.settings.scheduler.job_defaults.max_instances,
                'misfire_grace_time': self.settings.scheduler.job_defaults.misfire_grace_time
            }
        )
        
        # Register jobs
        self._register_jobs()
        
        # Start scheduler
        self.scheduler.start()
        logger.info("Scheduler service started successfully")
    
    def _register_jobs(self):
        """Register all scheduled jobs."""
        
        # Daily market summary at 7:00 AM IST
        summary_time = self.settings.market.summary_time.split(':')
        self.scheduler.add_job(
            jobs.daily_market_summary,
            trigger=CronTrigger(
                hour=int(summary_time[0]),
                minute=int(summary_time[1]),
                timezone=self.timezone
            ),
            id='daily_market_summary',
            name='Daily Market Summary',
            replace_existing=True
        )
        logger.info(f"Registered job: Daily Market Summary at {self.settings.market.summary_time}")
        
        # Live market monitoring during market hours
        # Every 30 minutes from 9:15 AM to 3:30 PM IST on weekdays
        market_open = self.settings.market.market_open.split(':')
        market_close = self.settings.market.market_close.split(':')
        
        self.scheduler.add_job(
            jobs.live_market_monitor,
            trigger=CronTrigger(
                day_of_week='mon-fri',
                hour=f'{market_open[0]}-{market_close[0]}',
                minute=f'*/{self.settings.market.monitor_interval_minutes}',
                timezone=self.timezone
            ),
            id='live_market_monitor',
            name='Live Market Monitor',
            replace_existing=True
        )
        logger.info(
            f"Registered job: Live Market Monitor "
            f"(every {self.settings.market.monitor_interval_minutes} min during market hours)"
        )
        
        # Check reminders every minute
        self.scheduler.add_job(
            jobs.check_reminders,
            trigger=IntervalTrigger(
                seconds=self.settings.reminders.check_interval_seconds,
                timezone=self.timezone
            ),
            id='check_reminders',
            name='Check Reminders',
            replace_existing=True
        )
        logger.info("Registered job: Check Reminders (every minute)")
        
        # Cleanup old data daily at midnight
        self.scheduler.add_job(
            jobs.cleanup_old_data,
            trigger=CronTrigger(
                hour=0,
                minute=0,
                timezone=self.timezone
            ),
            id='cleanup_old_data',
            name='Cleanup Old Data',
            replace_existing=True
        )
        logger.info("Registered job: Cleanup Old Data (daily at midnight)")
    
    def stop(self):
        """Stop the scheduler."""
        if self.scheduler is None:
            return
        
        logger.info("Stopping scheduler service")
        self.scheduler.shutdown(wait=True)
        self.scheduler = None
        logger.info("Scheduler service stopped")
    
    def get_jobs(self):
        """Get list of scheduled jobs."""
        if self.scheduler is None:
            return []
        
        return self.scheduler.get_jobs()
    
    def run_job_now(self, job_id: str):
        """
        Run a specific job immediately.
        
        Args:
            job_id: Job ID to run
        """
        if self.scheduler is None:
            logger.error("Scheduler not running")
            return False
        
        try:
            job = self.scheduler.get_job(job_id)
            if job:
                job.modify(next_run_time=None)
                logger.info(f"Triggered job: {job_id}")
                return True
            else:
                logger.error(f"Job not found: {job_id}")
                return False
        except Exception as e:
            logger.error(f"Error running job {job_id}: {e}")
            return False


# Global scheduler service instance
_scheduler_service = None


def get_scheduler_service() -> SchedulerService:
    """Get or create scheduler service instance."""
    global _scheduler_service
    if _scheduler_service is None:
        _scheduler_service = SchedulerService()
    return _scheduler_service
