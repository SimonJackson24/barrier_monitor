#!/usr/bin/env python3

import unittest
import sys
import os
import yaml
import RPi.GPIO as GPIO
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from monitor import BarrierMonitor
from email_handler import EmailNotifier
from watchdog_handler import WatchdogHandler

class TestBarrierMonitor(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.config_path = "../config.yaml"
        with open(self.config_path, 'r') as f:
            self.config = yaml.safe_load(f)
    
    def tearDown(self):
        """Clean up after tests"""
        GPIO.cleanup()

    def test_config_loading(self):
        """Test configuration loading"""
        monitor = BarrierMonitor(self.config_path)
        self.assertIsNotNone(monitor.config)
        self.assertIn('gpio', monitor.config)
        self.assertIn('email', monitor.config)
        self.assertIn('monitoring', monitor.config)

    def test_gpio_setup(self):
        """Test GPIO initialization"""
        monitor = BarrierMonitor(self.config_path)
        pin_state = GPIO.input(monitor.input_pin)
        self.assertIn(pin_state, [0, 1])

    def test_notification_cooldown(self):
        """Test notification cooldown logic"""
        monitor = BarrierMonitor(self.config_path)
        
        # Should be able to send first notification
        self.assertTrue(monitor.can_send_notification())
        
        # Simulate sending notification
        monitor.last_notification_time = time.time()
        monitor.daily_notification_count += 1
        
        # Should not be able to send notification during cooldown
        self.assertFalse(monitor.can_send_notification())

    def test_watchdog(self):
        """Test watchdog functionality"""
        watchdog = WatchdogHandler(timeout_seconds=2)
        
        # Should not timeout when properly pet
        watchdog.pet()
        time.sleep(1)
        self.assertTrue(watchdog.running)
        
        watchdog.stop()

    @unittest.skipIf(not os.path.exists('../credentials.json'), 
                    "Skipping email test - credentials.json not found")
    def test_email_notification(self):
        """Test email notification system"""
        notifier = EmailNotifier(self.config['email'])
        success = notifier.send_alert(
            "Test Alert",
            "This is a test message from the unit tests."
        )
        self.assertTrue(success)

def main():
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestBarrierMonitor)
    
    # Run tests
    print("\nRunning Barrier Monitor Tests")
    print("-" * 50)
    unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == "__main__":
    main()
