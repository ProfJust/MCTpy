
import subprocess
import socket
import platform
import re
import ipaddress
from concurrent.futures import ThreadPoolExecutor, as_completed

# --------------------------------------------------
# Einstellungen
# --------------------------------------------------
SUBNETZ = "192.168.0.0/24"
MAX_THREADS = 40


# --------------------------------------------------
# IP-Adresse anpingen
# --------------------------------------------------
def ping(ip):
    system = platform.system().lower()

    if system == "windows":
        befehl = ["ping", "-n", "1", "-w", "500", ip]
    else:
        befehl = ["ping", "-c", "1", "-W", "1", ip]

    try:
        ergebnis = subprocess.run(
            befehl,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=2
        )
        return ergebnis.returncode == 0
    except (subprocess.TimeoutExpired, OSError):
        return False


# --------------------------------------------------
# Hostname ermitteln
# --------------------------------------------------
def hostname_ermitteln(ip):
    try:
        hostname, _, _ = socket.gethostbyaddr(ip)
        return hostname
    except (socket.herror, socket.gaierror, OSError):
        return "Unbekannt"


# --------------------------------------------------
# MAC-Adresse aus ARP-Tabelle ermitteln
# --------------------------------------------------
def mac_ermitteln(ip):
    try:
        ergebnis = subprocess.run(
            ["arp", "-a", ip],
            capture_output=True,
            text=True,
            timeout=3
        )

        muster = (
            r"\b" + re.escape(ip) +
            r"\s+([0-9a-fA-F]{2}(?:[:-][0-9a-fA-F]{2}){5})\b"
        )

        treffer = re.search(muster, ergebnis.stdout)

        if treffer:
            return treffer.group(1)

    except (subprocess.TimeoutExpired, OSError):
        pass

    return "Unbekannt"


# --------------------------------------------------
# Einzelnes Gerät untersuchen
# --------------------------------------------------
def geraet_scannen(ip):
    if ping(ip):
        hostname = hostname_ermitteln(ip)
        mac = mac_ermitteln(ip)

        return ip, hostname, mac

    return None


# --------------------------------------------------
# Hauptprogramm
# --------------------------------------------------
def main():
    netz = ipaddress.ip_network(SUBNETZ)

    print(f"\nScanne Netzwerk: {SUBNETZ}")
    print("-" * 85)
    print(f"{'IP-Adresse':<18} {'Hostname':<40} {'MAC-Adresse':<20}")
    print("-" * 85)

    gefundene_geraete = []

    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:

        aufgaben = {
            executor.submit(geraet_scannen, str(ip)): str(ip)
            for ip in netz.hosts()
        }

        for aufgabe in as_completed(aufgaben):
            ergebnis = aufgabe.result()

            if ergebnis:
                gefundene_geraete.append(ergebnis)

    # Numerisch nach IP-Adresse sortieren
    gefundene_geraete.sort(
        key=lambda eintrag: ipaddress.ip_address(eintrag[0])
    )

    for ip, hostname, mac in gefundene_geraete:
        print(f"{ip:<18} {hostname:<40} {mac:<20}")

    print("-" * 85)
    print(f"Gefundene Geräte: {len(gefundene_geraete)}")


if __name__ == "__main__":
    main()
