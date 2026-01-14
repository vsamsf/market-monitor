"""FastAPI REST API for Market Monitor & Productivity System."""

import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from config import get_settings
from utils.logger import setup_logger, get_logger
from database import get_db_manager
from todos import TaskManager
from reminders import ReminderManager
from market_monitor import SummaryGenerator, MarketDataFetcher
from scheduler import get_scheduler_service

# Initialize
settings = get_settings()
logger = setup_logger('api', settings.app.log_file, settings.app.log_level)

app = FastAPI(
    title="Market Monitor API",
    description="REST API for Market Monitor & Productivity System",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize managers
task_manager = TaskManager()
reminder_manager = ReminderManager()
market_fetcher = MarketDataFetcher()
summary_generator = SummaryGenerator()


# Pydantic models for API
class TaskCreate(BaseModel):
    title: str
    description: str = ""
    due_date: Optional[str] = None
    priority: str = "medium"


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[str] = None
    priority: Optional[str] = None


class ReminderCreate(BaseModel):
    title: str
    description: str = ""
    datetime: str
    recurring_type: Optional[str] = None


class ReminderUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    datetime: Optional[str] = None
    recurring_type: Optional[str] = None


# Health check
@app.get("/")
async def root():
    """Root endpoint - health check."""
    return {
        "status": "online",
        "service": "Market Monitor API",
        "version": "1.0.0"
    }


# Task endpoints
@app.get("/api/tasks")
async def get_tasks(include_completed: bool = False):
    """Get all tasks."""
    try:
        tasks = task_manager.get_all_tasks(include_completed=include_completed)
        return {"tasks": [task.to_dict() for task in tasks]}
    except Exception as e:
        logger.error(f"Error fetching tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tasks/{task_id}")
async def get_task(task_id: int):
    """Get a specific task."""
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task.to_dict()


@app.post("/api/tasks")
async def create_task(task: TaskCreate):
    """Create a new task."""
    try:
        new_task = task_manager.create_task(
            title=task.title,
            description=task.description,
            due_date=task.due_date,
            priority=task.priority
        )
        return {"task": new_task.to_dict(), "message": "Task created successfully"}
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/tasks/{task_id}")
async def update_task(task_id: int, task: TaskUpdate):
    """Update a task."""
    try:
        updated = task_manager.update_task(
            task_id=task_id,
            title=task.title,
            description=task.description,
            due_date=task.due_date,
            priority=task.priority
        )
        if not updated:
            raise HTTPException(status_code=404, detail="Task not found")
        return {"task": updated.to_dict(), "message": "Task updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/tasks/{task_id}/complete")
async def complete_task(task_id: int):
    """Mark task as complete."""
    success = task_manager.complete_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task completed successfully"}


@app.post("/api/tasks/{task_id}/uncomplete")
async def uncomplete_task(task_id: int):
    """Mark task as incomplete."""
    success = task_manager.uncomplete_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task marked as incomplete"}


@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: int):
    """Delete a task."""
    success = task_manager.delete_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully"}


@app.get("/api/tasks/filter/today")
async def get_today_tasks():
    """Get tasks due today."""
    tasks = task_manager.get_today_tasks()
    return {"tasks": [task.to_dict() for task in tasks]}


@app.get("/api/tasks/filter/overdue")
async def get_overdue_tasks():
    """Get overdue tasks."""
    tasks = task_manager.get_overdue_tasks()
    return {"tasks": [task.to_dict() for task in tasks]}


# Reminder endpoints
@app.get("/api/reminders")
async def get_reminders(active_only: bool = True):
    """Get all reminders."""
    try:
        reminders = reminder_manager.get_all_reminders(active_only=active_only)
        return {"reminders": [r.to_dict() for r in reminders]}
    except Exception as e:
        logger.error(f"Error fetching reminders: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/reminders/{reminder_id}")
async def get_reminder(reminder_id: int):
    """Get a specific reminder."""
    reminder = reminder_manager.get_reminder(reminder_id)
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return reminder.to_dict()


@app.post("/api/reminders")
async def create_reminder(reminder: ReminderCreate):
    """Create a new reminder."""
    try:
        new_reminder = reminder_manager.create_reminder(
            title=reminder.title,
            datetime_str=reminder.datetime,
            description=reminder.description,
            recurring_type=reminder.recurring_type
        )
        return {"reminder": new_reminder.to_dict(), "message": "Reminder created successfully"}
    except Exception as e:
        logger.error(f"Error creating reminder: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/reminders/{reminder_id}")
async def update_reminder(reminder_id: int, reminder: ReminderUpdate):
    """Update a reminder."""
    try:
        updated = reminder_manager.update_reminder(
            reminder_id=reminder_id,
            title=reminder.title,
            datetime_str=reminder.datetime,
            description=reminder.description,
            recurring_type=reminder.recurring_type
        )
        if not updated:
            raise HTTPException(status_code=404, detail="Reminder not found")
        return {"reminder": updated.to_dict(), "message": "Reminder updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating reminder: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/reminders/{reminder_id}")
async def delete_reminder(reminder_id: int):
    """Delete a reminder."""
    success = reminder_manager.delete_reminder(reminder_id)
    if not success:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return {"message": "Reminder deleted successfully"}


# Market data endpoints
@app.get("/api/market/summary")
async def get_market_summary():
    """Get current market summary."""
    try:
        summary = summary_generator.generate_daily_summary(
            indices=settings.market.indices,
            include_sectors=True
        )
        
        # If summary indicates failure, use demo data
        if "Unable to fetch" in summary or not summary.strip():
            logger.warning("Market summary generation failed, using demo data")
            from market_monitor.demo_data import get_demo_summary
            summary = get_demo_summary()
        
        return {"summary": summary}
    except Exception as e:
        logger.error(f"Error generating market summary: {e}")
        # Return demo summary on error
        try:
            from market_monitor.demo_data import get_demo_summary
            return {"summary": get_demo_summary()}
        except:
            raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/market/indices")
async def get_market_indices():
    """Get current market index data."""
    try:
        indices_data = market_fetcher.fetch_multiple_indices(settings.market.indices)
        
        # If no data was fetched (API failures, rate limits, etc.), use demo data
        if not indices_data:
            logger.warning("No real market data available, returning demo data")
            from market_monitor.demo_data import get_demo_indices
            indices_data = get_demo_indices()
        
        return {"indices": indices_data}
    except Exception as e:
        logger.error(f"Error fetching market indices: {e}")
        # Return demo data on error
        try:
            from market_monitor.demo_data import get_demo_indices
            return {"indices": get_demo_indices()}
        except:
            raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/market/sectors")
async def get_sector_performance():
    """Get sector performance data."""
    try:
        sectors = market_fetcher.get_sector_performance()
        return {"sectors": sectors}
    except Exception as e:
        logger.error(f"Error fetching sector performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# System endpoints
@app.get("/api/system/status")
async def get_system_status():
    """Get system and scheduler status."""
    try:
        scheduler = get_scheduler_service()
        jobs = scheduler.get_jobs() if scheduler.scheduler else []
        
        return {
            "status": "running",
            "scheduler_active": scheduler.scheduler is not None,
            "jobs": [
                {
                    "id": job.id,
                    "name": job.name,
                    "next_run": job.next_run_time.isoformat() if job.next_run_time else None
                }
                for job in jobs
            ]
        }
    except Exception as e:
        logger.error(f"Error fetching system status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    """Get dashboard statistics."""
    try:
        all_tasks = task_manager.get_all_tasks(include_completed=False)
        today_tasks = task_manager.get_today_tasks()
        overdue_tasks = task_manager.get_overdue_tasks()
        active_reminders = reminder_manager.get_all_reminders(active_only=True)
        
        return {
            "tasks": {
                "total": len(all_tasks),
                "today": len(today_tasks),
                "overdue": len(overdue_tasks),
                "high_priority": len([t for t in all_tasks if t.priority == "high"])
            },
            "reminders": {
                "active": len(active_reminders)
            }
        }
    except Exception as e:
        logger.error(f"Error fetching dashboard stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Serve static files (frontend) in production
static_dir = Path(__file__).parent.parent / "static"
if static_dir.exists():
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
