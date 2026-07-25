"""
Version 3: A plain QObject worker moved to a QThread (recommended pattern).

Run:
    python 3_worker_object_app.py

What to watch:
    Same behavior as 2_subclass_qthread_app.py from the user's point of
    view — the counter keeps ticking during the 3-second "slow task." The
    difference is under the hood: thread affinity is set explicitly via
    moveToThread(), so ResponderWorker and every method on it belong to the
    worker thread — not just whatever's inside one specially-treated method.
    NOTE: The methods cannot be triggered normally, it must be triggered via 
    signal and slot connections, otherwise it runs within the thread it is 
    being executed on.
"""

import sys
import time

from PyQt6.QtCore import QObject, QThread, QTimer, pyqtSignal
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class ResponderWorker(QObject):
    result_ready = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, text: str, parent=None):
        super().__init__(parent)
        self.text = text

    def run(self) -> None:
        time.sleep(3)  # pretend this is a slow network call / computation
        response = f"You said: {self.text}"
        self.result_ready.emit(response)
        self.finished.emit()


# This manages the thread lifecycle sets the ResponderWorker to use it
def make_responder_thread(text: str) -> tuple[QThread, ResponderWorker]:
    thread = QThread()
    worker = ResponderWorker(text)
    worker.moveToThread(thread)

    thread.started.connect(worker.run)
    worker.finished.connect(thread.quit)
    worker.finished.connect(worker.deleteLater)
    thread.finished.connect(thread.deleteLater)

    return thread, worker


class WorkerObjectWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("3. Worker Object + moveToThread()")
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

        self.thread: QThread | None = None
        self.worker: ResponderWorker | None = None

    def tick(self):
        self.tick_count += 1
        self.tick_label.setText(f"Ticks: {self.tick_count}")

    def run_slow_task(self):
        self.status_label.setText("Status: running in background thread...")
        self.run_button.setEnabled(False)

        # Keep references on self — locals could get garbage collected
        # mid-run and kill the thread unexpectedly.
        self.thread, self.worker = make_responder_thread("hello")
        self.worker.result_ready.connect(self.on_result)
        self.thread.start()

    def on_result(self, result: str):
        self.status_label.setText(f"Status: {result}")
        self.run_button.setEnabled(True)


def main():
    app = QApplication(sys.argv)
    window = WorkerObjectWindow()
    window.show()
    # starts main event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
