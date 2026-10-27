from enum import Enum

# Zustände definieren
class Zustand(Enum):
    STOP = 0
    FAHREN = 1
    DREHEN = 2
    ENDE = 3

zustand = Zustand.STOP

while zustand != Zustand.ENDE:

    if zustand == Zustand.STOP:
        print("Roboter wartet")
        input("Enter zum Starten")
        zustand = Zustand.FAHREN

    elif zustand == Zustand.FAHREN:
        print("Roboter fährt geradeaus")
        abstand = float(input("Abstand in cm: "))

        if abstand < 10:
            zustand = Zustand.DREHEN

    elif zustand == Zustand.DREHEN:
        print("Roboter dreht sich")
        zustand = Zustand.FAHREN

print("Programm beendet")