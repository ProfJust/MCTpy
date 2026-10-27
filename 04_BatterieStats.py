from arduino_alvik import ArduinoAlvik
from time import sleep_ms

alvik = ArduinoAlvik()
alvik.begin()

sleep_ms(2000)

soc_alt = None
print(f"Batterieladung anzeigen - SOC ")

while True:
    soc = alvik.get_battery_charge()

    if soc is not None and soc > 0 and soc is not soc_alt:
        soc_alt = soc
        print(f"Batterie zu {soc} % geladen")
    # else:
    #     print(f"Ungültiger Wert: {soc}", end ="")
    #     print(f" Letzter gültiger Wert: {soc_alt}")

    # sleep_ms(1000)
    sleep_ms(10)