import threading
import time

class RecognitionWorker:
    def __init__(self, signal_manager):
        self.signal_manager = signal_manager
        self.running = False
        self.thread = threading.Thread(target=self._run, daemon=True)

    def start(self):
        """Start the recognition worker thread."""
        self.running = True
        self.thread.start()

    def stop(self):
        """Stop the recognition worker thread."""
        self.running = False
        self.thread.join()

    def _run(self):
        """Internal method to perform face recognition in a loop."""
        while self.running:
            print("RecognitionWorker: Performing face recognition...")
            # Simulate recognition and send a signal
            self.signal_manager.add_signal("Face recognized")
            time.sleep(2)