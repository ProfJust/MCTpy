from arduino_alvik import ArduinoAlvik
from time import sleep_ms
import math

alvik = ArduinoAlvik()
alvik.begin()

# Auf Check-Taste warten
print("Check-Taste zum Starten drücken")

while not alvik.get_touch_ok():
    sleep_ms(50)

# Odometrie zurücksetzen
alvik.reset_pose(0, 0, 0)

try:
    # -----------------------------------
    # 1. 20 cm geradeaus fahren
    # -----------------------------------
    print("Fahre 20 cm geradeaus")

    while True:
        x, y, theta = alvik.get_pose()

        strecke = math.sqrt(x**2 + y**2)

        if strecke >= 20:
            break

        alvik.set_wheels_speed(30, 30)
        sleep_ms(20)

    alvik.brake()
    sleep_ms(500)

    # -----------------------------------
    # 2. 90 Grad nach links drehen
    # -----------------------------------
    print("Drehe 90 Grad")

    alvik.reset_pose(0, 0, 0)

    while True:
        x, y, theta = alvik.get_pose()

        if theta >= 90:
            break

        alvik.set_wheels_speed(-20, 20)
        sleep_ms(20)

    alvik.brake()
    print("Fertig!")

finally:
    alvik.brake()