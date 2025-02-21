"""
Copyright 2025 Automate Systems and Simon Callaghan.

This software was developed by Simon Callaghan during employment at Automate Systems.
All rights reserved. See LICENSE file for details.
"""

#!/usr/bin/env python3

import logging
import threading
import time
import sys

class WatchdogHandler:
    def __init__(self, timeout_seconds):
        """Initialize watchdog timer"""
        self.logger = logging.getLogger(__name__)
        self.timeout = timeout_seconds
        self.last_pet = time.time()
        self.running = True
        
        # Start watchdog thread
        self.thread = threading.Thread(target=self._watchdog_loop, daemon=True)
        self.thread.start()
        self.logger.info(f"Watchdog started with {timeout_seconds}s timeout")

    def pet(self):
        """Reset the watchdog timer"""
        self.last_pet = time.time()

    def _watchdog_loop(self):
        """Main watchdog loop"""
        while self.running:
            if (time.time() - self.last_pet) > self.timeout:
                self.logger.critical("Watchdog timeout - system unresponsive!")
                sys.exit(1)
            time.sleep(1)

    def stop(self):
        """Stop the watchdog"""
        self.running = False
        self.thread.join()
        self.logger.info("Watchdog stopped")
