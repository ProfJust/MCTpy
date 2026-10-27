from arduino_alvik import ArduinoAlvik
from time import sleep_ms
from enum import Enum

class Zustand(Enum):
    FAHREN = 1
    DREHEN = 2

alvik = ArduinoAlvik()
alvik.begin()

zustand = Zustand.FAHREN

try:
    while True:

        if zustand == Zustand.FAHREN:
            abstand = alvik.get_distance()[1]

            if 0 < abstand < 10:
                alvik.brake()
                zustand = Zustand.DREHEN
            else:
                alvik.set_wheels_speed(30, 30)

        elif zustand == Zustand.DREHEN:
            alvik.set_wheels_speed(-20, 20)
            sleep_ms(1000)
            alvik.brake()
            zustand = Zustand.FAHREN

        sleep_ms(50)

except KeyboardInterrupt:
    alvik.brake()