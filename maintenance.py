"""
Copyright © 2025 Automate Systems and Simon Callaghan.

This software was developed by Simon Callaghan during employment at Automate Systems.
All rights reserved. See LICENSE file for details.
"""

#!/usr/bin/env python3

import sqlite3
import logging
import yaml
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import subprocess
import os

class DatabaseMaintenance:
    def __init__(self, config_path="config.yaml"):
        self.logger = logging.getLogger(__name__)
        self.load_config(config_path)
        self.setup_logging()

    def setup_logging(self):
        """Configure logging"""
        log_file = Path("/var/log/barrier-monitor/maintenance.log")
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )

    def load_config(self, config_path):
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
            self.logger.info("Maintenance configuration loaded")
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            raise

    def cleanup_old_data(self):
        """Remove data older than retention period"""
        try:
            retention_days = self.config['historical_data']['retention_days']
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            with sqlite3.connect(self.config['historical_data']['database_path']) as conn:
                # Delete old events
                conn.execute(
                    "DELETE FROM events WHERE timestamp < ?",
                    (cutoff_date.isoformat(),)
                )
                
                # Delete old system status records
                conn.execute(
                    "DELETE FROM system_status WHERE timestamp < ?",
                    (cutoff_date.isoformat(),)
                )
                
                # Vacuum database to reclaim space
                conn.execute("VACUUM")
                
            self.logger.info(f"Cleaned up data older than {retention_days} days")
            return True
        except Exception as e:
            self.logger.error(f"Failed to clean up old data: {e}")
            return False

    def backup_database(self):
        """Create backup of the database"""
        try:
            db_path = Path(self.config['historical_data']['database_path'])
            backup_dir = Path(self.config['historical_data']['backup_path'])
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Create timestamped backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = backup_dir / f"history_{timestamp}.db"
            
            # Create backup using SQLite's backup API
            with sqlite3.connect(db_path) as source:
                with sqlite3.connect(backup_path) as dest:
                    source.backup(dest)
            
            # Compress backup
            subprocess.run(['gzip', str(backup_path)], check=True)
            
            # Keep only last N backups
            backup_files = sorted(backup_dir.glob("history_*.db.gz"))
            max_backups = 5
            if len(backup_files) > max_backups:
                for old_backup in backup_files[:-max_backups]:
                    old_backup.unlink()
            
            self.logger.info(f"Database backed up to {backup_path}.gz")
            return True
        except Exception as e:
            self.logger.error(f"Failed to backup database: {e}")
            return False

    def optimize_database(self):
        """Optimize database performance"""
        try:
            with sqlite3.connect(self.config['historical_data']['database_path']) as conn:
                # Analyze tables for query optimization
                conn.execute("ANALYZE")
                
                # Rebuild indexes
                conn.execute("REINDEX")
                
                # Optimize database
                conn.execute("VACUUM")
                
            self.logger.info("Database optimization completed")
            return True
        except Exception as e:
            self.logger.error(f"Failed to optimize database: {e}")
            return False

    def check_disk_space(self):
        """Check available disk space"""
        try:
            db_path = Path(self.config['historical_data']['database_path'])
            backup_path = Path(self.config['historical_data']['backup_path'])
            
            # Check database directory
            db_stat = os.statvfs(db_path.parent)
            db_free_gb = (db_stat.f_bavail * db_stat.f_frsize) / (1024**3)
            
            # Check backup directory
            backup_stat = os.statvfs(backup_path)
            backup_free_gb = (backup_stat.f_bavail * backup_stat.f_frsize) / (1024**3)
            
            # Alert if less than 1GB free
            if db_free_gb < 1:
                self.logger.warning(f"Low disk space on database directory: {db_free_gb:.2f}GB remaining")
            if backup_free_gb < 1:
                self.logger.warning(f"Low disk space on backup directory: {backup_free_gb:.2f}GB remaining")
            
            return {
                'database_free_gb': db_free_gb,
                'backup_free_gb': backup_free_gb
            }
        except Exception as e:
            self.logger.error(f"Failed to check disk space: {e}")
            return None

def run_maintenance():
    """Run all maintenance tasks"""
    maintenance = DatabaseMaintenance()
    
    # Check disk space first
    space_info = maintenance.check_disk_space()
    if space_info and (space_info['database_free_gb'] > 1 and space_info['backup_free_gb'] > 1):
        # Run maintenance tasks
        maintenance.cleanup_old_data()
        maintenance.optimize_database()
        maintenance.backup_database()
    else:
        maintenance.logger.error("Insufficient disk space for maintenance tasks")

if __name__ == "__main__":
    run_maintenance()
