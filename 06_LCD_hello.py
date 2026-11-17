from machine import Pin, I2C
from time import sleep_ms

# I2C-Schnittstelle des Alvik
i2c = I2C(0, scl=Pin(12), sda=Pin(11),
          freq=100000)

LCD_ADDR = 0x3E

# Kommando an das LCD senden
def lcd_cmd(cmd):
    i2c.writeto(LCD_ADDR, bytes([0x80, cmd]))
    sleep_ms(2)

# Einzelnes Zeichen senden
def lcd_data(char):
    i2c.writeto(LCD_ADDR, bytes([0x40, ord(char)]))

# LCD initialisieren
def lcd_init():
    sleep_ms(100)
    lcd_cmd(0x38)  # 8 Bit, 2 Zeilen
    lcd_cmd(0x39)  # Erweiterte Befehle
    lcd_cmd(0x14)  # Bias/Oszillator
    lcd_cmd(0x70)  # Kontrast
    lcd_cmd(0x56)  # Spannungsfolger
    lcd_cmd(0x6C)  # Spannungsfolger ein
    sleep_ms(200)
    lcd_cmd(0x38)  # Normalmodus
    lcd_cmd(0x0C)  # Display ein
    lcd_cmd(0x01)  # Display löschen
    sleep_ms(5)

# Text an Position ausgeben
def lcd_text(zeile, text):
    adresse = 0x80 if zeile == 0 else 0xC0
    lcd_cmd(adresse)

    for zeichen in text[:16].ljust(16):
        lcd_data(zeichen)


# Hauptprogramm
lcd_init()

lcd_text(0, "Arduino Alvik")
lcd_text(1, "Hallo Welt!")

print("LCD initialisiert")
