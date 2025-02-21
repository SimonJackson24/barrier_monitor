"""
SMS notification handler using LTE modem AT commands
"""
import logging
import time
from datetime import datetime, timedelta

class SMSNotifier:
    def __init__(self, config):
        self.logger = logging.getLogger(__name__)
        self.config = config.get('sms', {})
        self.enabled = self.config.get('enabled', False)
        self.recipients = self.config.get('recipients', [])
        self.subject_prefix = self.config.get('subject_prefix', '[BARRIER ALERT]')
        self.last_notification = {}
        self.notification_count = {}
        self.reset_time = datetime.strptime(
            self.config.get('reset_time', '00:00'),
            '%H:%M'
        ).time()
        
        # Get LTE handler instance
        from lte_handler import LTEHandler
        self.lte = LTEHandler(config)

    def send_notification(self, message):
        """Send SMS notification using LTE modem"""
        if not self.enabled:
            self.logger.info("SMS notifications are disabled")
            return False

        if not self.recipients:
            self.logger.warning("No SMS recipients configured")
            return False

        try:
            # Format message
            formatted_message = self.format_message(message)
            
            # Check rate limits
            if not self._check_rate_limits():
                return False
            
            # Ensure LTE is initialized
            if not self.lte.initialize():
                self.logger.error("Failed to initialize LTE modem")
                return False
            
            success = True
            for recipient in self.recipients:
                # Send SMS using AT commands
                if not self._send_sms(recipient, formatted_message):
                    success = False
                    continue
                
                # Update notification tracking
                self._update_notification_count()
                self.last_notification[recipient] = datetime.now()
            
            return success

        except Exception as e:
            self.logger.error(f"Failed to send SMS notification: {e}")
            return False

    def _send_sms(self, recipient, message):
        """Send SMS using AT commands"""
        try:
            # Set SMS text mode
            if not self.lte._send_command('AT+CMGF=1'):
                return False
            
            # Set recipient
            if not self.lte._send_command(f'AT+CMGS="{recipient}"'):
                return False
            
            # Send message content (must end with Ctrl+Z character)
            if not self.lte._send_command(f'{message}\x1A'):
                return False
            
            self.logger.info(f"SMS sent to {recipient}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send SMS via modem: {e}")
            return False

    def format_message(self, message):
        """Format SMS message with prefix"""
        return f"{self.subject_prefix} {message}"

    def _check_rate_limits(self):
        """Check if we can send notifications based on rate limits"""
        current_time = datetime.now()
        
        # Reset daily counts if past reset time
        if current_time.time() < self.reset_time:
            yesterday = current_time - timedelta(days=1)
            reset_time = datetime.combine(yesterday.date(), self.reset_time)
        else:
            reset_time = datetime.combine(current_time.date(), self.reset_time)
        
        if any(last <= reset_time for last in self.last_notification.values()):
            self.notification_count = {}

        # Check cooldown period
        cooldown = timedelta(minutes=self.config.get('notification_cooldown_min', 5))
        for recipient, last_time in self.last_notification.items():
            if last_time and current_time - last_time < cooldown:
                self.logger.info(f"Notification cooldown in effect for {recipient}")
                return False

        # Check daily limit
        max_daily = self.config.get('max_daily_notifications', 50)
        if any(count >= max_daily for count in self.notification_count.values()):
            self.logger.warning("Daily notification limit reached")
            return False

        return True

    def _update_notification_count(self):
        """Update notification counter for rate limiting"""
        current_time = datetime.now()
        for recipient in self.recipients:
            self.notification_count[recipient] = self.notification_count.get(recipient, 0) + 1
