import threading
import queue
import requests

class SignalHandler:
    def __init__(self):
        # Queue to store incoming signals
        self.signal_queue = queue.Queue()
        self.lock = threading.Lock()

    def add_signal(self, signal):
        """Add a signal to the queue."""
        with self.lock:
            self.signal_queue.put(signal)

    def process_signals(self):
        """Process signals in the queue."""
        while not self.signal_queue.empty():
            signal = self.signal_queue.get()
            self.handle_signal(signal)

    def handle_signal(self, signal):
        """Handle a single signal. Override this method for custom logic."""
        print(f"Processing signal: {signal}")

    def register_fingerprint(self, command_url, hw_time, time_zone="GMT+8"):
        """Send a command to register the fingerprint."""
        payload = {
            "name": "camera._connect",
            "parameters": {
                "hw_time": hw_time,
                "time_zone": time_zone
            }
        }
        headers = {"Content-Type": "application/json"}
        response = requests.post(command_url, json=payload, headers=headers, timeout=10)
        response_data = response.json()
        if response_data.get("state") == "done":
            return response_data["results"].get("Fingerprint")
        else:
            raise Exception("Failed to register fingerprint")