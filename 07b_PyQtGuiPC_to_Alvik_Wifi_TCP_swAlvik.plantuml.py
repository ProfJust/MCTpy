
@startuml
title Arduino Alvik - WLAN-TCP-Steuerung

start

:Arduino Alvik initialisieren;
:Beide Räder stoppen;

:WLAN aktivieren;
:Mit Access Point verbinden;

if (WLAN verbunden?) then (Ja)
  :IP-Adresse ausgeben;
else (Nein)
  :Maximal 15 Sekunden warten;
  if (Verbindung hergestellt?) then (Ja)
    :IP-Adresse ausgeben;
  else (Nein)
    :RuntimeError;
    stop
  endif
endif

:TCP-Server auf Port 5000 starten;

while (Server läuft?) is (Ja)
  :Auf TCP-Client warten;
  :Verbindung annehmen;
  :Buffer und Watchdog initialisieren;

  while (Client verbunden?) is (Ja)
    :Mit select() auf Daten prüfen;

    if (Daten vorhanden?) then (Ja)
      :Bytes empfangen;

      if (Verbindung geschlossen oder Buffer zu lang?) then (Ja)
        break
      endif

      if (Komplette Nachricht vorhanden?) then (Ja)
        :Nachricht dekodieren;
        :Radgeschwindigkeiten prüfen;

        if (Gültige Werte?) then (Ja)
          :Radgeschwindigkeiten setzen;
          :Watchdog zurücksetzen;
        endif
      endif
    endif

    if (Watchdog > 500 ms?) then (Ja)
      :Beide Räder stoppen;
    endif
  endwhile (Nein)

  :Beide Räder stoppen;
  :Client-Socket schließen;
endwhile (Nein)

:Server schließen;
:Beide Räder stoppen;

stop
@enduml
