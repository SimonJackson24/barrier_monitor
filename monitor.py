"""
Copyright 2025 Automate Systems and Simon Callaghan.

This software was developed by Simon Callaghan during employment at Automate Systems.
All rights reserved. See LICENSE file for details.
"""

#!/usr/bin/env python3

import RPi.GPIO as GPIO
import yaml
import time
import logging
import sys
from datetime import datetime
from pathlib import Path
from email_handler import EmailNotifier
from watchdog_handler import WatchdogHandler
from web_interface import WebInterface, start_web_interface

class BarrierMonitor:
    def __init__(self, config_path="config.yaml"):
        self.setup_logging()
        self.load_config(config_path)
        self.setup_gpio()
        self.email_notifier = EmailNotifier(self.config['email'])
        self.watchdog = WatchdogHandler(self.config['system']['watchdog_timeout_sec'])
        self.last_notification_time = datetime.min
        self.daily_notification_count = 0
        self.last_count_reset = datetime.now()
        self.start_time = time.time()
        
        # Initialize web interface if enabled
        if self.config['web_interface']['enabled']:
            self.web_interface = WebInterface(config_path)
            start_web_interface(
                host=self.config['web_interface']['host'],
                port=self.config['web_interface']['port']
            )
            self.logger.info("Web interface started")

    def setup_logging(self):
        """Configure logging with rotation"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('/var/log/barrier-monitor.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)

    def load_config(self, config_path):
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
            self.logger.info("Configuration loaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            sys.exit(1)

    def setup_gpio(self):
        """Initialize GPIO settings"""
        try:
            GPIO.setmode(GPIO.BCM)
            self.input_pin = self.config['gpio']['input_pin']
            GPIO.setup(
                self.input_pin,
                GPIO.IN,
                pull_up_down=GPIO.PUD_UP if self.config['gpio']['pull_up'] else GPIO.PUD_DOWN
            )
            self.logger.info(f"GPIO initialized on pin {self.input_pin}")
        except Exception as e:
            self.logger.error(f"Failed to initialize GPIO: {e}")
            sys.exit(1)

    def can_send_notification(self):
        """Check if we can send a notification based on cooldown and daily limit"""
        now = datetime.now()
        
        # Reset daily counter if it's past reset time
        reset_time = datetime.strptime(self.config['monitoring']['reset_time'], "%H:%M").time()
        if now.time() < reset_time and self.last_count_reset.time() > reset_time:
            self.daily_notification_count = 0
            self.last_count_reset = now

        # Check cooldown and daily limit
        cooldown_ok = (now - self.last_notification_time).total_seconds() >= \
                     (self.config['monitoring']['notification_cooldown_min'] * 60)
        daily_limit_ok = self.daily_notification_count < self.config['monitoring']['max_daily_notifications']
        
        return cooldown_ok and daily_limit_ok

    def update_system_status(self):
        """Update system status for web interface"""
        if hasattr(self, 'web_interface'):
            uptime = int(time.time() - self.start_time)
            self.web_interface.update_system_status(
                status="Running",
                uptime=uptime,
                notification_count=self.daily_notification_count
            )

    def log_barrier_event(self, event_type, duration, description):
        """Log barrier event to historical data"""
        if hasattr(self, 'web_interface'):
            self.web_interface.log_event(event_type, duration, description)

    def monitor_barrier(self):
        """Main monitoring loop"""
        self.logger.info("Starting barrier monitoring")
        last_state = GPIO.input(self.input_pin)
        state_change_time = None
        last_status_update = time.time()

        try:
            while True:
                self.watchdog.pet()
                current_state = GPIO.input(self.input_pin)
                
                # Update system status periodically
                if time.time() - last_status_update >= 5:
                    self.update_system_status()
                    last_status_update = time.time()
                
                # State has changed
                if current_state != last_state:
                    if current_state == (0 if self.config['gpio']['active_low'] else 1):
                        # Barrier potentially stuck open
                        state_change_time = time.time()
                        self.log_barrier_event(
                            "BARRIER_OPENED",
                            0,
                            "Barrier state changed to open"
                        )
                    else:
                        # Barrier closed
                        if state_change_time:
                            duration = int(time.time() - state_change_time)
                            self.log_barrier_event(
                                "BARRIER_CLOSED",
                                duration,
                                f"Barrier closed after {duration} seconds"
                            )
                        state_change_time = None
                    last_state = current_state

                # Check if barrier has been open too long
                if state_change_time and \
                   (time.time() - state_change_time) > self.config['monitoring']['photocell_timeout_sec']:
                    if self.can_send_notification():
                        self.logger.warning("Barrier potentially stuck open - sending notification")
                        duration = int(time.time() - state_change_time)
                        self.email_notifier.send_alert(
                            "Barrier Alert",
                            f"Barrier has been open for more than "
                            f"{self.config['monitoring']['photocell_timeout_sec']} seconds."
                        )
                        self.log_barrier_event(
                            "ALERT_SENT",
                            duration,
                            "Notification sent for extended open state"
                        )
                        self.last_notification_time = datetime.now()
                        self.daily_notification_count += 1
                        state_change_time = time.time()  # Reset timer to prevent spam

                time.sleep(self.config['monitoring']['check_interval_ms'] / 1000)

        except KeyboardInterrupt:
            self.logger.info("Monitoring stopped by user")
        except Exception as e:
            self.logger.error(f"Monitoring error: {e}")
        finally:
            GPIO.cleanup()

if __name__ == "__main__":
    monitor = BarrierMonitor()
    monitor.monitor_barrier()
