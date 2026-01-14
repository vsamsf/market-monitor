"""Desktop notification implementation for Ubuntu."""

import os
import subprocess
from notifications.notifier import Notifier
from utils.logger import get_logger

logger = get_logger(__name__)


class DesktopNotifier(Notifier):
    """Desktop notification using notify-send (Ubuntu/Linux)."""
    
    def __init__(self, enabled: bool = True, app_name: str = "Market Monitor"):
        """
        Initialize desktop notifier.
        
        Args:
            enabled: Whether notifications are enabled
            app_name: Application name for notifications
        """
        super().__init__(enabled)
        self.app_name = app_name
        self._check_availability()
    
    def _check_availability(self):
        """Check if notify-send is available."""
        try:
            result = subprocess.run(
                ['which', 'notify-send'],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                logger.warning("notify-send not found. Desktop notifications may not work.")
                logger.info("Install with: sudo apt-get install libnotify-bin")
        except Exception as e:
            logger.error(f"Error checking notify-send availability: {e}")
    
    def send(self, title: str, message: str, priority: str = "normal") -> bool:
        """
        Send desktop notification using notify-send.
        
        Args:
            title: Notification title
            message: Notification message
            priority: Priority level (low, normal, critical)
        
        Returns:
            True if sent successfully
        """
        try:
            # Map priority to urgency
            urgency_map = {
                'low': 'low',
                'normal': 'normal',
                'high': 'normal',
                'critical': 'critical'
            }
            urgency = urgency_map.get(priority, 'normal')
            
            # Build notify-send command
            cmd = [
                'notify-send',
                '--app-name', self.app_name,
                '--urgency', urgency,
                '--icon', 'dialog-information',
                title,
                message
            ]
            
            # Execute command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                logger.debug(f"Desktop notification sent: {title}")
                return True
            else:
                logger.error(f"notify-send failed: {result.stderr}")
                return False
                
        except FileNotFoundError:
            logger.error("notify-send command not found. Please install libnotify-bin")
            return False
        except subprocess.TimeoutExpired:
            logger.error("notify-send timed out")
            return False
        except Exception as e:
            logger.error(f"Error sending desktop notification: {e}")
            return False


class PlyrDesktopNotifier(Notifier):
    """Desktop notification using plyer library (cross-platform fallback)."""
    
    def __init__(self, enabled: bool = True, app_name: str = "Market Monitor"):
        """
        Initialize plyer desktop notifier.
        
        Args:
            enabled: Whether notifications are enabled
            app_name: Application name for notifications
        """
        super().__init__(enabled)
        self.app_name = app_name
        self._notification = None
        self._load_plyer()
    
    def _load_plyer(self):
        """Load plyer notification module."""
        try:
            from plyer import notification
            self._notification = notification
            logger.debug("Plyer notification module loaded")
        except ImportError:
            logger.warning("plyer not installed. Install with: pip install plyer")
            self.enabled = False
    
    def send(self, title: str, message: str, priority: str = "normal") -> bool:
        """
        Send desktop notification using plyer.
        
        Args:
            title: Notification title
            message: Notification message
            priority: Priority level (ignored for plyer)
        
        Returns:
            True if sent successfully
        """
        if self._notification is None:
            logger.error("Plyer notification not available")
            return False
        
        try:
            self._notification.notify(
                title=f"{self.app_name}: {title}",
                message=message,
                app_name=self.app_name,
                timeout=10
            )
            logger.debug(f"Plyer notification sent: {title}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending plyer notification: {e}")
            return False
