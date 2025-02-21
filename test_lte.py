"""
Test script for LTE connection
"""
import yaml
import time
from lte_handler import LTEHandler

def test_lte():
    """Test LTE connection and functionality"""
    # Load configuration
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    success = True
    
    print("Testing LTE connection...")
    try:
        # Initialize LTE handler
        lte = LTEHandler(config)
        
        # Test initialization
        print("1. Initializing LTE HAT...")
        if lte.initialize():
            print("✓ LTE HAT initialized")
        else:
            print("✗ LTE HAT initialization failed")
            success = False
            return success
        
        # Check signal strength
        print("\n2. Checking signal strength...")
        signal = lte._check_signal_quality()
        if signal > 0:
            print(f"✓ Signal strength: {signal}/31")
        else:
            print("✗ No signal detected")
            success = False
        
        # Test connection
        print("\n3. Testing connection...")
        if lte.connect():
            print("✓ LTE connected successfully")
        else:
            print("✗ LTE connection failed")
            success = False
        
        # Test internet connectivity
        print("\n4. Testing internet connectivity...")
        if lte.check_connection():
            print("✓ Internet connection verified")
        else:
            print("✗ Internet connection failed")
            success = False
        
        # Test disconnection
        print("\n5. Testing disconnection...")
        if lte.disconnect():
            print("✓ LTE disconnected successfully")
        else:
            print("✗ LTE disconnection failed")
            success = False
        
    except Exception as e:
        print(f"✗ LTE test error: {e}")
        success = False
    
    return success

if __name__ == '__main__':
    print("Running LTE tests...")
    success = test_lte()
    
    if not success:
        print("\nTroubleshooting steps:")
        print("1. Check if SIM card is properly inserted")
        print("2. Verify antenna connection")
        print("3. Check APN settings in config.yaml")
        print("4. Ensure SIM card is activated")
        print("5. Check signal strength in current location")
        print("6. Verify serial port permissions")
        exit(1)
    else:
        print("\nAll LTE tests passed!")
