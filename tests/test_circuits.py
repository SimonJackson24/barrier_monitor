"""Test cases for multiple circuit monitoring functionality"""
import unittest
from unittest.mock import patch, MagicMock
import threading
import time
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from circuit_monitor import CircuitMonitor

class TestCircuitMonitor(unittest.TestCase):
    def setUp(self):
        self.config = {
            'circuits': {
                'main_entrance': {
                    'gpio_pin': 17,
                    'timeout_sec': 30,
                    'notification_cooldown_min': 5,
                    'max_daily_notifications': 50,
                    'pull_up': True,
                    'active_low': True,
                    'check_interval_ms': 100,
                    'description': "Main Entrance Barrier"
                }
            }
        }

    @patch('RPi.GPIO')
    def test_circuit_initialization(self, mock_gpio):
        """Test circuit initialization"""
        monitor = CircuitMonitor(self.config)
        self.assertEqual(len(monitor.circuits), 1)
        mock_gpio.setup.assert_called_once_with(
            17, mock_gpio.IN, pull_up_down=mock_gpio.PUD_UP
        )

    @patch('RPi.GPIO')
    def test_circuit_state_change(self, mock_gpio):
        """Test circuit state change detection"""
        monitor = CircuitMonitor(self.config)
        
        # Simulate state change
        mock_gpio.input.return_value = False
        monitor.check_circuit('main_entrance')
        self.assertTrue(monitor.circuits['main_entrance']['alert_active'])

    @patch('RPi.GPIO')
    def test_multiple_circuits(self, mock_gpio):
        """Test monitoring multiple circuits"""
        self.config['circuits']['rear_exit'] = {
            'gpio_pin': 27,
            'timeout_sec': 30,
            'notification_cooldown_min': 5,
            'max_daily_notifications': 50,
            'pull_up': True,
            'active_low': True,
            'check_interval_ms': 100,
            'description': "Rear Exit Barrier"
        }
        
        monitor = CircuitMonitor(self.config)
        self.assertEqual(len(monitor.circuits), 2)
        
        # Test independent state tracking
        mock_gpio.input.side_effect = [False, True]  # main_entrance triggered, rear_exit normal
        monitor.check_circuit('main_entrance')
        monitor.check_circuit('rear_exit')
        
        self.assertTrue(monitor.circuits['main_entrance']['alert_active'])
        self.assertFalse(monitor.circuits['rear_exit']['alert_active'])

    @patch('RPi.GPIO')
    def test_notification_cooldown(self, mock_gpio):
        """Test notification cooldown per circuit"""
        monitor = CircuitMonitor(self.config)
        
        # First alert should trigger notification
        mock_gpio.input.return_value = False
        result1 = monitor.check_circuit('main_entrance')
        self.assertTrue(result1['should_notify'])
        
        # Second alert within cooldown should not notify
        result2 = monitor.check_circuit('main_entrance')
        self.assertFalse(result2['should_notify'])

    @patch('RPi.GPIO')
    def test_daily_notification_limit(self, mock_gpio):
        """Test daily notification limit per circuit"""
        monitor = CircuitMonitor(self.config)
        mock_gpio.input.return_value = False
        
        # Exceed daily limit
        for _ in range(51):
            monitor.circuits['main_entrance']['notification_count'] += 1
        
        result = monitor.check_circuit('main_entrance')
        self.assertFalse(result['should_notify'])

    @patch('RPi.GPIO')
    def test_thread_safety(self, mock_gpio):
        """Test thread safety of circuit monitoring"""
        monitor = CircuitMonitor(self.config)
        
        def simulate_checks():
            for _ in range(100):
                monitor.check_circuit('main_entrance')
                time.sleep(0.001)
        
        threads = [
            threading.Thread(target=simulate_checks)
            for _ in range(5)
        ]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # No exceptions should be raised

if __name__ == '__main__':
    unittest.main()
