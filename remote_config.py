"""
Copyright © 2025 Automate Systems and Simon Callaghan.

This software was developed by Simon Callaghan during employment at Automate Systems.
All rights reserved. See LICENSE file for details.
"""

#!/usr/bin/env python3

import yaml
import logging
import json
import os
from pathlib import Path
from flask import Blueprint, request, jsonify
from functools import wraps

config_api = Blueprint('config_api', __name__)
logger = logging.getLogger(__name__)

def require_auth(f):
    """Decorator to require API key authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != config_api.config['api_key']:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated

@config_api.route('/api/config', methods=['GET'])
@require_auth
def get_config():
    """Get current configuration"""
    try:
        with open(config_api.config_path, 'r') as f:
            config = yaml.safe_load(f)
        return jsonify({'success': True, 'config': config})
    except Exception as e:
        logger.error(f"Failed to read configuration: {e}")
        return jsonify({'success': False, 'error': str(e)})

@config_api.route('/api/config/circuits', methods=['GET'])
@require_auth
def get_circuits():
    """Get circuit configurations"""
    try:
        with open(config_api.config_path, 'r') as f:
            config = yaml.safe_load(f)
        return jsonify({
            'success': True,
            'circuits': config.get('circuits', {})
        })
    except Exception as e:
        logger.error(f"Failed to read circuit configuration: {e}")
        return jsonify({'success': False, 'error': str(e)})

@config_api.route('/api/config/circuits/<circuit_id>', methods=['PUT'])
@require_auth
def update_circuit(circuit_id):
    """Update configuration for a specific circuit"""
    try:
        with open(config_api.config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        circuit_config = request.json
        if not circuit_config:
            return jsonify({'success': False, 'error': 'No configuration provided'})
        
        # Validate circuit configuration
        required_fields = ['gpio_pin', 'timeout_sec', 'notification_cooldown_min']
        for field in required_fields:
            if field not in circuit_config:
                return jsonify({'success': False, 'error': f'Missing required field: {field}'})
        
        # Update configuration
        if 'circuits' not in config:
            config['circuits'] = {}
        config['circuits'][circuit_id] = circuit_config
        
        # Save configuration
        backup_config(config_api.config_path)
        with open(config_api.config_path, 'w') as f:
            yaml.safe_dump(config, f)
        
        # Signal configuration change
        if config_api.change_callback:
            config_api.change_callback('circuit_update', circuit_id)
        
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Failed to update circuit configuration: {e}")
        return jsonify({'success': False, 'error': str(e)})

@config_api.route('/api/config/notifications', methods=['PUT'])
@require_auth
def update_notifications():
    """Update notification settings"""
    try:
        with open(config_api.config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        notification_config = request.json
        if not notification_config:
            return jsonify({'success': False, 'error': 'No configuration provided'})
        
        # Update email configuration
        if 'email' in notification_config:
            config['email'].update(notification_config['email'])
        
        # Update SMS configuration
        if 'sms' in notification_config:
            config['sms'].update(notification_config['sms'])
        
        # Save configuration
        backup_config(config_api.config_path)
        with open(config_api.config_path, 'w') as f:
            yaml.safe_dump(config, f)
        
        # Signal configuration change
        if config_api.change_callback:
            config_api.change_callback('notification_update', None)
        
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Failed to update notification configuration: {e}")
        return jsonify({'success': False, 'error': str(e)})

def backup_config(config_path):
    """Create a backup of the current configuration"""
    try:
        backup_dir = Path("/var/backup/barrier-monitor/config")
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Create timestamped backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"config_{timestamp}.yaml"
        
        with open(config_path, 'r') as src, open(backup_path, 'w') as dst:
            dst.write(src.read())
        
        # Keep only last 10 backups
        backups = sorted(backup_dir.glob("config_*.yaml"))
        if len(backups) > 10:
            for backup in backups[:-10]:
                backup.unlink()
        
        logger.info(f"Configuration backed up to {backup_path}")
    except Exception as e:
        logger.error(f"Failed to backup configuration: {e}")

def init_api(app, config_path, change_callback=None):
    """Initialize the configuration API"""
    config_api.config_path = config_path
    config_api.change_callback = change_callback
    
    # Load API configuration
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    config_api.config = config.get('remote_config', {})
    
    app.register_blueprint(config_api)
    logger.info("Remote configuration API initialized")
