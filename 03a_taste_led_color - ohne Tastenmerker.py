
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

"""Das * ist in Python der sogenannte Unpacking-Operator (Entpackungsoperator).
Er sorgt dafür, dass die einzelnen Elemente einer Liste oder eines Tupels 
als separate Argumente an eine Funktion übergeben werden.
Schrittweise Erklärung:
1. farben[farbe_index] liefert das Tupel (1, 0, 0).
2. Der Operator * entpackt das Tupel in drei einzelne Werte.
3. Diese Werte werden als drei Argumente an set_color() übergeben.
Die beiden folgenden Aufrufe sind somit gleichwertig:
    # Mit Unpacking
    alvik.left_led.set_color(*farben[0])
    # Ohne Unpacking
    alvik.left_led.set_color(1, 0, 0)
"""

print("Up-Taste: LED-Farbe wechseln")

try:
    while True:
        if alvik.get_touch_up():
            # Nächste Farbe auswählen
            farbe_index = (farbe_index + 1) % len(farben)

            # Neue Farbe einstellen
            alvik.left_led.set_color(*farben[farbe_index])

            print("Farbe:", farbe_index)

        sleep_ms(5)  # Hauptschleife

except KeyboardInterrupt:
    print("Programm beendet")

finally:
    alvik.left_led.set_color(0, 0, 0)
    alvik.stop()
