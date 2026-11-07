from arduino_alvik import ArduinoAlvik
from time import sleep_ms
 
 
def main():
    alvik = ArduinoAlvik()
    alvik.begin()
    print("Alvik ist bereit")
 
    try:
        sleep_ms(2000)
        alvik.set_wheels_speed(30, 30)
        sleep_ms(3000)
    finally:
        alvik.brake()
        print("Alvik gestoppt")
 
 
if __name__ == "__main__":
    main()
