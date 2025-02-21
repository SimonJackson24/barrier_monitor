"""
Web interface for barrier monitoring system with real-time updates and configuration management
"""

from flask import Flask, render_template, jsonify, request, send_file
from flask_socketio import SocketIO, emit
from datetime import datetime, timedelta
import sqlite3
import yaml
import threading
import logging
import json
from pathlib import Path
import os

app = Flask(__name__)
socketio = SocketIO(app)
logger = logging.getLogger(__name__)

class WebInterface:
    def __init__(self, config_path="config.yaml"):
        self.load_config(config_path)
        self.setup_database()
        self.setup_websocket_events()
        
    def load_config(self, config_path):
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
            logger.info("Web interface configuration loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise

    def setup_database(self):
        """Initialize SQLite database for historical data"""
        db_path = Path("/var/lib/barrier-monitor/history.db")
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(str(db_path)) as conn:
            # Events table for barrier events
            conn.execute('''
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    event_type TEXT,
                    circuit_id TEXT,
                    duration INTEGER,
                    description TEXT
                )
            ''')
            
            # System status table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS system_status (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    status TEXT,
                    uptime INTEGER,
                    notification_count INTEGER,
                    lte_signal INTEGER,
                    cpu_temp REAL,
                    memory_usage REAL
                )
            ''')
            
            # Notifications table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    type TEXT,
                    recipient TEXT,
                    message TEXT,
                    status TEXT
                )
            ''')

    def setup_websocket_events(self):
        """Setup WebSocket event handlers"""
        @socketio.on('connect')
        def handle_connect():
            logger.info("Client connected to WebSocket")
            self.send_initial_data()
        
        @socketio.on('disconnect')
        def handle_disconnect():
            logger.info("Client disconnected from WebSocket")
    
    def send_initial_data(self):
        """Send initial data to newly connected clients"""
        emit('system_status', self.get_system_status())
        emit('circuit_status', self.get_circuit_status())
        emit('recent_events', self.get_recent_events(10))

    def log_event(self, event_type, circuit_id, duration, description):
        """Log a barrier event to the database"""
        try:
            with sqlite3.connect("/var/lib/barrier-monitor/history.db") as conn:
                conn.execute(
                    "INSERT INTO events (event_type, circuit_id, duration, description) VALUES (?, ?, ?, ?)",
                    (event_type, circuit_id, duration, description)
                )
            
            # Emit event to connected clients
            event_data = {
                'timestamp': datetime.now().isoformat(),
                'event_type': event_type,
                'circuit_id': circuit_id,
                'duration': duration,
                'description': description
            }
            socketio.emit('new_event', event_data)
            
            logger.info(f"Event logged: {event_type}")
        except Exception as e:
            logger.error(f"Failed to log event: {e}")

    def update_system_status(self, status, uptime, notification_count, lte_signal, cpu_temp, memory_usage):
        """Update system status in the database"""
        try:
            with sqlite3.connect("/var/lib/barrier-monitor/history.db") as conn:
                conn.execute(
                    """INSERT INTO system_status 
                       (status, uptime, notification_count, lte_signal, cpu_temp, memory_usage) 
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (status, uptime, notification_count, lte_signal, cpu_temp, memory_usage)
                )
            
            # Emit status update to connected clients
            status_data = {
                'timestamp': datetime.now().isoformat(),
                'status': status,
                'uptime': uptime,
                'notification_count': notification_count,
                'lte_signal': lte_signal,
                'cpu_temp': cpu_temp,
                'memory_usage': memory_usage
            }
            socketio.emit('status_update', status_data)
            
            logger.info("System status updated")
        except Exception as e:
            logger.error(f"Failed to update system status: {e}")

    def log_notification(self, notification_type, recipient, message, status):
        """Log notification details"""
        try:
            with sqlite3.connect("/var/lib/barrier-monitor/history.db") as conn:
                conn.execute(
                    "INSERT INTO notifications (type, recipient, message, status) VALUES (?, ?, ?, ?)",
                    (notification_type, recipient, message, status)
                )
            logger.info(f"Notification logged: {notification_type} to {recipient}")
        except Exception as e:
            logger.error(f"Failed to log notification: {e}")

# Flask routes
@app.route('/')
def index():
    """Render main dashboard"""
    return render_template('index.html')

@app.route('/api/events')
def get_events():
    """Get historical events with filtering and pagination"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        event_type = request.args.get('type')
        circuit_id = request.args.get('circuit_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = "SELECT * FROM events WHERE 1=1"
        params = []
        
        if event_type:
            query += " AND event_type = ?"
            params.append(event_type)
        if circuit_id:
            query += " AND circuit_id = ?"
            params.append(circuit_id)
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date)
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date)
        
        query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
        params.extend([per_page, (page - 1) * per_page])
        
        with sqlite3.connect("/var/lib/barrier-monitor/history.db") as conn:
            cursor = conn.execute(query, params)
            events = [dict(zip([col[0] for col in cursor.description], row))
                     for row in cursor.fetchall()]
            
            # Get total count for pagination
            count_query = query.replace("SELECT *", "SELECT COUNT(*)")
            count_query = count_query[:count_query.find(" ORDER BY")]
            total = conn.execute(count_query, params[:-2]).fetchone()[0]
            
        return jsonify({
            "success": True,
            "events": events,
            "total": total,
            "page": page,
            "per_page": per_page
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/status')
def get_status():
    """Get current system status"""
    try:
        with sqlite3.connect("/var/lib/barrier-monitor/history.db") as conn:
            cursor = conn.execute(
                "SELECT * FROM system_status ORDER BY timestamp DESC LIMIT 1"
            )
            status = dict(zip([col[0] for col in cursor.description], cursor.fetchone()))
            
            # Add circuit status
            cursor = conn.execute(
                """SELECT circuit_id, event_type, timestamp 
                   FROM events 
                   WHERE timestamp >= datetime('now', '-1 hour')
                   ORDER BY timestamp DESC"""
            )
            circuit_events = cursor.fetchall()
            
            status['circuits'] = {}
            for circuit_id in self.config.get('circuits', {}).keys():
                relevant_events = [e for e in circuit_events if e[0] == circuit_id]
                status['circuits'][circuit_id] = {
                    'status': relevant_events[0][1] if relevant_events else 'normal',
                    'last_event': relevant_events[0][2] if relevant_events else None
                }
            
        return jsonify({"success": True, "status": status})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/config', methods=['GET', 'POST'])
def handle_config():
    """Get or update system configuration"""
    if request.method == 'GET':
        try:
            with open("config.yaml", 'r') as f:
                config = yaml.safe_load(f)
            return jsonify({"success": True, "config": config})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)})
    else:
        try:
            new_config = request.json
            # Validate config before saving
            if not validate_config(new_config):
                return jsonify({"success": False, "error": "Invalid configuration"})
            
            # Backup existing config
            backup_path = f"config.yaml.bak.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            os.rename("config.yaml", backup_path)
            
            # Save new config
            with open("config.yaml", 'w') as f:
                yaml.dump(new_config, f)
            
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)})

@app.route('/api/notifications')
def get_notifications():
    """Get notification history"""
    try:
        days = int(request.args.get('days', 7))
        with sqlite3.connect("/var/lib/barrier-monitor/history.db") as conn:
            cursor = conn.execute(
                """SELECT * FROM notifications 
                   WHERE timestamp >= datetime('now', ?) 
                   ORDER BY timestamp DESC""",
                (f'-{days} days',)
            )
            notifications = [dict(zip([col[0] for col in cursor.description], row))
                           for row in cursor.fetchall()]
        return jsonify({"success": True, "notifications": notifications})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/analytics')
def get_analytics():
    """Get system analytics"""
    try:
        days = int(request.args.get('days', 7))
        with sqlite3.connect("/var/lib/barrier-monitor/history.db") as conn:
            # Get event counts by type
            cursor = conn.execute(
                """SELECT event_type, COUNT(*) as count 
                   FROM events 
                   WHERE timestamp >= datetime('now', ?) 
                   GROUP BY event_type""",
                (f'-{days} days',)
            )
            event_counts = dict(cursor.fetchall())
            
            # Get notification success rate
            cursor = conn.execute(
                """SELECT status, COUNT(*) as count 
                   FROM notifications 
                   WHERE timestamp >= datetime('now', ?) 
                   GROUP BY status""",
                (f'-{days} days',)
            )
            notification_stats = dict(cursor.fetchall())
            
            # Get system uptime
            cursor = conn.execute(
                """SELECT AVG(uptime) as avg_uptime 
                   FROM system_status 
                   WHERE timestamp >= datetime('now', ?)""",
                (f'-{days} days',)
            )
            avg_uptime = cursor.fetchone()[0]
            
            # Get LTE signal strength history
            cursor = conn.execute(
                """SELECT timestamp, lte_signal 
                   FROM system_status 
                   WHERE timestamp >= datetime('now', ?) 
                   ORDER BY timestamp""",
                (f'-{days} days',)
            )
            signal_history = cursor.fetchall()
            
        return jsonify({
            "success": True,
            "event_counts": event_counts,
            "notification_stats": notification_stats,
            "avg_uptime": avg_uptime,
            "signal_history": signal_history
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

def validate_config(config):
    """Validate configuration structure and values"""
    required_fields = ['circuits', 'notifications', 'lte']
    if not all(field in config for field in required_fields):
        return False
    
    # Validate circuit configuration
    for circuit_id, circuit_config in config.get('circuits', {}).items():
        if not all(key in circuit_config for key in ['gpio_pin', 'name']):
            return False
        if not isinstance(circuit_config['gpio_pin'], int):
            return False
    
    # Validate notification configuration
    notifications = config.get('notifications', {})
    if not all(key in notifications for key in ['email', 'sms']):
        return False
    
    # Validate LTE configuration
    lte = config.get('lte', {})
    if not all(key in lte for key in ['port', 'baud_rate', 'apn']):
        return False
    
    return True

def start_web_interface(host='0.0.0.0', port=5000):
    """Start the web interface with WebSocket support"""
    socketio.run(app, host=host, port=port)

if __name__ == "__main__":
    start_web_interface()
