
from machine import Pin, I2C
from time import sleep_ms

import network
import espnow

# -------------------------------------------
# I2C-Konfiguration XIAO ESP32-S3
# -------------------------------------------
SDA_PIN = 5       # D4
SCL_PIN = 6       # D5
NUNCHUCK_ADDR = 0x52

i2c = I2C(
    0,
    sda=Pin(SDA_PIN),
    scl=Pin(SCL_PIN),
    freq=100000
)

# -------------------------------------------
# Nunchuck initialisieren
# -------------------------------------------
def nunchuck_init():
    devices = i2c.scan()
    print("I2C-Geräte:", [hex(x) for x in devices])

    if NUNCHUCK_ADDR not in devices:
        raise OSError("Nunchuck nicht gefunden!")

    # Unverschlüsselte Datenübertragung aktivieren
    i2c.writeto(NUNCHUCK_ADDR, b'\xF0\x55')
    sleep_ms(10)
    i2c.writeto(NUNCHUCK_ADDR, b'\xFB\x00')
    sleep_ms(10)

    print("Nunchuck initialisiert")


# -------------------------------------------
# Nunchuck auslesen
# -------------------------------------------
def nunchuck_read():

    # Neue Messung anfordern
    i2c.writeto(NUNCHUCK_ADDR, b'\x00')
    sleep_ms(5)

    # 6 Datenbytes lesen
    data = i2c.readfrom(NUNCHUCK_ADDR, 6)

    # Joystick
    joy_x = data[0]
    joy_y = data[1]

    # Beschleunigung (10 Bit)
    acc_x = (data[2] << 2) | ((data[5] >> 2) & 0x03)
    acc_y = (data[3] << 2) | ((data[5] >> 4) & 0x03)
    acc_z = (data[4] << 2) | ((data[5] >> 6) & 0x03)

    # Taster (aktiv LOW)
    button_z = not bool(data[5] & 0x01)
    button_c = not bool(data[5] & 0x02)

    return joy_x, joy_y, acc_x, acc_y, acc_z, button_c, button_z


# -------------------------------------------
# Hauptprogramm
# -------------------------------------------
nunchuck_init()
# ---- esp_now_init()
# WLAN-Funkhardware aktivieren
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

# ESP-NOW initialisieren
# s.o. import network
# s.o. import espnow
e = espnow.ESPNow()
e.active(True)

# MAC-Adresse des Empfängers eintragen
alvik01 =  b'\x3C\x84\x27\xC4\x32\xC0'
e.add_peer(alvik01)


while True:
    try:
        x, y, ax, ay, az, c, z = nunchuck_read()

        nun_str = f"Joystick: X={x:3d} Y={y:3d} Accel: X={ax:4d} Y={ay:4d} Z={az:4d} C={int(c)} Z={int(z)}"
        print(nun_str)
        # print(
        #     f"Joystick: X={x:3d} Y={y:3d} | "
        #     f"Accel: X={ax:4d} Y={ay:4d} Z={az:4d} | "
        #     f"C={int(c)} Z={int(z)}"
        # )
        e.send(alvik01, nun_str )

        sleep_ms(100)

    except OSError as e:
        print("I2C-Fehler:", e)
        sleep_ms(500)
