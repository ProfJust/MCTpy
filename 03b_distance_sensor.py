from arduino_alvik import ArduinoAlvik
from time import sleep_ms

alvik = ArduinoAlvik()
alvik.begin()

try:
    while True:
        # Fünf horizontale Distanzwerte
        L, CL, C, CR, R = alvik.get_distance()

        # Zwei vertikale Distanzwerte
        T = alvik.get_distance_top()
        B = alvik.get_distance_bottom()
        print(f"L: {L:.1f} | CL: {CL:.1f} | ")
        print(f"C: {C:.1f} | CR: {CR:.1f} | ")
        print(f"R: {R:.1f} | T: {T:.1f} | B: {B:.1f} cm")
        sleep_ms(200)

except KeyboardInterrupt:
    print("Programm beendet")

finally:
    alvik.stop()