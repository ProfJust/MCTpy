
import network
import socket
import select
from time import sleep_ms, ticks_ms, ticks_diff
from arduino_alvik import ArduinoAlvik

# ------------------------------------------
# WLAN-Konfiguration
# ------------------------------------------
SSID = "just_a_wlan"
PASSWORT = "Geheim1234"
PORT = 5000

# Sicherheitsparameter
MAX_SPEED = 13.0      # cm/s
TIMEOUT_MS = 500      # Kommunikations-Watchdog

alvik = ArduinoAlvik()
alvik.begin()
alvik.set_wheels_speed(0, 0)


def wlan_verbinden():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        print("Verbinde mit WLAN...")
        wlan.connect(SSID, PASSWORT)

        start = ticks_ms()

        while not wlan.isconnected():
            if ticks_diff(ticks_ms(), start) > 15000:
                raise RuntimeError("WLAN Timeout")
            sleep_ms(100)

    ip = wlan.ifconfig()[0]
    print("Alvik IP:", ip)
    return wlan


def server_starten():
    addr = socket.getaddrinfo(
        "0.0.0.0", PORT
    )[0][-1]

    server = socket.socket()
    server.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR, 1
    )
    server.bind(addr)
    server.listen(1)
    server.setblocking(False)

    print("TCP Server bereit, Port:", PORT)
    return server


def steuerung(server):
    while True:
        print("Warte auf PC...")

        # Nicht blockierend auf Verbindung warten
        while True:
            bereit, _, _ = select.select(
                [server], [], [], 0.1
            )
            if bereit:
                client, adresse = server.accept()
                break

        print("Verbunden:", adresse)
        client.setblocking(False)

        buffer = b""
        letzte_nachricht = ticks_ms()
        bewegt = False

        try:
            while True:
                bereit, _, _ = select.select(
                    [client], [], [], 0.01
                )

                if bereit:
                    daten = client.recv(128)

                    if not daten:
                        break

                    buffer += daten

                    # Schutz vor zu langen Nachrichten
                    if len(buffer) > 256:
                        break

                    while b"\n" in buffer:
                        zeile, buffer = buffer.split(
                            b"\n", 1
                        )

                        try:
                            teile = zeile.decode().split(",")

                            if len(teile) != 2:
                                continue

                            links = float(teile[0])
                            rechts = float(teile[1])

                            # Nur endliche Werte erlauben
                            if not (
                                -MAX_SPEED <= links <= MAX_SPEED
                                and
                                -MAX_SPEED <= rechts <= MAX_SPEED
                            ):
                                continue

                            alvik.set_wheels_speed(
                                links, rechts
                            )
                            bewegt = (links != 0 or rechts != 0)
                            letzte_nachricht = ticks_ms()

                        except (ValueError, UnicodeError):
                            pass

                # Stoppen bei Kommunikationsausfall
                if ticks_diff(
                    ticks_ms(), letzte_nachricht
                ) > TIMEOUT_MS:
                    if bewegt:
                        alvik.set_wheels_speed(0, 0)
                        bewegt = False

        finally:
            alvik.set_wheels_speed(0, 0)
            client.close()
            print("Verbindung getrennt")


server = None

try:
    wlan = wlan_verbinden()
    server = server_starten()
    steuerung(server)

finally:
    alvik.set_wheels_speed(0, 0)
    if server:
        server.close()
