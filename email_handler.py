"""
Copyright 2025 Automate Systems and Simon Callaghan.

This software was developed by Simon Callaghan during employment at Automate Systems.
All rights reserved. See LICENSE file for details.
"""

#!/usr/bin/env python3

import logging
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from email.mime.text import MIMEText
import base64

class EmailNotifier:
    def __init__(self, config):
        """Initialize the Gmail API client"""
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.service = None
        self.connect()

    def connect(self):
        """Connect to Gmail API"""
        SCOPES = ['https://www.googleapis.com/auth/gmail.send']
        creds = None

        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.config['credentials_file'], SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        try:
            self.service = build('gmail', 'v1', credentials=creds)
            self.logger.info("Successfully connected to Gmail API")
        except Exception as e:
            self.logger.error(f"Failed to connect to Gmail API: {e}")
            raise

    def create_message(self, subject, message_text):
        """Create an email message"""
        message = MIMEText(message_text)
        message['to'] = ', '.join(self.config['recipients'])
        message['from'] = self.config['sender']
        message['subject'] = f"{self.config['subject_prefix']} {subject}"
        
        return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

    def send_alert(self, subject, message):
        """Send an email alert"""
        try:
            if not self.service:
                self.connect()
            
            message = self.create_message(subject, message)
            self.service.users().messages().send(
                userId='me',
                body=message
            ).execute()
            
            self.logger.info(f"Alert email sent: {subject}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to send email: {e}")
            return False
