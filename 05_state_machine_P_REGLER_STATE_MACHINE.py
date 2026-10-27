# Arduino Alvik: Linienfolger mit State Machine und P-Regler

from arduino_alvik import ArduinoAlvik
from time import sleep_ms
from enum import Enum


# --------------------------------------------------
# Zustände definieren
# --------------------------------------------------
class Zustand(Enum):
    WARTEN = 0
    LINIE_FOLGEN = 1
    LINIE_SUCHEN = 2


# --------------------------------------------------
# P-Regler: Position der Linie berechnen
# --------------------------------------------------
def calculate_center(left, center, right):
    sum_weight = left + center + right

    if sum_weight == 0:
        return None  # Keine Linie erkannt

    centroid = (left + 2 * center + 3 * right) / sum_weight

    return 2 - centroid


# --------------------------------------------------
# Initialisierung
# --------------------------------------------------
alvik = ArduinoAlvik()
alvik.begin()

zustand = Zustand.WARTEN

# Parameter
KP = 50.0
GESCHWINDIGKEIT = 30.0
SUCHGESCHWINDIGKEIT = 15.0

letzter_fehler = 0.0

print("Linienfolger mit State Machine")
print("OK-Taste zum Starten")


# --------------------------------------------------
# Hauptprogramm
# --------------------------------------------------
try:
    while True:

        # Sensoren auslesen
        left, center, right = alvik.get_line_sensors()

        # Regelabweichung berechnen
        fehler = calculate_center(left, center, right)

        # ------------------------------------------
        # Zustand: WARTEN
        # ------------------------------------------
        if zustand == Zustand.WARTEN:

            alvik.brake()

            if alvik.get_touch_ok():
                zustand = Zustand.LINIE_FOLGEN
                print("Starte Linienfolger")
                sleep_ms(300)

        # ------------------------------------------
        # Zustand: LINIE_FOLGEN
        # ------------------------------------------
        elif zustand == Zustand.LINIE_FOLGEN:

            if fehler is None:
                alvik.brake()
                zustand = Zustand.LINIE_SUCHEN
                print("Linie verloren!")

            else:
                # P-Regler
                korrektur = KP * fehler

                # Motor-Geschwindigkeiten
                speed_left = GESCHWINDIGKEIT - korrektur
                speed_right = GESCHWINDIGKEIT + korrektur

                # Begrenzung der Geschwindigkeiten
                speed_left = max(-50, min(50, speed_left))
                speed_right = max(-50, min(50, speed_right))

                # Motoren ansteuern
                alvik.set_wheels_speed(speed_left, speed_right)

                # Letzte Richtung merken
                if abs(fehler) > 0.05:
                    letzter_fehler = fehler

        # ------------------------------------------
        # Zustand: LINIE_SUCHEN
        # ------------------------------------------
        elif zustand == Zustand.LINIE_SUCHEN:

            if fehler is not None:
                alvik.brake()
                zustand = Zustand.LINIE_FOLGEN
                print("Linie wiedergefunden!")

            else:
                # In zuletzt erkannte Richtung drehen
                if letzter_fehler > 0:
                    alvik.set_wheels_speed(
                        -SUCHGESCHWINDIGKEIT,
                        SUCHGESCHWINDIGKEIT
                    )
                else:
                    alvik.set_wheels_speed(
                        SUCHGESCHWINDIGKEIT,
                        -SUCHGESCHWINDIGKEIT
                    )

        sleep_ms(20)


except KeyboardInterrupt:
    print("Programm beendet")

finally:
    alvik.brake()