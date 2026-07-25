"""
Version 2: Subclassing QThread and overriding run() (classic pattern).

Run:
    python 2_subclass_qthread_app.py

What to watch:
    Click "Run Slow Task" — the counter keeps ticking and the button/window
    stay responsive while the 3-second sleep happens on a separate thread.
    Compare this to 1_freezing_app.py, where the counter stops dead.

Note for the lesson:
    Only code physically inside run() executes on the worker thread. If you
    added another method to ResponderWorker (besides __init__ and run), it
    would still run on the MAIN thread, because the ResponderWorker object
    itself was created there — the run() exemption doesn't extend to the
    rest of the class. See 3_worker_object_app.py for the pattern that
    avoids this trap.
"""

import sys
import time

from PyQt6.QtCore import QThread, QTimer, pyqtSignal, QCoreApplication
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


# Class that handles the call
class ResponderWorker(QThread):
    result_ready = pyqtSignal(str)

    def __init__(self, text: str):
        super().__init__()
        self.text = text

    # Run overrides for QThread always creates a separate thread
    def run(self) -> None:
        main_thread = QCoreApplication.instance().thread()
        current_thread = QThread.currentThread()
        print(f"run() main_thread == current_thread: {main_thread == current_thread}")
        time.sleep(3)  # pretend this is a slow network call / computation
        response = f"You said: {self.text}"
        self.result_ready.emit(response)

# Main windows with your widgets
class SubclassWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("2. QThread Subclass (run() override)")
        self.resize(400, 200)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        self.tick_count = 0
        self.tick_label = QLabel("Ticks: 0")
        layout.addWidget(self.tick_label)

        self.status_label = QLabel("Status: idle")
        layout.addWidget(self.status_label)

        self.run_button = QPushButton("Run Slow Task (stays responsive)")
        self.run_button.clicked.connect(self.run_slow_task)
        layout.addWidget(self.run_button)

        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)
        self.timer.start(100)

        self.worker: ResponderWorker | None = None

    def tick(self):
        self.tick_count += 1
        self.tick_label.setText(f"Ticks: {self.tick_count}")

    def run_slow_task(self):
        self.status_label.setText("Status: running in background thread...")
        self.run_button.setEnabled(False)

        # Keep a reference on self — a local variable could get garbage
        # collected mid-run and kill the thread unexpectedly.
        self.worker = ResponderWorker("hello")
        self.worker.result_ready.connect(self.on_result)
        self.worker.start()  # NOT run() directly — start() spins up the thread

    def on_result(self, result: str):
        self.status_label.setText(f"Status: {result}")
        self.run_button.setEnabled(True)


def main():
    app = QApplication(sys.argv)
    window = SubclassWindow()
    window.show()
    # starts main event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
