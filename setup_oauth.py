"""
OAuth setup script for Gmail API authentication
"""
import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def setup_oauth():
    """Setup OAuth 2.0 for Gmail API"""
    creds = None
    
    # Check if token.pickle exists
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If credentials need refresh or don't exist
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Load credentials from file
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save credentials
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return creds

if __name__ == '__main__':
    print("Setting up Gmail API OAuth...")
    try:
        creds = setup_oauth()
        print("OAuth setup successful! Token saved to token.pickle")
    except Exception as e:
        print(f"Error during OAuth setup: {e}")
        print("\nTroubleshooting steps:")
        print("1. Ensure credentials.json is in the current directory")
        print("2. Check that Gmail API is enabled in Google Cloud Console")
        print("3. Verify that credentials.json contains correct OAuth 2.0 client ID")
        exit(1)
