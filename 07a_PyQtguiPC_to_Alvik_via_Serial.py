# pip install PyQt6 pyserial

import sys
import serial
from serial.tools import list_ports

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QLabel,
    QComboBox, QSpinBox, QMessageBox
)
from PyQt6.QtCore import QTimer, Qt


class AlvikGUI(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Arduino Alvik Steuerung")
        self.setFixedSize(360, 310)

        self.ser = None
        self.links = 0
        self.rechts = 0

        layout = QVBoxLayout(self)

        # COM-Port auswählen
        zeile = QHBoxLayout()
        self.port_box = QComboBox()
        self.port_box.addItems(
            [p.device for p in list_ports.comports()]
        )

        self.connect_button = QPushButton("Verbinden")
        self.connect_button.clicked.connect(self.verbinden)

        zeile.addWidget(self.port_box)
        zeile.addWidget(self.connect_button)
        layout.addLayout(zeile)

        # Geschwindigkeit
        zeile = QHBoxLayout()
        zeile.addWidget(QLabel("Geschwindigkeit (cm/s):"))

        self.speed = QSpinBox()
        self.speed.setRange(5, 30)
        self.speed.setValue(15)

        zeile.addWidget(self.speed)
        layout.addLayout(zeile)

        # Richtungstasten
        self.vor = QPushButton("▲ Vorwärts")
        self.zurueck = QPushButton("▼ Rückwärts")
        self.links_btn = QPushButton("◀ Links")
        self.rechts_btn = QPushButton("Rechts ▶")
        self.stopp_btn = QPushButton("■ STOPP")

        self.stopp_btn.setStyleSheet(
            "background-color: #e74c3c; color: white;"
        )

        layout.addWidget(self.vor, alignment=Qt.AlignmentFlag.AlignHCenter)

        zeile = QHBoxLayout()
        zeile.addWidget(self.links_btn)
        zeile.addWidget(self.stopp_btn)
        zeile.addWidget(self.rechts_btn)
        layout.addLayout(zeile)

        layout.addWidget(
            self.zurueck,
            alignment=Qt.AlignmentFlag.AlignHCenter
        )

        self.status = QLabel("Nicht verbunden")
        layout.addWidget(self.status)

        # Tastendruck / Loslassen
        self.vor.pressed.connect(
            lambda: self.fahren("vor")
        )
        self.zurueck.pressed.connect(
            lambda: self.fahren("zurueck")
        )
        self.links_btn.pressed.connect(
            lambda: self.fahren("links")
        )
        self.rechts_btn.pressed.connect(
            lambda: self.fahren("rechts")
        )

        for button in (
            self.vor, self.zurueck,
            self.links_btn, self.rechts_btn
        ):
            button.released.connect(self.stoppen)

        self.stopp_btn.clicked.connect(self.stoppen)

        # Alle 100 ms Befehl erneut senden
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.senden)
        self.timer.start(100)

    def verbinden(self):
        try:
            if self.ser and self.ser.is_open:
                self.stoppen()
                self.ser.close()
                self.ser = None
                self.status.setText("Getrennt")
                self.connect_button.setText("Verbinden")
                return

            port = self.port_box.currentText()
            self.ser = serial.Serial(
                port, 115200, timeout=0.1
            )

            self.status.setText("Verbunden: " + port)
            self.connect_button.setText("Trennen")

        except serial.SerialException as e:
            QMessageBox.critical(self, "Fehler", str(e))

    def fahren(self, richtung):
        v = self.speed.value()

        if richtung == "vor":
            self.links, self.rechts = v, v
        elif richtung == "zurueck":
            self.links, self.rechts = -v, -v
        elif richtung == "links":
            self.links, self.rechts = -v, v
        elif richtung == "rechts":
            self.links, self.rechts = v, -v

        self.senden()

    def stoppen(self):
        self.links = 0
        self.rechts = 0
        self.senden()

    def senden(self):
        if self.ser and self.ser.is_open:
            try:
                befehl = f"{self.links},{self.rechts}\n"
                self.ser.write(befehl.encode())
            except serial.SerialException:
                self.links = 0
                self.rechts = 0
                self.status.setText("Verbindung verloren")
                self.ser.close()
                self.ser = None
                self.connect_button.setText("Verbinden")

    def keyPressEvent(self, event):
        if event.isAutoRepeat():
            return

        tasten = {
            Qt.Key.Key_Up: "vor",
            Qt.Key.Key_Down: "zurueck",
            Qt.Key.Key_Left: "links",
            Qt.Key.Key_Right: "rechts"
        }

        if event.key() in tasten:
            self.fahren(tasten[event.key()])

    def keyReleaseEvent(self, event):
        if not event.isAutoRepeat():
            if event.key() in (
                Qt.Key.Key_Up, Qt.Key.Key_Down,
                Qt.Key.Key_Left, Qt.Key.Key_Right
            ):
                self.stoppen()

    def closeEvent(self, event):
        self.stoppen()
        if self.ser and self.ser.is_open:
            self.ser.close()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    fenster = AlvikGUI()
    fenster.show()
    sys.exit(app.exec())
