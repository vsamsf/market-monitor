"""Quick start guide and examples."""

# Quick Start Guide

This guide will help you get started with the Market Monitor & Productivity System.

## 1. Installation

### On Ubuntu VM:
```bash
# Clone or navigate to project directory
cd /path/to/MyApp

# Run setup script
chmod +x setup.sh
./setup.sh
```

### On Mac/Development:
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize
python main.py setup
```

## 2. Configuration

Edit `config/config.yaml` to customize:
- Market monitoring times
- Notification preferences
- Alert thresholds

For email/Telegram:
```bash
cp .env.example .env
# Edit .env with your credentials
```

## 3. Testing the System

```bash
# Activate virtual environment
source venv/bin/activate

# Run comprehensive test
python test_system.py

# Quick test with notification
python main.py daemon --test
```

## 4. Managing Reminders

```bash
# Add a reminder
python -m reminders.cli add -t "Meeting" -d "2026-01-15 14:00" -desc "Team meeting"

# Add recurring reminder
python -m reminders.cli add -t "Daily Standup" -d "2026-01-15 09:00" -r daily

# List all reminders
python -m reminders.cli list

# Show due reminders
python -m reminders.cli due

# Delete a reminder
python -m reminders.cli delete 1
```

## 5. Managing Tasks

```bash
# Add a task
python -m todos.cli add -t "Complete report" -p high -d "2026-01-20"

# Add task with description
python -m todos.cli add -t "Buy groceries" -desc "Milk, eggs, bread" -p low

# List all tasks
python -m todos.cli list

# Show today's tasks
python -m todos.cli today

# Show overdue tasks
python -m todos.cli overdue

# Complete a task
python -m todos.cli complete 1

# Delete a task
python -m todos.cli delete 2

# Show task summary
python -m todos.cli summary
```

## 6. Market Information

```bash
# Get current market summary
python main.py market-summary

# View task summary
python main.py task-summary
```

## 7. Running as a Service

### Start the daemon:
```bash
# Manual mode (foreground)
python main.py daemon

# As systemd service (Ubuntu)
sudo systemctl start market-monitor
sudo systemctl status market-monitor
```

### View logs:
```bash
# Application logs
tail -f logs/app.log

# System logs (if using systemd)
journalctl -u market-monitor -f
```

### Check scheduled jobs:
```bash
python main.py status
```

### Run a job manually:
```bash
python main.py run-job daily_market_summary
python main.py run-job check_reminders
```

## 8. Daily Workflow

The system automatically:

**7:00 AM IST** - Sends daily summary with:
- Market overview from previous day
- Today's tasks
- Overdue tasks

**During market hours (9:15 AM - 3:30 PM)** - Every 30 minutes:
- Live market updates
- Significant movement alerts

**Every minute**:
- Checks for due reminders
- Sends notifications for upcoming reminders

**Midnight**:
- Archives old completed tasks (>30 days)

## 9. Example Scenarios

### Scenario 1: Set up morning routine
```bash
# Add morning reminders
python -m reminders.cli add -t "Morning Exercise" -d "2026-01-15 06:00" -r daily
python -m reminders.cli add -t "Check Emails" -d "2026-01-15 08:00" -r daily

# Add tasks for the day
python -m todos.cli add -t "Review market report" -p high -d today
python -m todos.cli add -t "Update portfolio" -p medium -d today
```

### Scenario 2: Track project deadlines
```bash
# Add project tasks
python -m todos.cli add -t "Submit proposal" -p high -d "2026-01-20" -desc "Client XYZ proposal"
python -m todos.cli add -t "Code review" -p medium -d "2026-01-18"
python -m todos.cli add -t "Documentation" -p low -d "2026-01-25"

# Set reminder before deadline
python -m reminders.cli add -t "Proposal due tomorrow" -d "2026-01-19 17:00"
```

### Scenario 3: Monitor specific market movements
```bash
# System automatically monitors configured indices
# You can customize thresholds in config/config.yaml:
# market:
#   alerts:
#     significant_change_percent: 2.0  # Alert if >2% move
#     large_move_percent: 1.5          # Warning if >1.5% move
```

## 10. Troubleshooting

### Notifications not working:
```bash
# Test desktop notifications
notify-send "Test" "This is a test"

# Check notification settings in config/config.yaml
# Enable desktop notifications:
notifications:
  desktop:
    enabled: true
```

### Market data not fetching:
```bash
# Test manually
python -c "from market_monitor import MarketDataFetcher; f = MarketDataFetcher(); print(f.fetch_index_data('^NSEI', 'NIFTY 50'))"

# Check internet connection
# Verify market hours (9:15 AM - 3:30 PM IST on weekdays)
```

### Service not starting:
```bash
# Check logs
journalctl -u market-monitor -xe

# Test manually
python main.py daemon

# Check if port is already in use (if using web interface)
```

## 11. Advanced Usage

### Custom notification channels:
Edit `config/config.yaml` to enable email or Telegram.

### Modify schedule:
Edit `config/config.yaml` to change:
- Daily summary time
- Market monitoring interval
- Reminder check frequency

### Add more indices:
Edit `config/config.yaml` and add to `market.indices` list.

## Support

Check logs:
- Application: `logs/app.log`
- Test: `logs/test.log`

For issues, review the README.md and implementation documentation.
