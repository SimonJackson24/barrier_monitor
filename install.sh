#!/bin/bash

# Barrier Monitor Installation Script

echo "Barrier Monitor System Installation"
echo "---------------------------------"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (sudo)"
    exit 1
fi

# Install system dependencies
echo "Installing system dependencies..."
apt-get update
apt-get install -y python3-pip python3-venv

# Create virtual environment
echo "Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "Installing Python packages..."
pip install -r requirements.txt

# Create necessary directories
echo "Creating system directories..."
mkdir -p /opt/barrier-monitor
mkdir -p /var/log/barrier-monitor

# Copy files to installation directory
echo "Copying files..."
cp -r * /opt/barrier-monitor/
cp barrier-monitor.service /etc/systemd/system/

# Set permissions
echo "Setting permissions..."
chown -R pi:pi /opt/barrier-monitor
chown -R pi:pi /var/log/barrier-monitor
chmod 755 /opt/barrier-monitor/monitor.py

# Setup systemd service
echo "Setting up systemd service..."
systemctl daemon-reload
systemctl enable barrier-monitor

echo
echo "Installation complete!"
echo
echo "Next steps:"
echo "1. Configure your settings in /opt/barrier-monitor/config.yaml"
echo "2. Run 'python3 setup_gmail_credentials.py' to set up email notifications"
echo "3. Run 'python3 tests/test_gpio.py' to verify your hardware setup"
echo "4. Start the service with 'sudo systemctl start barrier-monitor'"
echo
echo "To view logs:"
echo "  journalctl -u barrier-monitor -f"
echo
echo "To check service status:"
echo "  systemctl status barrier-monitor"
