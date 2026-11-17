# https://chatgpt.com/s/t_6af741094c448191863f214c70939c55
import sys

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QDoubleSpinBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtNetwork import QTcpSocket


class AlvikGUI(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Arduino Alvik WLAN-Steuerung")
        self.setFixedSize(400, 330)

        self.links = 0.0
        self.rechts = 0.0
        self.richtung = "STOPP"

        self.socket = QTcpSocket(self)
        self.socket.connected.connect(self.verbunden)
        self.socket.disconnected.connect(self.getrennt)
        self.socket.errorOccurred.connect(self.netzwerkfehler)

        layout = QVBoxLayout(self)

        # ----------------------------------
        # IP-Adresse und Verbindung
        # ----------------------------------
        zeile = QHBoxLayout()

        zeile.addWidget(QLabel("Alvik IP:"))

        self.ip = QLineEdit("192.168.0.182")
        zeile.addWidget(self.ip)

        self.btn_connect = QPushButton("Verbinden")
        self.btn_connect.clicked.connect(
            self.verbindung_umschalten
        )
        zeile.addWidget(self.btn_connect)

        layout.addLayout(zeile)

        # ----------------------------------
        # Geschwindigkeit
        # ----------------------------------
        zeile = QHBoxLayout()
        zeile.addWidget(QLabel("Geschwindigkeit:"))

        self.speed = QDoubleSpinBox()
        self.speed.setRange(1.0, 13.0)
        self.speed.setSingleStep(1.0)
        self.speed.setValue(8.0)
        self.speed.setSuffix(" cm/s")

        zeile.addWidget(self.speed)
        layout.addLayout(zeile)

        # ----------------------------------
        # Richtungstasten
        # ----------------------------------
        self.btn_vor = QPushButton("▲ Vorwärts")
        self.btn_zurueck = QPushButton("▼ Rückwärts")
        self.btn_links = QPushButton("◀ Links")
        self.btn_rechts = QPushButton("Rechts ▶")
        self.btn_stop = QPushButton("■ STOPP")

        self.btn_stop.setStyleSheet(
            "background-color: #e74c3c;"
            "color: white; font-weight: bold;"
        )

        layout.addWidget(
            self.btn_vor,
            alignment=Qt.AlignmentFlag.AlignHCenter
        )

        zeile = QHBoxLayout()
        zeile.addWidget(self.btn_links)
        zeile.addWidget(self.btn_stop)
        zeile.addWidget(self.btn_rechts)
        layout.addLayout(zeile)

        layout.addWidget(
            self.btn_zurueck,
            alignment=Qt.AlignmentFlag.AlignHCenter
        )

        self.btn_vor.pressed.connect(
            lambda: self.fahren("VOR")
        )
        self.btn_zurueck.pressed.connect(
            lambda: self.fahren("ZURUECK")
        )
        self.btn_links.pressed.connect(
            lambda: self.fahren("LINKS")
        )
        self.btn_rechts.pressed.connect(
            lambda: self.fahren("RECHTS")
        )

        for button in (
            self.btn_vor, self.btn_zurueck,
            self.btn_links, self.btn_rechts
        ):
            button.released.connect(self.stoppen)

        self.btn_stop.clicked.connect(self.stoppen)

        # ----------------------------------
        # Status
        # ----------------------------------
        self.status = QLabel("Nicht verbunden")
        self.status.setStyleSheet("color: #a33;")

        self.fahrstatus = QLabel("Fahrbefehl: STOPP")

        layout.addWidget(self.status)
        layout.addWidget(self.fahrstatus)

        # 10 Hz Steuertelegramme
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.senden)
        self.timer.start(100)

    def ist_verbunden(self):
        return self.socket.state() == (
            QTcpSocket.SocketState.ConnectedState
        )

    def verbindung_umschalten(self):
        if self.ist_verbunden():
            self.stoppen()
            self.socket.disconnectFromHost()
        else:
            self.status.setText("Verbinde...")
            self.socket.connectToHost(
                self.ip.text().strip(), 5000
            )

    def verbunden(self):
        self.status.setText("WLAN verbunden")
        self.status.setStyleSheet("color: green;")
        self.btn_connect.setText("Trennen")
        self.stoppen()

    def getrennt(self):
        self.links = 0
        self.rechts = 0
        self.richtung = "STOPP"
        self.fahrstatus.setText("Fahrbefehl: STOPP")
        self.status.setText("Nicht verbunden")
        self.status.setStyleSheet("color: #a33;")
        self.btn_connect.setText("Verbinden")

    def netzwerkfehler(self, fehler):
        self.status.setText(
            "Netzwerkfehler: " + self.socket.errorString()
        )

    def fahren(self, richtung):
        if not self.ist_verbunden():
            return

        v = self.speed.value()
        self.richtung = richtung

        if richtung == "VOR":
            self.links, self.rechts = v, v
        elif richtung == "ZURUECK":
            self.links, self.rechts = -v, -v
        elif richtung == "LINKS":
            self.links, self.rechts = -v, v
        elif richtung == "RECHTS":
            self.links, self.rechts = v, -v

        self.fahrstatus.setText(
            "Fahrbefehl: " + richtung
        )
        self.senden()

    def stoppen(self):
        self.links = 0
        self.rechts = 0
        self.richtung = "STOPP"
        self.fahrstatus.setText("Fahrbefehl: STOPP")
        self.senden()

    def senden(self):
        if self.ist_verbunden():
            nachricht = (
                f"{self.links:.2f},{self.rechts:.2f}\n"
            )
            self.socket.write(nachricht.encode("utf-8"))

    def keyPressEvent(self, event):
        if event.isAutoRepeat():
            return

        tasten = {
            Qt.Key.Key_Up: "VOR",
            Qt.Key.Key_Down: "ZURUECK",
            Qt.Key.Key_Left: "LINKS",
            Qt.Key.Key_Right: "RECHTS"
        }

        if event.key() in tasten:
            self.fahren(tasten[event.key()])

    def keyReleaseEvent(self, event):
        if event.isAutoRepeat():
            return

        if event.key() in (
            Qt.Key.Key_Up, Qt.Key.Key_Down,
            Qt.Key.Key_Left, Qt.Key.Key_Right
        ):
            self.stoppen()

    def closeEvent(self, event):
        self.stoppen()
        self.socket.flush()
        self.socket.abort()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    fenster = AlvikGUI()
    fenster.show()
    sys.exit(app.exec())
