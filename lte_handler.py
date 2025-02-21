"""
LTE Mini HAT handler for cellular connectivity
Uses the Clipper LTE mini HAT for internet connectivity when WiFi is unavailable
"""

import serial
import time
import logging
import subprocess
from pathlib import Path

class LTEHandler:
    def __init__(self, config):
        self.logger = logging.getLogger(__name__)
        self.config = config.get('lte', {})
        self.serial_port = self.config.get('serial_port', '/dev/ttyUSB0')
        self.baud_rate = self.config.get('baud_rate', 115200)
        self.apn = self.config.get('apn', 'internet')
        self.connection = None
        self.connected = False

    def initialize(self):
        """Initialize the LTE HAT"""
        try:
            self.connection = serial.Serial(
                port=self.serial_port,
                baudrate=self.baud_rate,
                timeout=1
            )
            
            # Reset modem
            self._send_command('AT+CFUN=1,1')
            time.sleep(10)  # Wait for modem to restart
            
            # Check modem response
            if not self._send_command('AT'):
                raise Exception("Modem not responding")
            
            # Configure modem
            self._send_command('AT+CMEE=2')  # Enable verbose error messages
            self._send_command(f'AT+CGDCONT=1,"IP","{self.apn}"')  # Set APN
            
            self.logger.info("LTE HAT initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize LTE HAT: {e}")
            return False

    def connect(self):
        """Establish LTE connection"""
        try:
            # Check signal quality
            signal = self._check_signal_quality()
            if signal < 10:  # Minimum acceptable signal strength
                self.logger.warning(f"Poor signal strength: {signal}")
            
            # Start data connection
            if self._send_command('AT+CGACT=1,1'):
                # Get IP address
                response = self._send_command('AT+CGPADDR=1')
                if response and ',' in response:
                    ip = response.split(',')[1].strip('"')
                    self.logger.info(f"LTE connected with IP: {ip}")
                    self.connected = True
                    
                    # Update system routing if needed
                    if self.config.get('set_default_route', False):
                        self._update_routing()
                    return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to establish LTE connection: {e}")
            return False

    def disconnect(self):
        """Disconnect LTE connection"""
        try:
            if self.connection:
                self._send_command('AT+CGACT=0,1')
                self.connection.close()
                self.connected = False
                self.logger.info("LTE disconnected")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to disconnect LTE: {e}")
            return False

    def check_connection(self):
        """Check if LTE connection is active and working"""
        try:
            # Check if modem is responsive
            if not self._send_command('AT'):
                return False
            
            # Check if we have an IP
            response = self._send_command('AT+CGPADDR=1')
            if not response or ',' not in response:
                return False
            
            # Ping test to verify connectivity
            try:
                result = subprocess.run(
                    ['ping', '-c', '1', '8.8.8.8'],
                    capture_output=True,
                    timeout=5
                )
                return result.returncode == 0
            except subprocess.TimeoutExpired:
                return False
        except Exception as e:
            self.logger.error(f"Failed to check LTE connection: {e}")
            return False

    def _send_command(self, command, timeout=5):
        """Send AT command to modem and get response"""
        try:
            self.connection.write(f"{command}\r\n".encode())
            time.sleep(0.5)
            
            start_time = time.time()
            response = ""
            
            while time.time() - start_time < timeout:
                if self.connection.in_waiting:
                    response += self.connection.read(self.connection.in_waiting).decode()
                    if "OK" in response:
                        return response.strip()
                    elif "ERROR" in response:
                        self.logger.error(f"Command error: {response}")
                        return None
                time.sleep(0.1)
            
            self.logger.error("Command timeout")
            return None
        except Exception as e:
            self.logger.error(f"Failed to send command: {e}")
            return None

    def _check_signal_quality(self):
        """Check LTE signal quality"""
        try:
            response = self._send_command('AT+CSQ')
            if response and '+CSQ:' in response:
                signal = int(response.split(':')[1].split(',')[0])
                return signal
            return 0
        except Exception:
            return 0

    def _update_routing(self):
        """Update system routing to use LTE as default route"""
        try:
            # Get current default route
            subprocess.run(['ip', 'route', 'del', 'default'], check=False)
            
            # Add new default route via LTE
            subprocess.run(
                ['ip', 'route', 'add', 'default', 'dev', 'ppp0'],
                check=True
            )
            self.logger.info("Updated system routing to use LTE")
            return True
        except Exception as e:
            self.logger.error(f"Failed to update routing: {e}")
            return False
