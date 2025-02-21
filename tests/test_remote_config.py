"""Test cases for remote configuration API functionality"""
import unittest
from unittest.mock import patch, MagicMock
import json
import yaml
import sys
from pathlib import Path
from ipaddress import ip_network, ip_address

sys.path.append(str(Path(__file__).parent.parent))
from remote_config import RemoteConfigAPI

class TestRemoteConfigAPI(unittest.TestCase):
    def setUp(self):
        self.config = {
            'remote_config': {
                'enabled': True,
                'api_key': 'test_api_key',
                'allowed_ips': ['192.168.1.0/24', '10.0.0.0/8'],
                'backup_enabled': True,
                'backup_count': 10,
                'backup_path': '/var/backup/barrier-monitor/config'
            }
        }
        self.api = RemoteConfigAPI(self.config)

    def test_api_key_validation(self):
        """Test API key validation"""
        self.assertTrue(
            self.api.validate_api_key('test_api_key')
        )
        self.assertFalse(
            self.api.validate_api_key('wrong_key')
        )

    def test_ip_validation(self):
        """Test IP address validation"""
        valid_ips = [
            '192.168.1.100',
            '10.0.0.50'
        ]
        invalid_ips = [
            '172.16.0.1',
            '8.8.8.8'
        ]
        
        for ip in valid_ips:
            self.assertTrue(
                self.api.validate_ip(ip)
            )
        
        for ip in invalid_ips:
            self.assertFalse(
                self.api.validate_ip(ip)
            )

    @patch('pathlib.Path.write_text')
    @patch('pathlib.Path.exists')
    def test_config_backup(self, mock_exists, mock_write):
        """Test configuration backup"""
        mock_exists.return_value = True
        
        result = self.api.backup_config()
        self.assertTrue(result)
        mock_write.assert_called_once()

    def test_config_validation(self):
        """Test configuration validation"""
        valid_config = {
            'circuits': {
                'main_entrance': {
                    'gpio_pin': 17,
                    'timeout_sec': 30
                }
            }
        }
        invalid_config = {
            'circuits': {
                'main_entrance': {
                    'gpio_pin': 'invalid',
                    'timeout_sec': -1
                }
            }
        }
        
        self.assertTrue(
            self.api.validate_config(valid_config)
        )
        self.assertFalse(
            self.api.validate_config(invalid_config)
        )

    @patch('yaml.safe_dump')
    def test_config_update(self, mock_yaml_dump):
        """Test configuration update"""
        new_config = {
            'circuits': {
                'main_entrance': {
                    'gpio_pin': 18,
                    'timeout_sec': 45
                }
            }
        }
        
        result = self.api.update_config(new_config)
        self.assertTrue(result)
        mock_yaml_dump.assert_called_once()

    def test_circuit_validation(self):
        """Test circuit configuration validation"""
        valid_circuit = {
            'gpio_pin': 17,
            'timeout_sec': 30,
            'notification_cooldown_min': 5,
            'max_daily_notifications': 50,
            'pull_up': True,
            'active_low': True
        }
        invalid_circuit = {
            'gpio_pin': -1,
            'timeout_sec': 'invalid',
            'notification_cooldown_min': -5
        }
        
        self.assertTrue(
            self.api.validate_circuit_config(valid_circuit)
        )
        self.assertFalse(
            self.api.validate_circuit_config(invalid_circuit)
        )

    @patch('yaml.safe_dump')
    def test_circuit_update(self, mock_yaml_dump):
        """Test circuit configuration update"""
        circuit_id = 'main_entrance'
        new_config = {
            'gpio_pin': 18,
            'timeout_sec': 45
        }
        
        result = self.api.update_circuit(circuit_id, new_config)
        self.assertTrue(result)
        mock_yaml_dump.assert_called_once()

    def test_disabled_api(self):
        """Test behavior when API is disabled"""
        self.config['remote_config']['enabled'] = False
        api = RemoteConfigAPI(self.config)
        
        result = api.update_config({'test': 'config'})
        self.assertFalse(result)

    @patch('pathlib.Path.exists')
    def test_backup_rotation(self, mock_exists):
        """Test backup file rotation"""
        mock_exists.return_value = True
        
        # Create more backups than allowed
        for i in range(15):
            self.api.backup_config()
        
        # Verify old backups were cleaned up
        self.assertEqual(
            len(list(Path(self.config['remote_config']['backup_path']).glob('*.yaml'))),
            self.config['remote_config']['backup_count']
        )

if __name__ == '__main__':
    unittest.main()
