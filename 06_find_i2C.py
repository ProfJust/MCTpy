
from machine import Pin, I2C

# I2C-Bus des Arduino Alvik initialisieren
i2c = I2C(0, scl=Pin(12), sda=Pin(11), freq=100000)

# Angeschlossene I2C-Geräte suchen
geraete = i2c.scan()

print("Gefundene I2C-Geräte:")

if len(geraete) == 0:
    print("Kein I2C-Gerät gefunden!")
else:
    for adresse in geraete:
        print("Adresse:", hex(adresse))
