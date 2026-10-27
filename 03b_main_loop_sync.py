
from arduino_alvik import ArduinoAlvik
from time import ticks_ms, ticks_diff, sleep_ms
# PERIODE_MS = 10

alvik = ArduinoAlvik()
alvik.begin()

# Farben als RGB-Tupel
farben = [
    (1, 0, 0),  # Rot
    (0, 1, 0),  # Grün
    (0, 0, 1),  # Blau
    (1, 1, 1)   # Weiß
]

farbe_index = 0

# Anfangsfarbe Rot
alvik.left_led.set_color(*farben[farbe_index])

print("Up-Taste: LED-Farbe wechseln")

touch_up_flag = False   # Tastenmerker

PERIODE_MS = 10
try:
    while True:
        startzeit = ticks_ms()
        aktuelle_zeit = ticks_ms()
        if alvik.get_touch_up() and not touch_up_flag:
            touch_up_flag = True  # Taste merken
            # Nächste Farbe auswählen
            farbe_index = (farbe_index + 1) % len(farben)

            # Neue Farbe einstellen
            alvik.left_led.set_color(*farben[farbe_index])

            print("Farbe:", farbe_index)

        if not alvik.get_touch_up():  # Wenn Taste losgelassen
          touch_up_flag = False  # Tastenmerker reset

        # Synchronisierung, warte bis PERIODE_MS erreicht
        while ticks_diff(ticks_ms(), startzeit) <= PERIODE_MS:
            dauer = ticks_diff(ticks_ms(), startzeit)

        print(f"Vergangene Zeit: {dauer} ms")

except KeyboardInterrupt:  # STRG+C im REPL
    print("Programm beendet")

finally:
    alvik.left_led.set_color(0, 0, 0)
    alvik.stop()
