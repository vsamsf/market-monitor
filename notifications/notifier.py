"""Base notification interface."""

from abc import ABC, abstractmethod
from typing import Optional
from utils.logger import get_logger

logger = get_logger(__name__)


class Notifier(ABC):
    """Abstract base class for all notifiers."""
    
    def __init__(self, enabled: bool = True):
        """
        Initialize notifier.
        
        Args:
            enabled: Whether this notifier is enabled
        """
        self.enabled = enabled
    
    @abstractmethod
    def send(self, title: str, message: str, priority: str = "normal") -> bool:
        """
        Send a notification.
        
        Args:
            title: Notification title
            message: Notification message
            priority: Priority level (low, normal, high, critical)
        
        Returns:
            True if sent successfully, False otherwise
        """
        pass
    
    def notify(self, title: str, message: str, priority: str = "normal", retry: int = 3) -> bool:
        """
        Send notification with retry logic.
        
        Args:
            title: Notification title
            message: Notification message
            priority: Priority level
            retry: Number of retries on failure
        
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.enabled:
            logger.debug(f"Notifier {self.__class__.__name__} is disabled")
            return False
        
        for attempt in range(retry):
            try:
                success = self.send(title, message, priority)
                if success:
                    logger.info(f"Notification sent via {self.__class__.__name__}: {title}")
                    return True
                else:
                    logger.warning(f"Failed to send notification (attempt {attempt + 1}/{retry})")
            except Exception as e:
                logger.error(f"Error sending notification (attempt {attempt + 1}/{retry}): {e}")
        
        logger.error(f"Failed to send notification after {retry} attempts")
        return False
