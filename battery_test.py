
from arduino_alvik import ArduinoAlvik
from time import sleep_ms

alvik = ArduinoAlvik()
alvik.begin()

sleep_ms(1000)

while True:
    try:
        batterie = alvik.get_battery_charge()
        print("Batterie:", batterie)
    except (TypeError, ValueError) as e:
        print("Fehler bei Batterieabfrage:", e)

    sleep_ms(1000)
