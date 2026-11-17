
from arduino_alvik import ArduinoAlvik
from time import ticks_ms, ticks_diff, sleep_ms
import sys
import select

alvik = ArduinoAlvik()
alvik.begin()

# Sicherheitsabschaltung nach 500 ms ohne Befehl
TIMEOUT_MS = 500
letzter_befehl = ticks_ms()

# Aktuelle Geschwindigkeit der beiden Räder
links = 0
rechts = 0

alvik.set_wheels_speed(0, 0)

while True:
    # Prüfen, ob Daten vom PC angekommen sind
    if select.select([sys.stdin], [], [], 0)[0]:
        zeile = sys.stdin.readline().strip()

        try:
            # Format: "linkes_rad,rechtes_rad"
            werte = zeile.split(",")
            if len(werte) == 2:
                l = float(werte[0])
                r = float(werte[1])

                # Geschwindigkeit begrenzen
                links = max(-30, min(30, l))
                rechts = max(-30, min(30, r))

                alvik.set_wheels_speed(links, rechts)
                letzter_befehl = ticks_ms()

        except ValueError:
            pass

    # Watchdog: Motoren stoppen
    if ticks_diff(ticks_ms(), letzter_befehl) > TIMEOUT_MS:
        if links != 0 or rechts != 0:
            alvik.set_wheels_speed(0, 0)
            links = 0
            rechts = 0

    sleep_ms(10)
