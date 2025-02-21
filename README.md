# Barrier System Monitor

A Raspberry Pi-based monitoring solution for automated barrier systems that detects potential failures and sends email notifications when issues are detected.

## Quick Start

1. Clone this repository:
```bash
git clone https://github.com/yourusername/barrier_monitor.git
cd barrier_monitor
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your settings in `config.yaml`:
```yaml
email:
  sender: your-email@gmail.com
  recipients:
    - recipient1@example.com
    - recipient2@example.com

monitoring:
  check_interval_ms: 100
  photocell_timeout_sec: 30
  notification_cooldown_min: 5
```

4. Set up the systemd service:
```bash
sudo cp barrier-monitor.service /etc/systemd/system/
sudo systemctl enable barrier-monitor
sudo systemctl start barrier-monitor
```

## Hardware Setup

#### Safety First! 
Before starting any wiring:
1. **ALWAYS** ensure your Raspberry Pi is completely powered off and unplugged
2. Avoid working in wet or damp conditions
3. If you're unsure about anything, consult a qualified electrician

#### Components Required
- Raspberry Pi (3B+ or newer recommended)
- Clipper LTE mini HAT
- NC (Normally Closed) photocell circuits
- Power supply (5V/2.5A minimum)
- Female-to-female jumper wires (at least 2)
- Small Phillips head screwdriver
- Optional: multimeter for testing connections

#### Wiring Instructions

##### Step 1: Locate the GPIO Pins
1. With your Raspberry Pi powered off, locate the GPIO pins
2. The GPIO pins are the two rows of pins on the board
3. We'll be using:
   - GPIO17 (Physical pin 11) for the photocell input
   - Any Ground pin (Physical pins 6, 9, 14, 20, 25, 30, 34, or 39)

##### Step 2: Connect the Photocell
Your photocell should have two wires:
- One wire for signal (usually black or white)
- One wire for ground (usually black)

Follow these steps:
1. Connect the signal wire to GPIO17 (Physical pin 11)
   - Use a female-to-female jumper wire
   - The connection should be firm but don't force it

2. Connect the ground wire to any ground pin
   - We recommend using Physical pin 9 (ground)
   - Again, use a female-to-female jumper wire
   - The connection should be snug

```
                    [Raspberry Pi GPIO Header]
                    ┌──────────────────────────┐
                    │ ○  1    2  ○            │
                    │ ○  3    4  ○            │
                    │ ○  5    6  ○[G]         │ <-- Ground (Pin 6)
                    │ ○  7    8  ○            │
                    │ ○[G]9   10  ○          │ <-- Alternative Ground (Pin 9)
Signal (GPIO17) --> │[S]○ 11  12  ○          │
                    │ ○  13   14[G]○          │ <-- Another Ground option (Pin 14)
                    │ ○  15   16  ○            │
                    │ ○  17   18  ○            │
                    │ ○  19   20[G]○          │ <-- Another Ground option (Pin 20)
                    │ ○  21   22  ○            │
                    │ ○  23   24  ○            │
                    │ ○[G]25  26  ○          │ <-- Another Ground option (Pin 25)
                    │ ○  27   28  ○            │
                    │ ○  29   30[G]○          │ <-- Another Ground option (Pin 30)
                    │ ○  31   32  ○            │
                    │ ○  33   34[G]○          │ <-- Another Ground option (Pin 34)
                    │ ○  35   36  ○            │
                    │ ○  37   38  ○            │
                    │ ○[G]39  40  ○          │ <-- Another Ground option (Pin 39)
                    └──────────────────────────┘
Legend:
○ = Pin
[G] = Ground Pin (any can be used)
[S] = Signal Pin (GPIO17, Physical Pin 11)
```

##### Step 3: Verify Connections
Before powering on:
1. Double-check all connections match the diagram
2. Ensure no bare wires are touching each other
3. Verify jumper wires are firmly connected

##### Step 4: Testing
1. Power on your Raspberry Pi
2. Open a terminal and run:
```bash
python3 -c "import RPi.GPIO as GPIO; GPIO.setmode(GPIO.BCM); GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP); print(GPIO.input(17))"
```
3. This should print:
   - `1` when the photocell beam is unbroken
   - `0` when the beam is broken

#### Troubleshooting Common Wiring Issues
- **No response when testing:**
  - Check if jumper wires are fully inserted
  - Try a different ground pin
  - Verify photocell is working with a multimeter

- **Inconsistent readings:**
  - Check for loose connections
  - Ensure photocell is properly aligned
  - Verify no interference from bright light sources

#### Safety Notes
- Never connect or disconnect wires while the Pi is powered on
- Keep all connections away from metal objects
- If you smell burning or see smoke, immediately unplug the Pi
- Don't expose the connections to water or moisture

## Hardware Installation

### Required Components
- Raspberry Pi (3B+ or newer recommended)
- Clipper LTE mini HAT
- NC (Normally Closed) photocell circuits
- 10kΩ pull-up resistors
- Terminal blocks for connections
- Shielded cable for long runs
- Cellular antenna
- Active SIM card with data plan

### Wiring Instructions
For quick installation, see [QUICK_WIRING.md](docs/QUICK_WIRING.md) (5-minute guide).

For detailed instructions, see [WIRING.md](docs/WIRING.md). This includes:
- LTE HAT installation and connections
- Barrier circuit wiring diagrams
- Cable specifications
- Grounding requirements
- Testing procedures
- Troubleshooting guide

⚠️ **Important**: Follow all safety precautions in the wiring guide.

## LTE Connectivity

### Hardware Setup

#### Clipper LTE Mini HAT Installation
1. Connect the Clipper LTE mini HAT to your Raspberry Pi's GPIO pins
2. Ensure the HAT is properly seated and secured
3. Connect the cellular antenna to the SMA connector
4. Insert a compatible SIM card with data plan

#### Physical Connections
```
Clipper LTE Mini HAT -> Raspberry Pi
TX (Pin 8)  -> RX (GPIO 15)
RX (Pin 10) -> TX (GPIO 14)
GND         -> GND
VCC         -> 3.3V
```

### Software Configuration

#### LTE Settings
Configure LTE parameters in `config.yaml`:
```yaml
lte:
  enabled: true
  serial_port: "/dev/ttyUSB0"    # Serial port for LTE HAT
  baud_rate: 115200              # Baud rate for serial communication
  apn: "internet"                # Your provider's APN
  set_default_route: false       # Use LTE as default route
```

#### Network Failover
The system supports automatic WiFi -> LTE failover:
```yaml
lte:
  failover:
    enabled: true               # Enable failover
    ping_host: "8.8.8.8"       # Connection test host
    ping_interval: 30          # Check interval
    max_failures: 3            # Failures before failover
```

### Testing LTE Connection

1. Check signal strength:
```bash
sudo python3 -c "from lte_handler import LTEHandler; handler = LTEHandler({}); print(handler._check_signal_quality())"
```

2. Test connection:
```bash
sudo python3 -c "from lte_handler import LTEHandler; handler = LTEHandler({}); print(handler.check_connection())"
```

### Troubleshooting LTE

#### Common Issues
1. No Serial Port
   - Check if HAT is properly seated
   - Verify serial port permissions
   - Run: `sudo chmod 666 /dev/ttyUSB0`

2. Connection Failures
   - Verify SIM card is activated
   - Check APN settings
   - Ensure antenna is connected
   - Check signal strength

3. Poor Signal
   - Reposition antenna
   - Use signal strength LED indicators
   - Consider external antenna

#### LED Indicators
- PWR: Power status
- NET: Network registration
- SIG: Signal strength
  - Slow blink: Weak signal
  - Fast blink: Strong signal
- ACT: Data activity

## Configuration

### GPIO Settings
- Default input pin: GPIO17 (configurable in config.yaml)
- Pull-up resistor enabled by default

### Email Settings
The system uses Gmail API for sending notifications. You'll need to:
1. Create a Google Cloud Project
2. Enable Gmail API
3. Create credentials (OAuth 2.0)
4. Save the credentials file as `credentials.json`

## New Features

### Multiple Circuit Monitoring
The system now supports monitoring multiple barrier circuits simultaneously:
- Individual configuration per circuit
- Separate state tracking and notifications
- Threaded monitoring for optimal performance
- Circuit-specific notification settings

Configuration example:
```yaml
circuits:
  main_entrance:
    gpio_pin: 17
    description: "Main Entrance Barrier"
    timeout_sec: 30
  rear_exit:
    gpio_pin: 27
    description: "Rear Exit Barrier"
    timeout_sec: 30
```

### Remote Configuration API
Secure API for remote system configuration:
- REST API endpoints for configuration management
- API key authentication
- IP-based access control
- Configuration backup system
- Validation and safety checks

API Endpoints:
- GET /api/v1/config - Retrieve current configuration
- PUT /api/v1/config - Update configuration
- GET /api/v1/circuits - List circuit status
- PUT /api/v1/circuits/{id} - Update circuit configuration

### Database Maintenance
Automated maintenance system for optimal performance:
- Daily data cleanup based on retention policy
- Database optimization
- Automated backups
- Disk space monitoring
- Systemd service integration

Maintenance tasks run daily via systemd timer. Configure retention and backup settings in config.yaml.

## Detailed Feature Documentation

### Circuit Monitoring System

#### Circuit States
The system tracks the following states for each circuit:
- Normal: Circuit is closed and operating normally
- Alert: Circuit has been open beyond the timeout period
- Error: System unable to read circuit state
- Disabled: Circuit monitoring temporarily disabled

#### Circuit Configuration
Each circuit can be configured with:
```yaml
circuits:
  circuit_name:
    gpio_pin: 17              # GPIO pin number
    timeout_sec: 30           # Alert timeout
    pull_up: true            # Use internal pull-up
    active_low: true         # Trigger on low signal
    check_interval_ms: 100   # Polling interval
    description: "Circuit"    # Human-readable name
    notification:
      cooldown_min: 5        # Minutes between notifications
      max_daily: 50          # Max notifications per day
      reset_time: "00:00"    # Daily counter reset time
```

### Notification System

#### Email Configuration
```yaml
email:
  enabled: true
  sender: "your-email@gmail.com"
  recipients: ["recipient@example.com"]
  templates:
    alert: "Alert: {circuit} {state}"
    restore: "Restored: {circuit}"
```

#### Rate Limiting
- Per-circuit cooldown periods
- Daily notification limits
- Automatic reset at configured time
- Separate counters for email

### Remote Configuration API

#### Authentication
- API key authentication required
- IP-based access control
- HTTPS required in production
- Rate limiting per IP

#### API Endpoints

##### GET /api/v1/config
Returns current configuration:
```json
{
  "circuits": {...},
  "notifications": {...},
  "monitoring": {...}
}
```

##### PUT /api/v1/config
Update system configuration:
```json
{
  "circuits": {
    "main_entrance": {
      "gpio_pin": 17,
      "timeout_sec": 30
    }
  }
}
```

##### GET /api/v1/circuits
Get circuit status:
```json
{
  "main_entrance": {
    "state": "normal",
    "last_alert": "2025-02-21T10:30:00Z",
    "notifications_today": 5
  }
}
```

### Database Management

#### Data Retention
- Configurable retention period
- Automatic cleanup of old records
- Backup before cleanup
- Storage space monitoring

#### Backup System
- Daily automated backups
- Compressed backup files
- Configurable backup retention
- Backup rotation

#### Optimization
- Regular index optimization
- Database vacuuming
- Performance monitoring
- Error recovery

### Testing

#### Unit Tests
- Individual component testing
- Mock external dependencies
- Error condition testing
- Configuration validation

#### Integration Tests
- Cross-component testing
- End-to-end workflows
- Concurrent operation testing
- Error recovery testing

## Troubleshooting

### Common Issues
1. **No Email Notifications**
   - Check Gmail API credentials
   - Verify internet connectivity
   - Check email configuration in config.yaml

2. **False Positives**
   - Adjust photocell_timeout_sec in config
   - Check photocell alignment
   - Verify wiring connections

3. **Service Not Starting**
   - Check system logs: `journalctl -u barrier-monitor`
   - Verify Python dependencies
   - Check file permissions

## Support

For issues and feature requests, please create an issue in the GitHub repository.

## License & Ownership

Copyright 2025 Automate Systems and Simon Callaghan.

This software was developed by Simon Callaghan during employment at Automate Systems. The intellectual property rights are held jointly by Automate Systems and Simon Callaghan, with specific conditions:

- Automate Systems holds exclusive commercial rights
- Simon Callaghan is credited as the original creator and developer
- Usage, modification, and distribution require written consent from both parties
- Internal use within Automate Systems is permitted without restriction

For complete license terms and conditions, please see the [LICENSE](LICENSE) file.

For licensing inquiries and permissions, please contact Automate Systems.

## Project Status

### Completed Features
- ✅ Multiple circuit monitoring
- ✅ Remote configuration API
- ✅ Database maintenance
- ✅ Comprehensive testing
- ✅ Documentation

### In Progress
- 🔄 Performance optimization
- 🔄 Additional notification channels
- 🔄 Enhanced reporting features

### Planned Features
- 📋 Machine learning anomaly detection
- 📋 Mobile application
- 📋 Advanced analytics dashboard
