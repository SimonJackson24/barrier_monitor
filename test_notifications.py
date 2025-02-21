"""
Test script for email and SMS notifications
"""
import yaml
from sms_handler import SMSNotifier
from monitor import send_email_notification

def test_notifications():
    """Test both email and SMS notifications"""
    # Load configuration
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    success = True
    
    # Test email notification
    print("Testing email notification...")
    try:
        result = send_email_notification(
            subject="Test Email",
            message="This is a test email from the barrier monitoring system.",
            config=config
        )
        if result:
            print("✓ Email notification successful")
        else:
            print("✗ Email notification failed")
            success = False
    except Exception as e:
        print(f"✗ Email notification error: {e}")
        success = False
    
    # Test SMS notification
    print("\nTesting SMS notification...")
    try:
        sms = SMSNotifier(config)
        result = sms.send_notification(
            "This is a test SMS from the barrier monitoring system."
        )
        if result:
            print("✓ SMS notification successful")
        else:
            print("✗ SMS notification failed")
            success = False
    except Exception as e:
        print(f"✗ SMS notification error: {e}")
        success = False
    
    return success

if __name__ == '__main__':
    print("Running notification tests...")
    success = test_notifications()
    
    if not success:
        print("\nTroubleshooting steps:")
        print("Email:")
        print("1. Check credentials.json and token.pickle exist")
        print("2. Verify Gmail API is enabled")
        print("3. Check email settings in config.yaml")
        
        print("\nSMS:")
        print("1. Verify SIM card is active and has credit")
        print("2. Check LTE signal strength")
        print("3. Ensure modem is responding to AT commands")
        
        exit(1)
    else:
        print("\nAll notification tests passed!")
