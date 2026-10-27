# Tasten TEsten
from arduino_alvik import ArduinoAlvik
import time

alvik = ArduinoAlvik()
alvik.begin()

print("X-Taste testen")

while True:
    print(alvik.get_touch_cancel())
    time.sleep_ms(200)