#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time
import sys

def test_gpio_input(pin=17, duration=30):
    """
    Test GPIO input reading for a specified duration.
    Prints the state changes and helps verify the photocell connection.
    """
    try:
        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        print(f"Starting GPIO test on pin {pin} for {duration} seconds")
        print("Press Ctrl+C to stop early")
        print("\nCurrent state readings (1 = beam unbroken, 0 = beam broken):")
        
        start_time = time.time()
        last_state = GPIO.input(pin)
        state_change_time = time.time()
        
        while (time.time() - start_time) < duration:
            current_state = GPIO.input(pin)
            
            # Print state changes with timing
            if current_state != last_state:
                time_in_state = time.time() - state_change_time
                state_str = "unbroken" if last_state == 1 else "broken"
                print(f"Beam was {state_str} for {time_in_state:.2f} seconds")
                state_change_time = time.time()
                last_state = current_state
            
            time.sleep(0.1)  # 100ms check interval
            
    except KeyboardInterrupt:
        print("\nTest stopped by user")
    except Exception as e:
        print(f"Error during test: {e}")
    finally:
        GPIO.cleanup()
        print("\nGPIO test completed")

if __name__ == "__main__":
    # Allow pin number to be specified as command line argument
    pin = int(sys.argv[1]) if len(sys.argv) > 1 else 17
    duration = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    
    test_gpio_input(pin, duration)
