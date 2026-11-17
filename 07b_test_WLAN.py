
import network
from time import sleep_ms

SSID = "MEIN_WLAN"
PASSWORT = "MEIN_PASSWORT"

wlan = network.WLAN(network.STA_IF)

print("1. WLAN aktivieren")
wlan.active(True)

sleep_ms(1000)

print("2. WLAN verbinden")
wlan.connect(SSID, PASSWORT)

print("3. Warte auf Verbindung")

for i in range(20):
    print("Status:", wlan.status())

    if wlan.isconnected():
        print("WLAN verbunden!")
        print("IP-Adresse:", wlan.ifconfig()[0])
        break

    sleep_ms(500)

print("Test beendet")
