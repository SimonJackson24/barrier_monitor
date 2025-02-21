"""Test cases for SMS notification functionality"""
import unittest
from unittest.mock import patch, MagicMock
from sms_handler import SMSHandler
import serial

class TestSMSHandler(unittest.TestCase):
    def setUp(self):
        self.sms = SMSHandler()
        self.mock_serial = MagicMock(spec=serial.Serial)
        self.sms.modem = self.mock_serial

    def test_send_sms_success(self):
        self.mock_serial.write.return_value = None
        self.mock_serial.readline.side_effect = [
            b'OK\r\n',  # AT
            b'OK\r\n',  # AT+CMGF=1
            b'OK\r\n',  # AT+CMGS
            b'> ',      # Prompt for message
            b'OK\r\n'   # Message sent
        ]

        result = self.sms.send_sms('+1234567890', 'Test message')
        self.assertTrue(result)
        self.assertEqual(self.mock_serial.write.call_count, 4)

    def test_send_sms_failure_no_signal(self):
        self.mock_serial.write.return_value = None
        self.mock_serial.readline.side_effect = [
            b'OK\r\n',
            b'ERROR\r\n'
        ]

        result = self.sms.send_sms('+1234567890', 'Test message')
        self.assertFalse(result)

    def test_check_signal_strength(self):
        self.mock_serial.write.return_value = None
        self.mock_serial.readline.side_effect = [
            b'OK\r\n',
            b'+CSQ: 20,0\r\n',
            b'OK\r\n'
        ]

        signal = self.sms.check_signal_strength()
        self.assertEqual(signal, 20)

    def test_rate_limiting(self):
        self.sms.last_sent = {}
        messages = ['Test 1', 'Test 2', 'Test 3']
        
        for msg in messages:
            self.sms.send_sms('+1234567890', msg)
            
        self.assertEqual(len(self.sms.last_sent), 1)

if __name__ == '__main__':
    unittest.main()
