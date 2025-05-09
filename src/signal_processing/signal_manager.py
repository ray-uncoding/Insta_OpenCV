import threading
from .signal_handler import SignalHandler

class SignalManager:
    def __init__(self):
        self.signal_handler = SignalHandler()
        self.running = False
        self.thread = threading.Thread(target=self._run, daemon=True)

    def start(self):
        """Start the signal manager thread."""
        self.running = True
        self.thread.start()

    def stop(self):
        """Stop the signal manager thread."""
        self.running = False
        self.thread.join()

    def _run(self):
        """Internal method to process signals in a loop."""
        while self.running:
            self.signal_handler.process_signals()

    def add_signal(self, signal):
        """Add a signal to the handler."""
        self.signal_handler.add_signal(signal)