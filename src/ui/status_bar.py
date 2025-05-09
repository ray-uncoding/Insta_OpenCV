from PyQt5.QtWidgets import QLabel

class StatusBar(QLabel):
    def __init__(self):
        super().__init__()
        self.setText("Status: Ready")

    def update_status(self, message):
        """Update the status message."""
        self.setText(f"Status: {message}")