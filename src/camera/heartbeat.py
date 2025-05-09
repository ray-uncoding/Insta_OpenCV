import threading
import time
import requests

class Heartbeat:
    def __init__(self, check_interval=1):
        self.check_interval = check_interval
        self.running = False
        self.thread = threading.Thread(target=self._monitor, daemon=True)

    def start(self):
        """Start the heartbeat monitoring."""
        self.running = True
        self.thread.start()

    def stop(self):
        """Stop the heartbeat monitoring."""
        self.running = False
        self.thread.join()

    def _monitor(self):
        """Internal method to periodically check the connection."""
        while self.running:
            print("Heartbeat: Checking camera connection...")
            time.sleep(self.check_interval)

    def send_heartbeat(self, state_url, fingerprint):
        """Send a heartbeat signal to keep the connection alive."""
        headers = {
            "Fingerprint": fingerprint,
            "Content-Type": "application/json"
        }
        response = requests.post(state_url, json={}, headers=headers, timeout=5)
        if response.status_code != 200:
            raise Exception("Heartbeat failed")