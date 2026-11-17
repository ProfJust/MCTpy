
from machine import Pin, I2C
import ssd1306

# I2C-Schnittstelle Arduino Alvik
i2c = I2C(0, scl=Pin(12), sda=Pin(11),
          freq=100000)

# OLED initialisieren
oled = ssd1306.SSD1306_I2C(
    128, 64, i2c, addr=0x3C
)

# Bildschirm löschen
oled.fill(0)

# Texte schreiben
oled.text("Arduino Alvik", 4, 4)
oled.text("Hallo MCTpy !", 4, 20)
oled.text("MicroPython", 4, 36)

# Rahmen über FrameBuffer zeichnen
# oled.framebuf.rect(0, 0, 128, 64, 1)
oled.rect(0, 0, 128, 64, 1)

# Ausgabe aktualisieren
oled.show()

print("OLED-Test abgeschlossen")
