
from machine import Pin, I2C
from time import sleep_ms

i2c = I2C(0, scl=Pin(12), sda=Pin(11),
          freq=100000)

RGB_ADDR = 0x62

def rgb_write(register, wert):
    i2c.writeto(RGB_ADDR, bytes([register, wert]))

def set_rgb(r, g, b):
    rgb_write(0x00, 0x00)
    rgb_write(0x01, 0x00)
    rgb_write(0x08, 0xAA)

    rgb_write(0x04, r)
    rgb_write(0x03, g)
    rgb_write(0x02, b)

# Farbtest
set_rgb(255, 0, 0)
print("ROT")
sleep_ms(2000)

set_rgb(0, 255, 0)
print("GRUEN")
sleep_ms(2000)

set_rgb(0, 0, 255)
print("BLAU")
sleep_ms(2000)

set_rgb(255, 255, 255)
print("WEISS")
