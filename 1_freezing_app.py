"""
Version 1: Everything on the main thread (BAD — freezes the GUI).

Run:
    python 1_freezing_app.py

What to watch:
    The ticking counter at the top updates every 100ms via a QTimer,
    proving the GUI is "alive." Click "Run Slow Task" and watch the
    counter freeze for 3 seconds — that's the whole app locking up,
    including the counter, the button, window dragging, everything.
"""

import sys
import time

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


def slow_task(text: str) -> str:
    time.sleep(3)  # pretend this is a slow network call / computation
    return f"You said: {text}"


# Main windows with your widgets
class FreezingWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("1. Freezing App (main thread only)")
        self.resize(400, 200)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        self.tick_count = 0
        self.tick_label = QLabel("Ticks: 0")
        layout.addWidget(self.tick_label)

        self.status_label = QLabel("Status: idle")
        layout.addWidget(self.status_label)

        self.run_button = QPushButton("Run Slow Task (blocks everything)")
        self.run_button.clicked.connect(self.run_slow_task)
        layout.addWidget(self.run_button)

        # Ticks every 100ms to prove the GUI is alive — watch this freeze.
        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)
        self.timer.start(100)

    def tick(self):
        self.tick_count += 1
        self.tick_label.setText(f"Ticks: {self.tick_count}")

    def run_slow_task(self):
        self.status_label.setText("Status: running... (and the whole GUI is frozen)")
        result = slow_task("hello")  # <-- runs directly on the main thread
        self.status_label.setText(f"Status: {result}")


def main():
    app = QApplication(sys.argv)
    window = FreezingWindow()
    window.show()
    # starts main event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
