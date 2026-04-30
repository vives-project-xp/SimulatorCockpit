# Installatie op verse Raspberry Pi

Deze scripts zijn bedoeld voor een nieuwe Raspberry Pi OS flash waar de repo al op staat.

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

De Pi 4 moet de Pi 5 broker kunnen bereiken op `10.10.229.190:1883`.

## Eerste test

Op de Pi 5:

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
