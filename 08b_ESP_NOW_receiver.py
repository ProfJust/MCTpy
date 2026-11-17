
import network
import espnow

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

e = espnow.ESPNow()
e.active(True)

print("Warte auf ESP-NOW-Nachrichten")

while True:
    host, msg = e.recv()

    if msg:
        print("Empfangen:", msg.decode())
