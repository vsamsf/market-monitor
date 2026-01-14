"""Notification manager to handle multiple notification channels."""

from typing import List
from notifications.notifier import Notifier
from notifications.desktop_notifier import DesktopNotifier
from notifications.email_notifier import EmailNotifier
from notifications.telegram_notifier import TelegramNotifier
from utils.logger import get_logger

logger = get_logger(__name__)


class NotificationManager:
    """Manage multiple notification channels."""
    
    def __init__(self):
        """Initialize notification manager."""
        self.notifiers: List[Notifier] = []
    
    def add_notifier(self, notifier: Notifier):
        """
        Add a notifier to the manager.
        
        Args:
            notifier: Notifier instance
        """
        self.notifiers.append(notifier)
        logger.info(f"Added notifier: {notifier.__class__.__name__}")
    
    def send_notification(
        self,
        title: str,
        message: str,
        priority: str = "normal",
        channels: List[str] = None
    ) -> bool:
        """
        Send notification through all enabled channels.
        
        Args:
            title: Notification title
            message: Notification message
            priority: Priority level
            channels: Optional list of specific channel types to use
        
        Returns:
            True if at least one notification was sent successfully
        """
        if not self.notifiers:
            logger.warning("No notifiers configured")
            return False
        
        success = False
        
        for notifier in self.notifiers:
            # Filter by channel if specified
            if channels:
                notifier_type = notifier.__class__.__name__.replace('Notifier', '').lower()
                if notifier_type not in [c.lower() for c in channels]:
                    continue
            
            if notifier.notify(title, message, priority):
                success = True
        
        return success
    
    @classmethod
    def from_settings(cls, settings) -> "NotificationManager":
        """
        Create notification manager from settings.
        
        Args:
            settings: Settings object
        
        Returns:
            NotificationManager instance
        """
        manager = cls()
        
        # Desktop notifications
        if settings.notifications.desktop.enabled:
            desktop = DesktopNotifier(
                enabled=True,
                app_name=settings.notifications.desktop.app_name
            )
            manager.add_notifier(desktop)
        
        # Email notifications
        if settings.notifications.email.enabled:
            email = EmailNotifier(
                enabled=True,
                smtp_server=settings.notifications.email.smtp_server,
                smtp_port=settings.notifications.email.smtp_port,
                use_tls=settings.notifications.email.use_tls,
                sender_email=settings.notifications.email.sender_email,
                sender_password=settings.notifications.email.sender_password,
                recipient_email=settings.notifications.email.recipient_email
            )
            manager.add_notifier(email)
        
        # Telegram notifications
        if settings.notifications.telegram.enabled:
            telegram = TelegramNotifier(
                enabled=True,
                bot_token=settings.notifications.telegram.bot_token,
                chat_id=settings.notifications.telegram.chat_id
            )
            manager.add_notifier(telegram)
        
        return manager
