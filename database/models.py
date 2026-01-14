"""Database models using SQLAlchemy."""

from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class Reminder(Base):
    """Reminder model for storing user reminders."""
    
    __tablename__ = 'reminders'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    datetime = Column(DateTime, nullable=False)
    recurring_type = Column(String(20), nullable=True)  # daily, weekly, monthly
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    last_notified = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<Reminder(id={self.id}, title='{self.title}', datetime={self.datetime})>"
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'datetime': self.datetime.isoformat() if self.datetime else None,
            'recurring_type': self.recurring_type,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Task(Base):
    """Task model for to-do list items."""
    
    __tablename__ = 'tasks'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    due_date = Column(DateTime, nullable=True)
    priority = Column(String(20), default='medium', nullable=False)  # low, medium, high
    is_completed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    completed_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        status = "✓" if self.is_completed else "○"
        return f"<Task({status} {self.id}: '{self.title}' - {self.priority})>"
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'priority': self.priority,
            'is_completed': self.is_completed,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }


class MarketSnapshot(Base):
    """Market snapshot model for historical tracking."""
    
    __tablename__ = 'market_snapshots'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    index_name = Column(String(50), nullable=False)
    index_symbol = Column(String(50), nullable=False)
    value = Column(Float, nullable=False)
    change = Column(Float, nullable=True)
    change_percent = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    def __repr__(self):
        return f"<MarketSnapshot({self.index_name}: {self.value} at {self.timestamp})>"
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'index_name': self.index_name,
            'index_symbol': self.index_symbol,
            'value': self.value,
            'change': self.change,
            'change_percent': self.change_percent,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
