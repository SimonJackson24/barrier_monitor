# System Verification Checklist

## Required Credentials
- [ ] Gmail API credentials (`credentials.json`)
- [ ] Active SIM card with data plan
- [ ] APN settings for your cellular provider

## Configuration Files
- [ ] `config.yaml` with all required settings
  - Email configuration
  - GPIO pin assignments
  - LTE settings
  - Circuit configurations
  - Notification parameters

## System Dependencies
- [ ] Python packages:
  ```
  RPi.GPIO
  google-api-python-client
  google-auth-oauthlib
  google-auth-httplib2
  pyyaml
  flask
  pyserial
  ```

## Installation Steps

1. Install System Dependencies:
```bash
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv
```

2. Create Virtual Environment:
```bash
python3 -m venv /opt/barrier-monitor/venv
source /opt/barrier-monitor/venv/bin/activate
```

3. Install Python Dependencies:
```bash
pip install -r requirements.txt
```

4. Set Up Gmail API:
- Create project in Google Cloud Console
- Enable Gmail API
- Create OAuth credentials
- Download `credentials.json`
- Place in project directory

5. Configure LTE:
- Get APN settings from provider
- Update config.yaml with APN
- Test LTE connection

6. Install System Service:
```bash
sudo cp barrier-monitor.service /etc/systemd/system/
sudo cp barrier-monitor-maintenance.service /etc/systemd/system/
sudo cp barrier-monitor-maintenance.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable barrier-monitor
sudo systemctl enable barrier-monitor-maintenance.timer
```

## First-Time Setup

1. Initialize OAuth Flow:
```bash
python3 setup_oauth.py
```

2. Test Notifications:
```bash
python3 test_notifications.py
```

3. Verify LTE Connection:
```bash
python3 test_lte.py
```

4. Test GPIO Monitoring:
```bash
python3 test_circuits.py
```

## Common Setup Issues

### Email Notifications
- OAuth token not generated
- Incorrect credentials path
- Missing required scopes
- Gmail API not enabled

### LTE Connection
- Incorrect APN settings
- SIM card not activated
- Poor signal strength
- Serial port permissions

### GPIO Monitoring
- Permission issues
- Incorrect pin numbers
- Missing pull-up resistors
- Wiring issues

## Required Files Checklist
- [ ] monitor.py
- [ ] circuit_monitor.py
- [ ] lte_handler.py
- [ ] maintenance.py
- [ ] config.yaml
- [ ] credentials.json
- [ ] requirements.txt
- [ ] barrier-monitor.service
- [ ] barrier-monitor-maintenance.service
- [ ] barrier-monitor-maintenance.timer

## Testing Procedure
1. Start with power off
2. Connect all circuits
3. Power up system
4. Check LED indicators
5. Test each circuit
6. Verify notifications
7. Monitor system logs

## Verification Commands
```bash
# Check service status
sudo systemctl status barrier-monitor

# View logs
sudo journalctl -u barrier-monitor -f

# Test GPIO readings
gpio readall

# Check LTE connection
mmcli -m 0

# Verify database
sqlite3 /var/lib/barrier-monitor/history.db ".tables"
```
