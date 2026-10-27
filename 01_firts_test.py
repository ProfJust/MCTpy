from arduino_alvik import ArduinoAlvik
from time import sleep
from time import sleep_ms

print("Start, wenn BEGIN nicht OK ist, prüfen ob Schutzfolie an der Alvik-Batterie entfernt?")
alvik = ArduinoAlvik()
print("Objekt OK")
sleep(2)

print("begin...")
alvik.begin()
print("BEGIN OK")
print("Library:", alvik.get_lib_version())
print("Firmware:", alvik.get_fw_version())
# Test LED #
print("Lasse DL1 und DL2 anwechselnd blinken")
print("Drücke beliebige Taste zum Beenden")
while True:
   # DL1 an, DL2 aus
    alvik.left_led.set_color(1, 0, 0)
    alvik.right_led.set_color(0, 0, 0)
    # Prüfen, ob X gedrückt wurde
    if alvik.get_touch_any():
        break
    sleep_ms(500)

    # DL1 aus, DL2 an
    alvik.left_led.set_color(0, 0, 0)
    alvik.right_led.set_color(0, 0, 1)
    # Prüfen, ob X gedrückt wurde
    if alvik.get_touch_any():
        break
    sleep_ms(500)


print("Programm beendet")