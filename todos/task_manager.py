"""Task manager for CRUD operations."""

from typing import List, Optional
from datetime import datetime, timedelta
from database.models import Task
from database.db_manager import get_db_manager
from utils.logger import get_logger
from utils.helpers import get_ist_now

logger = get_logger(__name__)


class TaskManager:
    """Manager for task/to-do operations."""
    
    def __init__(self):
        """Initialize task manager."""
        self.db = get_db_manager()
    
    def create_task(
        self,
        title: str,
        description: str = "",
        due_date: Optional[str] = None,
        priority: str = "medium"
    ) -> Task:
        """
        Create a new task.
        
        Args:
            title: Task title
            description: Task description
            due_date: Due date (ISO format or readable)
            priority: Priority level (low, medium, high)
        
        Returns:
            Created Task object
        """
        try:
            # Parse due date if provided
            due_dt = None
            if due_date:
                from dateutil import parser
                due_dt = parser.parse(due_date)
            
            task = Task(
                title=title,
                description=description,
                due_date=due_dt,
                priority=priority,
                is_completed=False
            )
            
            with self.db.get_session() as session:
                session.add(task)
                session.flush()
                session.refresh(task)
                session.expunge(task)  # Expunge to avoid detached instance errors
                
            logger.info(f"Created task: {task.title} (priority: {task.priority})")
            return task
                
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            raise
    
    def get_all_tasks(self, include_completed: bool = False) -> List[Task]:
        """
        Get all tasks.
        
        Args:
            include_completed: Whether to include completed tasks
        
        Returns:
            List of Task objects
        """
        with self.db.get_session() as session:
            query = session.query(Task)
            if not include_completed:
                query = query.filter(Task.is_completed == False)
            tasks = query.order_by(Task.due_date.asc().nullslast(), Task.priority.desc()).all()
            # Expunge all to avoid detached instance errors
            for task in tasks:
                session.expunge(task)
            return tasks
    
    def get_task(self, task_id: int) -> Optional[Task]:
        """
        Get a specific task by ID.
        
        Args:
            task_id: Task ID
        
        Returns:
            Task object or None
        """
        return self.db.get_by_id(Task, task_id)
    
    def get_tasks_by_priority(self, priority: str) -> List[Task]:
        """
        Get tasks filtered by priority.
        
        Args:
            priority: Priority level
        
        Returns:
            List of Task objects
        """
        with self.db.get_session() as session:
            return session.query(Task).filter(
                Task.priority == priority,
                Task.is_completed == False
            ).all()
    
    def get_today_tasks(self) -> List[Task]:
        """
        Get tasks due today.
        
        Returns:
            List of Task objects
        """
        now = get_ist_now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        with self.db.get_session() as session:
            return session.query(Task).filter(
                Task.due_date >= today_start,
                Task.due_date <= today_end,
                Task.is_completed == False
            ).all()
    
    def get_overdue_tasks(self) -> List[Task]:
        """
        Get overdue tasks.
        
        Returns:
            List of Task objects
        """
        now = get_ist_now()
        
        with self.db.get_session() as session:
            return session.query(Task).filter(
                Task.due_date < now,
                Task.is_completed == False
            ).all()
    
    def update_task(
        self,
        task_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        due_date: Optional[str] = None,
        priority: Optional[str] = None
    ) -> Optional[Task]:
        """
        Update a task.
        
        Args:
            task_id: Task ID
            title: New title
            description: New description
            due_date: New due date
            priority: New priority
        
        Returns:
            Updated Task or None
        """
        with self.db.get_session() as session:
            task = session.query(Task).filter(Task.id == task_id).first()
            if not task:
                logger.warning(f"Task {task_id} not found")
                return None
            
            if title:
                task.title = title
            if description is not None:
                task.description = description
            if due_date:
                from dateutil import parser
                task.due_date = parser.parse(due_date)
            if priority:
                task.priority = priority
            
            session.flush()
            logger.info(f"Updated task {task_id}")
            return task
    
    def complete_task(self, task_id: int) -> bool:
        """
        Mark a task as completed.
        
        Args:
            task_id: Task ID
        
        Returns:
            True if completed, False if not found
        """
        with self.db.get_session() as session:
            task = session.query(Task).filter(Task.id == task_id).first()
            if not task:
                return False
            
            task.is_completed = True
            task.completed_at = get_ist_now()
            session.flush()
            logger.info(f"Completed task {task_id}: {task.title}")
            return True
    
    def uncomplete_task(self, task_id: int) -> bool:
        """
        Mark a task as not completed.
        
        Args:
            task_id: Task ID
        
        Returns:
            True if uncompleted, False if not found
        """
        with self.db.get_session() as session:
            task = session.query(Task).filter(Task.id == task_id).first()
            if not task:
                return False
            
            task.is_completed = False
            task.completed_at = None
            session.flush()
            logger.info(f"Uncompleted task {task_id}")
            return True
    
    def delete_task(self, task_id: int) -> bool:
        """
        Delete a task.
        
        Args:
            task_id: Task ID
        
        Returns:
            True if deleted, False if not found
        """
        with self.db.get_session() as session:
            task = session.query(Task).filter(Task.id == task_id).first()
            if not task:
                return False
            
            session.delete(task)
            session.flush()
            logger.info(f"Deleted task {task_id}")
            return True
    
    def archive_old_tasks(self, days: int = 30) -> int:
        """
        Archive (delete) old completed tasks.
        
        Args:
            days: Number of days to keep completed tasks
        
        Returns:
            Number of tasks archived
        """
        cutoff_date = get_ist_now() - timedelta(days=days)
        
        with self.db.get_session() as session:
            old_tasks = session.query(Task).filter(
                Task.is_completed == True,
                Task.completed_at < cutoff_date
            ).all()
            
            count = len(old_tasks)
            for task in old_tasks:
                session.delete(task)
            
            session.flush()
            logger.info(f"Archived {count} old tasks")
            return count
    
    def generate_daily_summary(self) -> str:
        """
        Generate a daily task summary.
        
        Returns:
            Formatted summary string
        """
        today_tasks = self.get_today_tasks()
        overdue_tasks = self.get_overdue_tasks()
        all_tasks = self.get_all_tasks()
        
        lines = [
            "",
            "📋 TASK SUMMARY",
            "-" * 60
        ]
        
        if overdue_tasks:
            lines.append(f"⚠️  Overdue Tasks: {len(overdue_tasks)}")
            for task in overdue_tasks[:3]:  # Show max 3
                lines.append(f"   • {task.title} (Due: {task.due_date.strftime('%Y-%m-%d')})")
        
        if today_tasks:
            lines.append(f"📅 Today's Tasks: {len(today_tasks)}")
            for task in today_tasks:
                priority_emoji = {"low": "🔵", "medium": "🟡", "high": "🔴"}.get(task.priority, "⚪")
                lines.append(f"   {priority_emoji} {task.title}")
        else:
            lines.append("📅 No tasks due today")
        
        # Priority breakdown
        high_priority = len([t for t in all_tasks if t.priority == "high"])
        if high_priority > 0:
            lines.append(f"🔴 High Priority Tasks: {high_priority}")
        
        return "\n".join(lines)
