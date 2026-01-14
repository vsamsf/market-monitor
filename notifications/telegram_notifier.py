"""Telegram notification implementation."""

from typing import Optional
from notifications.notifier import Notifier
from utils.logger import get_logger

logger = get_logger(__name__)


class TelegramNotifier(Notifier):
    """Telegram notification using bot API."""
    
    def __init__(
        self,
        enabled: bool = False,
        bot_token: str = "",
        chat_id: str = ""
    ):
        """
        Initialize Telegram notifier.
        
        Args:
            enabled: Whether Telegram notifications are enabled
            bot_token: Telegram bot token
            chat_id: Chat ID to send messages to
        """
        super().__init__(enabled)
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.bot = None
        
        # Validate and initialize
        if enabled and not all([bot_token, chat_id]):
            logger.warning("Telegram notifier enabled but missing credentials")
            self.enabled = False
        elif enabled:
            self._initialize_bot()
    
    def _initialize_bot(self):
        """Initialize Telegram bot."""
        try:
            from telegram import Bot
            self.bot = Bot(token=self.bot_token)
            logger.info("Telegram bot initialized")
        except ImportError:
            logger.warning("python-telegram-bot not installed. Install with: pip install python-telegram-bot")
            self.enabled = False
        except Exception as e:
            logger.error(f"Error initializing Telegram bot: {e}")
            self.enabled = False
    
    def send(self, title: str, message: str, priority: str = "normal") -> bool:
        """
        Send Telegram message.
        
        Args:
            title: Message title
            message: Message content
            priority: Priority level (affects emoji prefix)
        
        Returns:
            True if sent successfully
        """
        if self.bot is None:
            logger.error("Telegram bot not initialized")
            return False
        
        try:
            # Add emoji based on priority
            priority_emoji = {
                'low': 'ℹ️',
                'normal': '📢',
                'high': '⚠️',
                'critical': '🚨'
            }.get(priority, '📢')
            
            # Format message
            formatted_message = f"{priority_emoji} <b>{title}</b>\n\n{message}"
            
            # Send message
            import asyncio
            asyncio.run(self.bot.send_message(
                chat_id=self.chat_id,
                text=formatted_message,
                parse_mode='HTML'
            ))
            
            logger.info(f"Telegram message sent: {title}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
            return False
