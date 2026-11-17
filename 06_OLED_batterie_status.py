
from machine import Pin, I2C
from time import sleep_ms
from arduino_alvik import ArduinoAlvik
import ssd1306


# --------------------------------------------------
# Eigene Grafikfunktionen
# --------------------------------------------------

def hline(x, y, breite, farbe=1):
    """Horizontale Linie zeichnen."""
    for i in range(breite):
        oled.pixel(x + i, y, farbe)


def rect(x, y, breite, hoehe, farbe=1):
    """Rechteck zeichnen."""
    for i in range(breite):
        oled.pixel(x + i, y, farbe)
        oled.pixel(x + i, y + hoehe - 1, farbe)

    for i in range(hoehe):
        oled.pixel(x, y + i, farbe)
        oled.pixel(x + breite - 1, y + i, farbe)


def fill_rect(x, y, breite, hoehe, farbe=1):
    """Gefülltes Rechteck zeichnen."""
    for dy in range(hoehe):
        for dx in range(breite):
            oled.pixel(x + dx, y + dy, farbe)


# --------------------------------------------------
# Arduino Alvik initialisieren
# --------------------------------------------------

alvik = ArduinoAlvik()
alvik.begin()

# Warten auf erste Sensorwerte
sleep_ms(3000)


# --------------------------------------------------
# Grove OLED initialisieren
# --------------------------------------------------

i2c = I2C(
    0,
    scl=Pin(12),
    sda=Pin(11),
    freq=100000
)

oled = ssd1306.SSD1306_I2C(
    128, 64, i2c, addr=0x3C
)

batterie = None


# --------------------------------------------------
# Hauptprogramm
# --------------------------------------------------

try:
    while True:

        # Batterie abfragen
        try:
            wert = alvik.get_battery_charge()

            if wert is not None and 0 < wert <= 100:
                batterie = wert

        except (TypeError, ValueError):
            pass

        # OLED löschen
        oled.fill(0)

        # Überschrift
        oled.text("Arduino Alvik", 0, 0)
        hline(0, 12, 128)

        # Batteriewert anzeigen
        oled.text("Akku:", 0, 24)

        if batterie is not None:

            oled.text(
                str(round(batterie)) + " %",
                50, 24
            )

            # Batteriebalken zeichnen
            rect(0, 45, 102, 12)

            fill_rect(
                1, 46,
                int(batterie),
                10
            )

        else:
            oled.text("Warte auf Daten", 0, 40)

        # Display aktualisieren
        oled.show()

        sleep_ms(1000)

except KeyboardInterrupt:
    print("Programm beendet")

finally:
    alvik.stop()
