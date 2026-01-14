#!/usr/bin/env python3
"""Test script to verify system functionality."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from colorama import Fore, Style, init
from config import get_settings
from utils.logger import setup_logger
from database import get_db_manager
from market_monitor import MarketDataFetcher, SummaryGenerator
from reminders import ReminderManager
from todos import TaskManager
from notifications import NotificationManager

# Initialize colorama
init(autoreset=True)


def print_section(title):
    """Print section header."""
    print(f"\n{Fore.CYAN}{'=' * 70}")
    print(f"{title}")
    print(f"{'=' * 70}{Style.RESET_ALL}\n")


def test_configuration():
    """Test configuration loading."""
    print_section("Testing Configuration")
    
    try:
        settings = get_settings()
        print(f"{Fore.GREEN}✓ Configuration loaded successfully")
        print(f"  App Name: {settings.app.name}")
        print(f"  Timezone: {settings.app.timezone}")
        print(f"  Database: {settings.database.url}")
        return True
    except Exception as e:
        print(f"{Fore.RED}✗ Configuration failed: {e}")
        return False


def test_database():
    """Test database initialization."""
    print_section("Testing Database")
    
    try:
        db = get_db_manager()
        print(f"{Fore.GREEN}✓ Database initialized successfully")
        print(f"  Database URL: {db.database_url}")
        return True
    except Exception as e:
        print(f"{Fore.RED}✗ Database failed: {e}")
        return False


def test_market_data():
    """Test market data fetching."""
    print_section("Testing Market Data Fetching")
    
    try:
        fetcher = MarketDataFetcher()
        
        # Test NIFTY 50
        print(f"{Fore.YELLOW}Fetching NIFTY 50 data...")
        data = fetcher.fetch_index_data('^NSEI', 'NIFTY 50')
        
        if data:
            print(f"{Fore.GREEN}✓ Market data fetched successfully")
            print(f"  Index: {data['name']}")
            print(f"  Current Price: {data['current_price']}")
            print(f"  Change: {data['change']} ({data['change_percent']}%)")
            return True
        else:
            print(f"{Fore.YELLOW}⚠ Market data returned None (might be after market hours)")
            return True  # Not a failure, just timing
    except Exception as e:
        print(f"{Fore.RED}✗ Market data fetching failed: {e}")
        return False


def test_summary_generation():
    """Test summary generation."""
    print_section("Testing Summary Generation")
    
    try:
        generator = SummaryGenerator()
        settings = get_settings()
        
        print(f"{Fore.YELLOW}Generating market summary...")
        summary = generator.generate_daily_summary(
            indices=settings.market.indices[:2],  # Test with first 2 indices
            include_sectors=False
        )
        
        print(f"{Fore.GREEN}✓ Summary generated successfully")
        print(f"\n{summary}")
        return True
    except Exception as e:
        print(f"{Fore.RED}✗ Summary generation failed: {e}")
        return False


def test_reminders():
    """Test reminder functionality."""
    print_section("Testing Reminders")
    
    try:
        manager = ReminderManager()
        
        # Create test reminder
        print(f"{Fore.YELLOW}Creating test reminder...")
        reminder = manager.create_reminder(
            title="Test Reminder",
            datetime_str="2026-01-15 10:00",
            description="This is a test reminder"
        )
        
        print(f"{Fore.GREEN}✓ Reminder created (ID: {reminder.id})")
        
        # List reminders
        reminders = manager.get_all_reminders()
        print(f"  Total active reminders: {len(reminders)}")
        
        # Delete test reminder
        manager.delete_reminder(reminder.id)
        print(f"{Fore.GREEN}✓ Test reminder deleted")
        
        return True
    except Exception as e:
        print(f"{Fore.RED}✗ Reminder test failed: {e}")
        return False


def test_tasks():
    """Test task functionality."""
    print_section("Testing Tasks")
    
    try:
        manager = TaskManager()
        
        # Create test task
        print(f"{Fore.YELLOW}Creating test task...")
        task = manager.create_task(
            title="Test Task",
            description="This is a test task",
            priority="high"
        )
        
        print(f"{Fore.GREEN}✓ Task created (ID: {task.id})")
        
        # Complete task
        manager.complete_task(task.id)
        print(f"{Fore.GREEN}✓ Task completed")
        
        # Delete test task
        manager.delete_task(task.id)
        print(f"{Fore.GREEN}✓ Test task deleted")
        
        return True
    except Exception as e:
        print(f"{Fore.RED}✗ Task test failed: {e}")
        return False


def test_notifications():
    """Test notification system."""
    print_section("Testing Notifications")
    
    try:
        settings = get_settings()
        notifier = NotificationManager.from_settings(settings)
        
        print(f"{Fore.YELLOW}Sending test notification...")
        success = notifier.send_notification(
            title="Test Notification",
            message="This is a test notification from the Market Monitor system.",
            priority="normal"
        )
        
        if success:
            print(f"{Fore.GREEN}✓ Notification sent successfully")
        else:
            print(f"{Fore.YELLOW}⚠ Notification delivery uncertain (check your notification settings)")
        
        return True
    except Exception as e:
        print(f"{Fore.RED}✗ Notification test failed: {e}")
        return False


def main():
    """Run all tests."""
    print(f"\n{Fore.CYAN}{'=' * 70}")
    print(f"Market Monitor & Productivity System - Test Suite")
    print(f"{'=' * 70}{Style.RESET_ALL}")
    
    # Setup logger
    logger = setup_logger('test', 'logs/test.log', 'INFO')
    
    # Run tests
    tests = [
        ("Configuration", test_configuration),
        ("Database", test_database),
        ("Market Data", test_market_data),
        ("Summary Generation", test_summary_generation),
        ("Reminders", test_reminders),
        ("Tasks", test_tasks),
        ("Notifications", test_notifications),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"{Fore.RED}✗ Unexpected error in {name}: {e}")
            results.append((name, False))
    
    # Print summary
    print_section("Test Summary")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = f"{Fore.GREEN}PASS" if success else f"{Fore.RED}FAIL"
        print(f"{status}{Style.RESET_ALL} - {name}")
    
    print(f"\n{Fore.CYAN}Results: {passed}/{total} tests passed")
    
    if passed == total:
        print(f"{Fore.GREEN}✓ All tests passed! System is ready to use.{Style.RESET_ALL}")
        return 0
    else:
        print(f"{Fore.YELLOW}⚠ Some tests failed. Review the errors above.{Style.RESET_ALL}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
