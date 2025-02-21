#!/usr/bin/env python3

import os
import sys
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle

def setup_credentials():
    """
    Guide the user through setting up Gmail API credentials.
    """
    print("Gmail API Credentials Setup")
    print("-" * 50)
    
    # Check for existing credentials
    if not os.path.exists('credentials.json'):
        print("""
Error: credentials.json not found!

Please follow these steps to get your credentials:
1. Go to https://console.cloud.google.com/
2. Create a new project or select an existing one
3. Enable the Gmail API for your project
4. Go to APIs & Services > Credentials
5. Click 'Create Credentials' > 'OAuth client ID'
6. Select 'Desktop app' as application type
7. Download the credentials and save as 'credentials.json' in this directory
""")
        return False

    # Initialize OAuth 2.0 flow
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']
    creds = None

    if os.path.exists('token.pickle'):
        print("Found existing token.pickle file")
        try:
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
            if creds and creds.valid:
                print("Existing credentials are valid!")
                return True
        except Exception as e:
            print(f"Error reading existing token: {e}")
    
    try:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing expired credentials...")
            creds.refresh(Request())
        else:
            print("\nStarting OAuth 2.0 authorization flow...")
            print("A browser window will open. Please log in and grant access.")
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials
        with open('token.pickle', 'wb') as token:
            print("Saving credentials to token.pickle...")
            pickle.dump(creds, token)
        
        print("\nCredentials setup completed successfully!")
        return True
        
    except Exception as e:
        print(f"\nError during setup: {e}")
        return False

if __name__ == "__main__":
    if setup_credentials():
        print("\nYou can now use the email notification system!")
        print("Try running tests/test_email.py to verify everything works.")
    else:
        print("\nCredential setup failed. Please check the error messages above.")
