"""Integration tests for the barrier monitoring system"""
import unittest
from unittest.mock import patch, MagicMock
import serial
from monitor import BarrierMonitor

class TestBarrierMonitorIntegration(unittest.TestCase):
    def setUp(self):
        self.config = {
            'monitoring': {
                'check_interval': 1,
                'max_daily_notifications': 10,
                'notification_cooldown': 300
            },
            'circuits': {
                'main_entrance': {
                    'gpio_pin': 17,
                    'name': 'Main Entrance'
                },
                'exit_gate': {
                    'gpio_pin': 27,
                    'name': 'Exit Gate'
                }
            },
            'notifications': {
                'enabled': True,
                'recipients': ['+1234567890']
            },
            'lte': {
                'port': '/dev/ttyUSB0',
                'baud': 115200,
                'pin': None
            }
        }
        
        self.monitor = BarrierMonitor(self.config)
        
    def test_full_notification_flow(self):
        """Test complete notification flow when circuit breaks"""
        with patch('RPi.GPIO') as mock_gpio, \
             patch('serial.Serial') as mock_serial:
            
            # Setup GPIO mock
            mock_gpio.input.return_value = True  # Circuit broken
            
            # Setup Serial mock for LTE
            mock_serial.return_value.write.return_value = None
            mock_serial.return_value.readline.side_effect = [
                b'OK\r\n',
                b'OK\r\n',
                b'> ',
                b'OK\r\n'
            ]
            
            # Run one monitoring cycle
            self.monitor.check_circuits()
            
            # Verify notifications were sent
            self.assertTrue(mock_serial.return_value.write.called)
            self.assertEqual(
                mock_serial.return_value.write.call_count,
                4  # AT, CMGF, CMGS, message
            )
            
    def test_rate_limiting(self):
        """Test notification rate limiting across multiple circuits"""
        with patch('RPi.GPIO') as mock_gpio, \
             patch('serial.Serial') as mock_serial:
            
            # Setup mocks
            mock_gpio.input.return_value = True
            mock_serial.return_value.write.return_value = None
            mock_serial.return_value.readline.return_value = b'OK\r\n'
            
            # Trigger max notifications
            for _ in range(self.config['monitoring']['max_daily_notifications']):
                self.monitor.check_circuits()
            
            # Reset call counts
            mock_serial.return_value.write.reset_mock()
            
            # This should not send due to rate limiting
            self.monitor.check_circuits()
            self.assertFalse(mock_serial.return_value.write.called)
            
    def test_system_recovery(self):
        """Test system behavior when circuit recovers"""
        with patch('RPi.GPIO'), patch('serial.Serial'):
            # Simulate circuit break
            self.monitor.circuit_status['main_entrance'] = False
            
            # Simulate recovery
            self.monitor.handle_circuit_recovery('main_entrance')
            
            self.assertTrue(self.monitor.circuit_status['main_entrance'])
            
    def test_gpio_setup(self):
        """Test GPIO initialization"""
        with patch('RPi.GPIO') as mock_gpio:
            monitor = BarrierMonitor(self.config)
            
            # Verify GPIO setup
            self.assertEqual(
                mock_gpio.setup.call_count,
                len(self.config['circuits'])
            )
            
if __name__ == '__main__':
    unittest.main()
