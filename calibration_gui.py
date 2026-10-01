import sys
import time

import serial
from PyQt6.QtWidgets import (
    QApplication,
    QGridLayout,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

PORT = "COM9"
BAUDRATE = 115200

X_MIN_POS = -10
Y_MIN_POS = -35
Z_MIN_POS = -0.5

X_MAX_POS = 280
Y_MAX_POS = 210
Z_MAX_POS = 300

CORNER_MARGIN = 25


def send_command(command):
    printer.write(f"{command}\n".encode())

    while True:
        line = printer.readline().decode(errors="ignore").strip()

        if line and line != "ok" and line != "echo:busy: processing":
            print(line)

        if line == "ok":
            return


def probe(x, y):
    send_command("G28 O")
    send_command(f"G0 X{x} Y{y} F5000")
    send_command("G30")
    send_command(f"G0 X{x} Y{y} F5000")


def home():
    send_command("G28")
    send_command("G0 Z7")


positions = {
    "Top Left": (X_MAX_POS - CORNER_MARGIN, CORNER_MARGIN),
    "Top Right": (CORNER_MARGIN, CORNER_MARGIN),
    "Center": (X_MAX_POS / 2, Y_MAX_POS / 2),
    "Bottom Left": (X_MAX_POS - CORNER_MARGIN, Y_MAX_POS - CORNER_MARGIN),
    "Bottom Right": (CORNER_MARGIN, Y_MAX_POS - CORNER_MARGIN),
}


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Bed Probe")
        self.setFixedSize(350, 300)

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        home_button = QPushButton("Home (G28)")
        home_button.clicked.connect(home)
        layout.addWidget(home_button)

        grid = QGridLayout()
        grid.setSpacing(5)
        layout.addLayout(grid)

        buttons = {
            "Top Left": (0, 0),
            "Top Right": (0, 2),
            "Center": (1, 1),
            "Bottom Left": (2, 0),
            "Bottom Right": (2, 2),
        }

        for name, (row, column) in buttons.items():
            x, y = positions[name]

            button = QPushButton(name)
            button.setMinimumSize(100, 60)
            button.clicked.connect(lambda checked=False, x=x, y=y: probe(x, y))

            grid.addWidget(button, row, column)

        self.setCentralWidget(central)


app = QApplication(sys.argv)

try:
    printer = serial.Serial(PORT, BAUDRATE, timeout=2)
    time.sleep(1)
except serial.SerialException as e:
    QMessageBox.critical(None, "Serial Error", str(e))
    sys.exit(1)

window = MainWindow()
window.show()

sys.exit(app.exec())
