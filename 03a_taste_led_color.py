
from arduino_alvik import ArduinoAlvik
from time import sleep_ms

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

try:
    while True:
        if alvik.get_touch_up() and not touch_up_flag:
            touch_up_flag = True  # Taste merken
            # Nächste Farbe auswählen
            farbe_index = (farbe_index + 1) % len(farben)

            # Neue Farbe einstellen
            alvik.left_led.set_color(*farben[farbe_index])

            print("Farbe:", farbe_index)

        if not alvik.get_touch_up():  # Wenn Taste losgelassen
          touch_up_flag = False  # Tastenmerker reset

        sleep_ms(10)

except KeyboardInterrupt:
    print("Programm beendet")

finally:
    alvik.left_led.set_color(0, 0, 0)
    alvik.stop()
