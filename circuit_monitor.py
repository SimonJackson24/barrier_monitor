"""
Copyright © 2025 Automate Systems and Simon Callaghan.

This software was developed by Simon Callaghan during employment at Automate Systems.
All rights reserved. See LICENSE file for details.
"""

#!/usr/bin/env python3

import RPi.GPIO as GPIO
import logging
import time
from datetime import datetime
from threading import Thread, Lock

class CircuitMonitor:
    def __init__(self, circuit_id, config, notification_callback):
        """Initialize a single circuit monitor"""
        self.logger = logging.getLogger(f"circuit_{circuit_id}")
        self.circuit_id = circuit_id
        self.config = config
        self.notification_callback = notification_callback
        self.state_change_time = None
        self.last_notification_time = datetime.min
        self.daily_notification_count = 0
        self.last_count_reset = datetime.now()
        self.running = False
        self.lock = Lock()
        
        # Initialize GPIO
        self.setup_gpio()

    def setup_gpio(self):
        """Set up GPIO for this circuit"""
        try:
            self.input_pin = self.config['gpio_pin']
            GPIO.setup(
                self.input_pin,
                GPIO.IN,
                pull_up_down=GPIO.PUD_UP if self.config['pull_up'] else GPIO.PUD_DOWN
            )
            self.logger.info(f"GPIO initialized on pin {self.input_pin}")
        except Exception as e:
            self.logger.error(f"Failed to initialize GPIO: {e}")
            raise

    def can_send_notification(self):
        """Check if notification can be sent based on cooldown and daily limit"""
        with self.lock:
            now = datetime.now()
            
            # Reset daily counter if it's past reset time
            reset_time = datetime.strptime(self.config['reset_time'], "%H:%M").time()
            if now.time() < reset_time and self.last_count_reset.time() > reset_time:
                self.daily_notification_count = 0
                self.last_count_reset = now

            # Check cooldown and daily limit
            cooldown_ok = (now - self.last_notification_time).total_seconds() >= \
                         (self.config['notification_cooldown_min'] * 60)
            daily_limit_ok = self.daily_notification_count < self.config['max_daily_notifications']
            
            return cooldown_ok and daily_limit_ok

    def monitor_loop(self):
        """Main monitoring loop for this circuit"""
        self.logger.info(f"Starting monitoring for circuit {self.circuit_id}")
        last_state = GPIO.input(self.input_pin)
        
        while self.running:
            try:
                current_state = GPIO.input(self.input_pin)
                
                # State has changed
                if current_state != last_state:
                    if current_state == (0 if self.config['active_low'] else 1):
                        # Barrier potentially stuck open
                        self.state_change_time = time.time()
                        self.notification_callback(
                            self.circuit_id,
                            "state_change",
                            "open",
                            0
                        )
                    else:
                        # Barrier closed
                        if self.state_change_time:
                            duration = int(time.time() - self.state_change_time)
                            self.notification_callback(
                                self.circuit_id,
                                "state_change",
                                "closed",
                                duration
                            )
                        self.state_change_time = None
                    last_state = current_state

                # Check if barrier has been open too long
                if self.state_change_time and \
                   (time.time() - self.state_change_time) > self.config['timeout_sec']:
                    if self.can_send_notification():
                        with self.lock:
                            duration = int(time.time() - self.state_change_time)
                            self.notification_callback(
                                self.circuit_id,
                                "alert",
                                "timeout",
                                duration
                            )
                            self.last_notification_time = datetime.now()
                            self.daily_notification_count += 1
                            self.state_change_time = time.time()  # Reset timer

                time.sleep(self.config['check_interval_ms'] / 1000)

            except Exception as e:
                self.logger.error(f"Error in circuit {self.circuit_id} monitoring: {e}")
                time.sleep(1)  # Prevent rapid error loops

    def start(self):
        """Start monitoring this circuit"""
        self.running = True
        self.thread = Thread(target=self.monitor_loop, daemon=True)
        self.thread.start()

    def stop(self):
        """Stop monitoring this circuit"""
        self.running = False
        if hasattr(self, 'thread'):
            self.thread.join()
        self.logger.info(f"Stopped monitoring circuit {self.circuit_id}")

class MultiCircuitMonitor:
    def __init__(self, config):
        """Initialize monitoring for multiple circuits"""
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.circuits = {}
        GPIO.setmode(GPIO.BCM)

    def add_circuit(self, circuit_id, config, notification_callback):
        """Add a new circuit to monitor"""
        try:
            circuit = CircuitMonitor(circuit_id, config, notification_callback)
            self.circuits[circuit_id] = circuit
            circuit.start()
            self.logger.info(f"Added circuit {circuit_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to add circuit {circuit_id}: {e}")
            return False

    def remove_circuit(self, circuit_id):
        """Remove a circuit from monitoring"""
        if circuit_id in self.circuits:
            try:
                self.circuits[circuit_id].stop()
                del self.circuits[circuit_id]
                self.logger.info(f"Removed circuit {circuit_id}")
                return True
            except Exception as e:
                self.logger.error(f"Error removing circuit {circuit_id}: {e}")
                return False
        return False

    def get_circuit_status(self, circuit_id):
        """Get current status of a specific circuit"""
        if circuit_id in self.circuits:
            circuit = self.circuits[circuit_id]
            return {
                'id': circuit_id,
                'state': 'open' if circuit.state_change_time else 'closed',
                'duration': int(time.time() - circuit.state_change_time) if circuit.state_change_time else 0,
                'daily_notifications': circuit.daily_notification_count
            }
        return None

    def get_all_statuses(self):
        """Get status of all circuits"""
        return {cid: self.get_circuit_status(cid) for cid in self.circuits}

    def stop_all(self):
        """Stop monitoring all circuits"""
        for circuit in self.circuits.values():
            circuit.stop()
        GPIO.cleanup()
        self.logger.info("Stopped all circuit monitoring")
