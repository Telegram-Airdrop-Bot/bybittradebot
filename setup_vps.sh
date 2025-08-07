#!/bin/bash

# ByBit Grid Trading Bot - VPS Setup Script
# This script sets up the environment for running the trading bot on a VPS

set -e

echo "Setting up ByBit Grid Trading Bot on VPS..."

# Update system
echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python 3.9+ and pip
echo "Installing Python and dependencies..."
sudo apt install -y python3 python3-pip python3-venv

# Install Redis for state persistence
echo "Installing Redis..."
sudo apt install -y redis-server
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Install system monitoring tools
echo "Installing monitoring tools..."
sudo apt install -y htop iotop nethogs

# Create bot directory
echo "Creating bot directory..."
sudo mkdir -p /opt/bybit-bot
sudo chown $USER:$USER /opt/bybit-bot

# Copy bot files to VPS
echo "Copying bot files..."
cp -r * /opt/bybit-bot/
cd /opt/bybit-bot

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create systemd service
echo "Creating systemd service..."
sudo tee /etc/systemd/system/bybit-bot.service > /dev/null <<EOF
[Unit]
Description=ByBit Grid Trading Bot
After=network.target redis.service

[Service]
Type=simple
User=$USER
WorkingDirectory=/opt/bybit-bot
Environment=PATH=/opt/bybit-bot/venv/bin
ExecStart=/opt/bybit-bot/venv/bin/python run.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable service
sudo systemctl daemon-reload
sudo systemctl enable bybit-bot.service

# Create log directory
sudo mkdir -p /var/log/bybit-bot
sudo chown $USER:$USER /var/log/bybit-bot

# Set up log rotation
sudo tee /etc/logrotate.d/bybit-bot > /dev/null <<EOF
/var/log/bybit-bot/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 $USER $USER
}
EOF

# Create configuration template
echo "Creating configuration template..."
if [ ! -f config.yaml ]; then
    cp config.yaml.example config.yaml 2>/dev/null || echo "Please create config.yaml with your API credentials"
fi

echo ""
echo "=== VPS Setup Complete ==="
echo ""
echo "Next steps:"
echo "1. Edit /opt/bybit-bot/config.yaml with your ByBit API credentials"
echo "2. Test the bot: cd /opt/bybit-bot && source venv/bin/activate && python run.py"
echo "3. Start the service: sudo systemctl start bybit-bot"
echo "4. Check status: sudo systemctl status bybit-bot"
echo "5. View logs: sudo journalctl -u bybit-bot -f"
echo ""
echo "Bot will automatically restart on system reboot."
echo "" 