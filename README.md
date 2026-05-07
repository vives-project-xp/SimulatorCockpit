# Simulator Cockpit

Simulator Cockpit is een schoolproject rond een fysieke cockpit die met FlightGear praat via MQTT, GPIO en custom socket protocols.

## Structuur

- `Software/Flightgear_PC`: bridge tussen FlightGear, MQTT en cockpitinputs
- `Software/RPI`: code en Docker setup voor de Raspberry Pi knoppen en broker
- `install`: installatiescripts voor Pi 4 en Pi 5
- `Documentatie`: schema's, extra nota's en demo-materiaal

## Snel starten

Voor de pc-kant:

- [Software/Flightgear_PC/README.md](Software/Flightgear_PC/README.md)

Voor de Raspberry Pi:

- [install/README.md](install/README.md)
- [Software/RPI/README.md](Software/RPI/README.md)
