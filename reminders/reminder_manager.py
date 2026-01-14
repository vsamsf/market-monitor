"""Reminder manager for CRUD operations."""

from typing import List, Optional
from datetime import datetime, timedelta
from database.models import Reminder
from database.db_manager import get_db_manager
from utils.logger import get_logger
from utils.helpers import get_ist_now

logger = get_logger(__name__)


class ReminderManager:
    """Manager for reminder operations."""
    
    def __init__(self):
        """Initialize reminder manager."""
        self.db = get_db_manager()
    
    def create_reminder(
        self,
        title: str,
        datetime_str: str,
        description: str = "",
        recurring_type: Optional[str] = None
    ) -> Reminder:
        """
        Create a new reminder.
        
        Args:
            title: Reminder title
            datetime_str: Reminder datetime (ISO format or readable)
            description: Optional description
            recurring_type: Optional recurring type (daily, weekly, monthly)
        
        Returns:
            Created Reminder object
        """
        try:
            # Parse datetime
            reminder_dt = self._parse_datetime(datetime_str)
            
            reminder = Reminder(
                title=title,
                description=description,
                datetime=reminder_dt,
                recurring_type=recurring_type,
                is_active=True
            )
            
            with self.db.get_session() as session:
                session.add(reminder)
                session.flush()
                session.refresh(reminder)
                logger.info(f"Created reminder: {title} at {reminder_dt}")
                return reminder
                
        except Exception as e:
            logger.error(f"Error creating reminder: {e}")
            raise
    
    def get_all_reminders(self, active_only: bool = True) -> List[Reminder]:
        """
        Get all reminders.
        
        Args:
            active_only: Whether to return only active reminders
        
        Returns:
            List of Reminder objects
        """
        with self.db.get_session() as session:
            query = session.query(Reminder)
            if active_only:
                query = query.filter(Reminder.is_active == True)
            reminders = query.order_by(Reminder.datetime).all()
            # Expunge all to avoid detached instance errors
            for reminder in reminders:
                session.expunge(reminder)
            return reminders
    
    def get_reminder(self, reminder_id: int) -> Optional[Reminder]:
        """
        Get a specific reminder by ID.
        
        Args:
            reminder_id: Reminder ID
        
        Returns:
            Reminder object or None
        """
        return self.db.get_by_id(Reminder, reminder_id)
    
    def update_reminder(
        self,
        reminder_id: int,
        title: Optional[str] = None,
        datetime_str: Optional[str] = None,
        description: Optional[str] = None,
        recurring_type: Optional[str] = None
    ) -> Optional[Reminder]:
        """
        Update a reminder.
        
        Args:
            reminder_id: Reminder ID
            title: New title
            datetime_str: New datetime
            description: New description
            recurring_type: New recurring type
        
        Returns:
            Updated Reminder or None
        """
        with self.db.get_session() as session:
            reminder = session.query(Reminder).filter(Reminder.id == reminder_id).first()
            if not reminder:
                logger.warning(f"Reminder {reminder_id} not found")
                return None
            
            if title:
                reminder.title = title
            if datetime_str:
                reminder.datetime = self._parse_datetime(datetime_str)
            if description is not None:
                reminder.description = description
            if recurring_type is not None:
                reminder.recurring_type = recurring_type
            
            session.flush()
            logger.info(f"Updated reminder {reminder_id}")
            return reminder
    
    def delete_reminder(self, reminder_id: int) -> bool:
        """
        Delete a reminder.
        
        Args:
            reminder_id: Reminder ID
        
        Returns:
            True if deleted, False if not found
        """
        with self.db.get_session() as session:
            reminder = session.query(Reminder).filter(Reminder.id == reminder_id).first()
            if not reminder:
                logger.warning(f"Reminder {reminder_id} not found")
                return False
            
            session.delete(reminder)
            session.flush()
            logger.info(f"Deleted reminder {reminder_id}")
            return True
    
    def deactivate_reminder(self, reminder_id: int) -> bool:
        """
        Deactivate a reminder (soft delete).
        
        Args:
            reminder_id: Reminder ID
        
        Returns:
            True if deactivated, False if not found
        """
        with self.db.get_session() as session:
            reminder = session.query(Reminder).filter(Reminder.id == reminder_id).first()
            if not reminder:
                return False
            
            reminder.is_active = False
            session.flush()
            logger.info(f"Deactivated reminder {reminder_id}")
            return True
    
    def get_due_reminders(self, advance_minutes: int = 0) -> List[Reminder]:
        """
        Get reminders that are due (or due within advance_minutes).
        
        Args:
            advance_minutes: Minutes ahead to check
        
        Returns:
            List of due Reminder objects
        """
        now = get_ist_now()
        check_until = now + timedelta(minutes=advance_minutes)
        
        with self.db.get_session() as session:
            reminders = session.query(Reminder).filter(
                Reminder.is_active == True,
                Reminder.datetime <= check_until,
                Reminder.datetime >= now - timedelta(minutes=1)  # Not already notified
            ).all()
            
            # Filter out recently notified reminders
            due_reminders = []
            for reminder in reminders:
                if reminder.last_notified is None or \
                   (now - reminder.last_notified) > timedelta(hours=1):
                    due_reminders.append(reminder)
            
            return due_reminders
    
    def mark_notified(self, reminder_id: int):
        """
        Mark a reminder as notified.
        
        Args:
            reminder_id: Reminder ID
        """
        with self.db.get_session() as session:
            reminder = session.query(Reminder).filter(Reminder.id == reminder_id).first()
            if reminder:
                reminder.last_notified = get_ist_now()
                
                # Handle recurring reminders
                if reminder.recurring_type:
                    next_dt = self._calculate_next_occurrence(
                        reminder.datetime,
                        reminder.recurring_type
                    )
                    reminder.datetime = next_dt
                    logger.info(f"Rescheduled recurring reminder to {next_dt}")
                else:
                    # Deactivate one-time reminder
                    reminder.is_active = False
                    logger.info(f"Deactivated one-time reminder {reminder_id}")
                
                session.flush()
    
    def _parse_datetime(self, datetime_str: str) -> datetime:
        """Parse datetime string to datetime object."""
        from dateutil import parser
        try:
            return parser.parse(datetime_str)
        except Exception as e:
            logger.error(f"Error parsing datetime '{datetime_str}': {e}")
            raise ValueError(f"Invalid datetime format: {datetime_str}")
    
    def _calculate_next_occurrence(self, current_dt: datetime, recurring_type: str) -> datetime:
        """Calculate next occurrence for recurring reminder."""
        if recurring_type == 'daily':
            return current_dt + timedelta(days=1)
        elif recurring_type == 'weekly':
            return current_dt + timedelta(weeks=1)
        elif recurring_type == 'monthly':
            # Add one month (approximate)
            return current_dt + timedelta(days=30)
        else:
            return current_dt
