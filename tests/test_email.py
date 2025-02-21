#!/usr/bin/env python3

import sys
import os
import yaml
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from email_handler import EmailNotifier

def test_email_notification():
    """
    Test the email notification system by sending a test email.
    """
    try:
        # Load configuration
        with open('../config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        print("Initializing email notifier...")
        notifier = EmailNotifier(config['email'])
        
        print("Sending test email...")
        subject = "Test Alert"
        message = """
        This is a test email from the Barrier Monitor system.
        
        If you received this email, the notification system is working correctly.
        
        Time: {}
        """.format(time.strftime("%Y-%m-%d %H:%M:%S"))
        
        success = notifier.send_alert(subject, message)
        
        if success:
            print("Test email sent successfully!")
        else:
            print("Failed to send test email")
            
    except Exception as e:
        print(f"Error during test: {e}")

if __name__ == "__main__":
    test_email_notification()
