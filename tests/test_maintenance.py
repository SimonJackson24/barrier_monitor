"""Test cases for database maintenance functionality"""
import unittest
from unittest.mock import patch, MagicMock, mock_open
import sqlite3
import os
from datetime import datetime, timedelta
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from maintenance import DatabaseMaintenance

class TestDatabaseMaintenance(unittest.TestCase):
    def setUp(self):
        self.config = {
            'historical_data': {
                'database_path': '/var/lib/barrier-monitor/history.db',
                'backup_path': '/var/backup/barrier-monitor',
                'retention_days': 30
            }
        }
        
        # Mock config file
        self.mock_config = mock_open(read_data="""
            historical_data:
                database_path: "/var/lib/barrier-monitor/history.db"
                backup_path: "/var/backup/barrier-monitor"
                retention_days: 30
        """)

    @patch('builtins.open', new_callable=mock_open)
    @patch('yaml.safe_load')
    def test_config_loading(self, mock_yaml, mock_file):
        """Test configuration loading"""
        mock_yaml.return_value = self.config
        maintenance = DatabaseMaintenance()
        self.assertEqual(
            maintenance.config['historical_data']['retention_days'],
            30
        )

    @patch('sqlite3.connect')
    def test_cleanup_old_data(self, mock_connect):
        """Test old data cleanup"""
        mock_cursor = MagicMock()
        mock_connect.return_value.__enter__.return_value = mock_cursor
        
        maintenance = DatabaseMaintenance()
        maintenance.config = self.config
        
        result = maintenance.cleanup_old_data()
        self.assertTrue(result)
        
        # Verify correct SQL executed
        cutoff_date = datetime.now() - timedelta(days=30)
        mock_cursor.execute.assert_any_call(
            "DELETE FROM events WHERE timestamp < ?",
            (cutoff_date.isoformat(),)
        )

    @patch('sqlite3.connect')
    @patch('subprocess.run')
    @patch('pathlib.Path.mkdir')
    def test_backup_database(self, mock_mkdir, mock_run, mock_connect):
        """Test database backup creation"""
        maintenance = DatabaseMaintenance()
        maintenance.config = self.config
        
        result = maintenance.backup_database()
        self.assertTrue(result)
        
        # Verify backup directory created
        mock_mkdir.assert_called_with(parents=True, exist_ok=True)
        
        # Verify gzip called
        mock_run.assert_called_once()
        self.assertTrue('gzip' in mock_run.call_args[0][0])

    @patch('os.statvfs')
    def test_disk_space_check(self, mock_statvfs):
        """Test disk space checking"""
        mock_stat = MagicMock()
        mock_stat.f_bavail = 1000000  # Simulate plenty of space
        mock_stat.f_frsize = 4096
        mock_statvfs.return_value = mock_stat
        
        maintenance = DatabaseMaintenance()
        maintenance.config = self.config
        
        space_info = maintenance.check_disk_space()
        self.assertIsNotNone(space_info)
        self.assertTrue(space_info['database_free_gb'] > 0)
        self.assertTrue(space_info['backup_free_gb'] > 0)

    @patch('sqlite3.connect')
    def test_optimize_database(self, mock_connect):
        """Test database optimization"""
        mock_cursor = MagicMock()
        mock_connect.return_value.__enter__.return_value = mock_cursor
        
        maintenance = DatabaseMaintenance()
        maintenance.config = self.config
        
        result = maintenance.optimize_database()
        self.assertTrue(result)
        
        # Verify optimization commands executed
        mock_cursor.execute.assert_any_call("ANALYZE")
        mock_cursor.execute.assert_any_call("REINDEX")
        mock_cursor.execute.assert_any_call("VACUUM")

    @patch('sqlite3.connect')
    def test_error_handling(self, mock_connect):
        """Test error handling during maintenance"""
        mock_connect.side_effect = sqlite3.Error("Test error")
        
        maintenance = DatabaseMaintenance()
        maintenance.config = self.config
        
        result = maintenance.cleanup_old_data()
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()
