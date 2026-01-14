"""Database manager for handling database operations."""

from pathlib import Path
from typing import Optional, List, Type, TypeVar
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from database.models import Base, Reminder, Task, MarketSnapshot
from utils.logger import get_logger

logger = get_logger(__name__)

T = TypeVar('T')


class DatabaseManager:
    """Database manager class for all database operations."""
    
    def __init__(self, database_url: str = "sqlite:///data/productivity.db"):
        """
        Initialize database manager.
        
        Args:
            database_url: SQLAlchemy database URL
        """
        self.database_url = database_url
        
        # Create data directory if using SQLite
        if database_url.startswith('sqlite:///'):
            db_path = Path(database_url.replace('sqlite:///', ''))
            db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.engine = create_engine(database_url, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        logger.info(f"Database initialized: {database_url}")
    
    def create_tables(self):
        """Create all tables in the database."""
        Base.metadata.create_all(bind=self.engine)
        logger.info("Database tables created")
    
    def drop_tables(self):
        """Drop all tables in the database."""
        Base.metadata.drop_all(bind=self.engine)
        logger.warning("Database tables dropped")
    
    @contextmanager
    def get_session(self) -> Session:
        """
        Get a database session context manager.
        
        Yields:
            Database session
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    def add(self, obj: T) -> T:
        """
        Add an object to the database.
        
        Args:
            obj: SQLAlchemy model instance
        
        Returns:
            The added object
        """
        with self.get_session() as session:
            session.add(obj)
            session.flush()
            session.refresh(obj)
            # Expunge to avoid detached instance errors
            session.expunge(obj)
            return obj
    
    def get_by_id(self, model: Type[T], obj_id: int) -> Optional[T]:
        """
        Get an object by ID.
        
        Args:
            model: SQLAlchemy model class
            obj_id: Object ID
        
        Returns:
            Model instance or None
        """
        with self.get_session() as session:
            return session.query(model).filter(model.id == obj_id).first()
    
    def get_all(self, model: Type[T]) -> List[T]:
        """
        Get all objects of a model.
        
        Args:
            model: SQLAlchemy model class
        
        Returns:
            List of model instances
        """
        with self.get_session() as session:
            return session.query(model).all()
    
    def update(self, obj: T) -> T:
        """
        Update an object in the database.
        
        Args:
            obj: SQLAlchemy model instance
        
        Returns:
            Updated object
        """
        with self.get_session() as session:
            session.merge(obj)
            session.flush()
            return obj
    
    def delete(self, obj: T):
        """
        Delete an object from the database.
        
        Args:
            obj: SQLAlchemy model instance
        """
        with self.get_session() as session:
            session.delete(obj)
            session.flush()
    
    def delete_by_id(self, model: Type[T], obj_id: int):
        """
        Delete an object by ID.
        
        Args:
            model: SQLAlchemy model class
            obj_id: Object ID
        """
        with self.get_session() as session:
            obj = session.query(model).filter(model.id == obj_id).first()
            if obj:
                session.delete(obj)
                session.flush()


# Global database manager instance
db_manager: Optional[DatabaseManager] = None


def get_db_manager(database_url: Optional[str] = None) -> DatabaseManager:
    """
    Get or create database manager instance.
    
    Args:
        database_url: Optional database URL override
    
    Returns:
        DatabaseManager instance
    """
    global db_manager
    if db_manager is None:
        if database_url is None:
            from config import get_settings
            settings = get_settings()
            database_url = settings.database.url
        db_manager = DatabaseManager(database_url)
        db_manager.create_tables()
    return db_manager
