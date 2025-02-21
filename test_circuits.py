"""
Test script for barrier circuits
"""
import yaml
import time
import RPi.GPIO as GPIO
from circuit_monitor import CircuitMonitor

def test_circuits():
    """Test barrier circuit monitoring"""
    # Load configuration
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    success = True
    
    print("Testing barrier circuits...")
    try:
        # Initialize circuit monitor
        monitor = CircuitMonitor(config)
        
        # Test each configured circuit
        for circuit_name, circuit_config in config['circuits'].items():
            print(f"\nTesting circuit: {circuit_name}")
            
            # Test GPIO setup
            print(f"1. Checking GPIO {circuit_config['gpio_pin']}...")
            try:
                value = GPIO.input(circuit_config['gpio_pin'])
                print(f"✓ GPIO reading: {'HIGH' if value else 'LOW'}")
            except Exception as e:
                print(f"✗ GPIO error: {e}")
                success = False
                continue
            
            # Test circuit monitoring
            print("\n2. Monitoring circuit state...")
            try:
                state = monitor.check_circuit(circuit_name)
                print(f"✓ Circuit state: {'ALERT' if state['alert_active'] else 'NORMAL'}")
            except Exception as e:
                print(f"✗ Monitoring error: {e}")
                success = False
            
            # Test notification trigger
            print("\n3. Testing notification trigger...")
            try:
                if state['should_notify']:
                    print("✓ Notification would be triggered")
                else:
                    print("✓ No notification needed")
            except Exception as e:
                print(f"✗ Notification check error: {e}")
                success = False
            
            # Test pull-up resistor
            print("\n4. Checking pull-up resistor...")
            try:
                # Read value multiple times to ensure stable reading
                readings = [GPIO.input(circuit_config['gpio_pin']) for _ in range(5)]
                if all(readings):
                    print("✓ Pull-up resistor working")
                else:
                    print("✗ Pull-up resistor may be missing or faulty")
                    success = False
            except Exception as e:
                print(f"✗ Pull-up test error: {e}")
                success = False
    
    except Exception as e:
        print(f"✗ Circuit test error: {e}")
        success = False
    
    finally:
        # Clean up GPIO
        GPIO.cleanup()
    
    return success

if __name__ == '__main__':
    print("Running circuit tests...")
    success = test_circuits()
    
    if not success:
        print("\nTroubleshooting steps:")
        print("1. Check physical connections")
        print("2. Verify GPIO pin numbers in config.yaml")
        print("3. Ensure pull-up resistors are properly connected")
        print("4. Check for any loose wires")
        print("5. Verify photocell operation")
        print("6. Test continuity of NC contacts")
        exit(1)
    else:
        print("\nAll circuit tests passed!")
