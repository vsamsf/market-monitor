# Market Monitor & Productivity System

A Python-based automated system for daily financial market monitoring and personal productivity management, designed to run on Ubuntu.

## 🌟 Features

### Market Monitoring
- **Daily Market Summary** (7:00 AM IST)
  - NSE NIFTY 50 and BSE SENSEX indices
  - Market sentiment analysis (bullish/bearish)
  - Sector performance overview
  - Top gainers and losers

- **Live Market Updates** (Every 30 minutes during market hours)
  - Real-time index tracking (9:15 AM - 3:30 PM IST)
  - Mid-cap and small-cap trend analysis
  - Automatic alerts on significant moves

### Productivity Management
- **Reminder System**
  - Create, view, update, and delete reminders
  - Recurring reminders (daily, weekly, monthly)
  - Advance notifications
  - Multiple notification channels

- **To-Do List Management**
  - Task creation with priorities (low, medium, high)
  - Due date tracking
  - Daily task summaries
  - Overdue task alerts
  - Auto-archive completed tasks

### Notifications
- Desktop notifications (Ubuntu)
- Email notifications (SMTP)
- Telegram bot integration (optional)

## 📋 Requirements

- Ubuntu 20.04+ (or compatible Linux distribution)
- Python 3.8+
- Internet connection for market data

## 🚀 Quick Start

### 1. Clone or Download

```bash
cd /path/to/MyApp
```

### 2. Run Setup Script (Ubuntu)

```bash
chmod +x setup.sh
./setup.sh
```

This will:
- Install Python dependencies
- Create virtual environment
- Initialize database
- Set up systemd service

### 3. Configure

Edit `config/config.yaml` to customize:
- Market monitoring schedule
- Notification preferences
- Alert thresholds

For email or Telegram notifications:
```bash
cp .env.example .env
# Edit .env with your credentials
```

### 4. Test the System

```bash
# Activate virtual environment
source venv/bin/activate

# Run a test
python main.py daemon --test
```

### 5. Start the Service

```bash
# Start as systemd service
sudo systemctl start market-monitor

# Check status
sudo systemctl status market-monitor

# View logs
journalctl -u market-monitor -f
```

## 💻 Manual Usage

### Run as Daemon

```bash
python main.py daemon
```

### View Scheduled Jobs Status

```bash
python main.py status
```

### Run a Specific Job Immediately

```bash
python main.py run-job daily_market_summary
```

### Generate Market Summary

```bash
python main.py market-summary
```

### View Task Summary

```bash
python main.py task-summary
```

## 📁 Project Structure

```
MyApp/
├── config/              # Configuration files
│   ├── config.yaml      # Main configuration
│   └── settings.py      # Settings loader
├── database/            # Database models and manager
├── market_monitor/      # Market data fetching and analysis
├── reminders/           # Reminder management
├── todos/               # Task management
├── notifications/       # Notification system
├── scheduler/           # Job scheduling
├── utils/               # Utility functions
├── main.py              # Application entry point
├── requirements.txt     # Python dependencies
└── setup.sh             # Ubuntu setup script
```

## ⚙️ Configuration

### Market Data Sources

The system uses `yfinance` to fetch Indian stock market data. Supported indices:
- NIFTY 50 (^NSEI)
- SENSEX (^BSESN)
- NIFTY MIDCAP 50 (^NSEMDCP50)
- NIFTY SMALLCAP 50 (NIFTY_SMLCAP_50.NS)
- Sector indices (BANK, IT, AUTO, PHARMA, FMCG)

### Notification Setup

#### Desktop Notifications (Ubuntu)
Enabled by default. Uses `notify-send`.

#### Email Notifications
Set in `.env`:
```env
EMAIL_SENDER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_RECIPIENT=recipient@gmail.com
```

For Gmail, use an [App Password](https://support.google.com/accounts/answer/185833).

#### Telegram Notifications
1. Create a bot via [@BotFather](https://t.me/botfather)
2. Get your chat ID via [@userinfobot](https://t.me/userinfobot)
3. Set in `.env`:
```env
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_CHAT_ID=your-chat-id
```

## 🔧 Troubleshooting

### Desktop Notifications Not Working
```bash
# Install libnotify-bin
sudo apt-get install libnotify-bin
```

### Market Data Not Fetching
- Check internet connection
- Verify market hours (9:15 AM - 3:30 PM IST on weekdays)
- yfinance may have rate limits

### Service Not Starting
```bash
# Check service status
sudo systemctl status market-monitor

# View detailed logs
journalctl -u market-monitor -xe

# Check application logs
tail -f logs/app.log
```

## 📊 Scheduled Jobs

| Job | Schedule | Description |
|-----|----------|-------------|
| Daily Summary | 7:00 AM IST | Market summary + task list |
| Market Monitor | Every 30 min (9:15 AM - 3:30 PM) | Live index updates |
| Check Reminders | Every minute | Process due reminders |
| Cleanup | Daily at midnight | Archive old completed tasks |

## 🛠️ Development

### Install for Development

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Run Tests

```bash
pytest tests/
```

### Add New Features

1. Market indicators → `market_monitor/analyzer.py`
2. Custom jobs → `scheduler/jobs.py`
3. New notification channels → Create in `notifications/`

## 📝 License

This project is for personal use.

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📧 Support

For issues, check the logs:
- Application logs: `logs/app.log`
- System logs: `journalctl -u market-monitor`

---

**Made with ❤️ for automated market monitoring and productivity**
