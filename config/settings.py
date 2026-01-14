"""Configuration management using Pydantic."""

from typing import List, Dict, Any
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings
import yaml


class AppSettings(BaseSettings):
    """Application settings."""
    name: str = "Market Monitor"
    timezone: str = "Asia/Kolkata"
    log_level: str = "INFO"
    log_file: str = "logs/app.log"


class DatabaseSettings(BaseSettings):
    """Database configuration."""
    url: str = "sqlite:///data/productivity.db"
    echo: bool = False


class MarketIndex(BaseSettings):
    """Market index configuration."""
    symbol: str
    name: str
    type: str


class MarketAlerts(BaseSettings):
    """Market alert thresholds."""
    significant_change_percent: float = 2.0
    large_move_percent: float = 1.5


class MarketSettings(BaseSettings):
    """Market monitoring configuration."""
    summary_time: str = "07:00"
    market_open: str = "09:15"
    market_close: str = "15:30"
    monitor_interval_minutes: int = 30
    indices: List[Dict[str, str]] = []
    alerts: MarketAlerts = Field(default_factory=MarketAlerts)


class DesktopNotificationSettings(BaseSettings):
    """Desktop notification settings."""
    enabled: bool = True
    app_name: str = "Market Monitor"


class EmailNotificationSettings(BaseSettings):
    """Email notification settings."""
    enabled: bool = False
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    use_tls: bool = True
    sender_email: str = ""
    sender_password: str = ""
    recipient_email: str = ""

    class Config:
        env_prefix = "EMAIL_"


class TelegramNotificationSettings(BaseSettings):
    """Telegram notification settings."""
    enabled: bool = False
    bot_token: str = ""
    chat_id: str = ""

    class Config:
        env_prefix = "TELEGRAM_"


class NotificationSettings(BaseSettings):
    """Notification configuration."""
    desktop: DesktopNotificationSettings = Field(default_factory=DesktopNotificationSettings)
    email: EmailNotificationSettings = Field(default_factory=EmailNotificationSettings)
    telegram: TelegramNotificationSettings = Field(default_factory=TelegramNotificationSettings)


class ReminderSettings(BaseSettings):
    """Reminder configuration."""
    check_interval_seconds: int = 60
    advance_notification_minutes: int = 5


class TaskSettings(BaseSettings):
    """Task/To-Do configuration."""
    default_priority: str = "medium"
    auto_archive_completed_days: int = 30
    priorities: List[str] = ["low", "medium", "high"]


class SchedulerJobDefaults(BaseSettings):
    """Scheduler job defaults."""
    coalesce: bool = True
    max_instances: int = 1
    misfire_grace_time: int = 300


class SchedulerSettings(BaseSettings):
    """Scheduler configuration."""
    timezone: str = "Asia/Kolkata"
    job_defaults: SchedulerJobDefaults = Field(default_factory=SchedulerJobDefaults)


class Settings(BaseSettings):
    """Main settings class."""
    app: AppSettings = Field(default_factory=AppSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    market: MarketSettings = Field(default_factory=MarketSettings)
    notifications: NotificationSettings = Field(default_factory=NotificationSettings)
    reminders: ReminderSettings = Field(default_factory=ReminderSettings)
    tasks: TaskSettings = Field(default_factory=TaskSettings)
    scheduler: SchedulerSettings = Field(default_factory=SchedulerSettings)

    @classmethod
    def load_from_yaml(cls, config_path: str = "config/config.yaml") -> "Settings":
        """Load settings from YAML file."""
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_file, 'r') as f:
            config_data = yaml.safe_load(f)
        
        return cls(**config_data)


# Global settings instance
settings: Settings = None


def get_settings() -> Settings:
    """Get or create settings instance."""
    global settings
    if settings is None:
        try:
            settings = Settings.load_from_yaml()
        except FileNotFoundError:
            # Use default settings if config file doesn't exist
            settings = Settings()
    return settings
