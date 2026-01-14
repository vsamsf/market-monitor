#!/bin/bash
# Setup script for Ubuntu VM

set -e

echo "=========================================="
echo "Market Monitor & Productivity System Setup"
echo "=========================================="
echo ""

# Check if running on Ubuntu
if [ ! -f /etc/os-release ]; then
    echo "Error: Cannot detect OS. This script is designed for Ubuntu."
    exit 1
fi

# Update package list
echo "📦 Updating package list..."
sudo apt-get update

# Install Python 3 and pip
echo "🐍 Installing Python 3 and pip..."
sudo apt-get install -y python3 python3-pip python3-venv

# Install system dependencies for notifications
echo "🔔 Installing notification dependencies..."
sudo apt-get install -y libnotify-bin

# Create virtual environment
echo "🔨 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data logs

# Run application setup
echo "🔧 Running application setup..."
python main.py setup

# Create systemd service file
echo "⚙️  Creating systemd service..."
SERVICE_FILE="/etc/systemd/system/market-monitor.service"

sudo tee $SERVICE_FILE > /dev/null <<EOF
[Unit]
Description=Market Monitor & Productivity System
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment="PATH=$(pwd)/venv/bin"
ExecStart=$(pwd)/venv/bin/python $(pwd)/main.py daemon
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
echo "🔄 Reloading systemd..."
sudo systemctl daemon-reload

# Enable service
echo "✅ Enabling service to start on boot..."
sudo systemctl enable market-monitor.service

echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Edit config/config.yaml to configure your settings"
echo "  2. Copy .env.example to .env and add your credentials (if using email/telegram)"
echo "  3. Test the system: python main.py daemon --test"
echo "  4. Start the service: sudo systemctl start market-monitor"
echo "  5. Check status: sudo systemctl status market-monitor"
echo "  6. View logs: journalctl -u market-monitor -f"
echo ""
echo "Manual commands:"
echo "  • Start: sudo systemctl start market-monitor"
echo "  • Stop: sudo systemctl stop market-monitor"
echo "  • Restart: sudo systemctl restart market-monitor"
echo "  • Status: sudo systemctl status market-monitor"
echo ""
