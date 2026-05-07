# Installatie op verse Raspberry Pi

Deze scripts zijn bedoeld voor een nieuwe Raspberry Pi OS flash waar de repo al op staat.

## Belangrijk

De namen `pi4` en `pi5` in deze repo verwijzen vooral naar de **rol** van de Raspberry Pi in het project:

- `pi5`: de Pi die de **knoppen en MQTT broker** draait
- `pi4`: de Pi die de **interface op het scherm** draait

Je kunt die rollen in principe ook op een andere Raspberry Pi uitvoeren, zolang de hardware past bij de taak:

- de **buttons/broker Pi** moet GPIO kunnen gebruiken
- de **interface Pi** moet een desktop/display omgeving hebben

## Pi 5: broker + knoppen

```bash
cd ~/SimCockpit/SimulatorCockpit
bash install/pi5.sh
```

Dit doet:

- Docker installeren als het nog niet bestaat
- Docker automatisch laten starten bij boot
- MQTT broker en `buttons.py` starten via Docker Compose
- Containers op `restart: unless-stopped` zetten via de Compose file

Na reboot:

```bash
cd ~/SimCockpit/SimulatorCockpit/Software/RPI
docker compose -f docker-compose.pi5.yml ps
docker compose -f docker-compose.pi5.yml logs -f
```

## Pi 4: interface scherm

```bash
cd ~/SimCockpit/SimulatorCockpit
bash install/pi4.sh
```

Dit doet:

- Docker installeren als het nog niet bestaat
- De interface Docker image bouwen
- Een desktop autostart entry maken
- De interface starten na grafische login

De interface-Pi moet de broker-Pi kunnen bereiken op `10.10.229.190:1883`.

## Eerste test

Op de broker/knoppen-Pi:

```bash
cd ~/SimCockpit/SimulatorCockpit/Software/RPI
docker compose -f docker-compose.pi5.yml logs -f
```

In een tweede terminal:

```bash
sudo apt install -y mosquitto-clients
mosquitto_sub -h localhost -t 'cockpit/#' -v
```

Druk op een knop. Je zou MQTT berichten moeten zien verschijnen.
