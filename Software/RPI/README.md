# Raspberry Pi

Deze map bevat de Pi-kant van het cockpitproject:

- `buttons.py`: leest GPIO-inputs en publiceert ze via MQTT
- `interface.py`: cockpitinterface voor het scherm
- `docker-compose.pi5.yml`: Pi 5 setup met Mosquitto en `buttons.py`
- `docker-compose.pi4.yml`: Pi 4 setup voor de interface

## Belangrijk

Voor dit project is Docker de standaardmanier om alles te starten.

Je hoeft dus normaal gezien **niet** zelf een virtual environment te maken, **niet** handmatig `mosquitto` te installeren, en **niet** apart `buttons.py` te starten.

Gebruik gewoon de Docker setup.

## Pi 5 starten met Docker

Vanaf de root van de repo:

```bash
cd ~/SimCockpit/SimulatorCockpit
bash install/pi5.sh
```

Dit script doet:

- Docker installeren als het nog niet bestaat
- Docker automatisch laten starten bij boot
- de MQTT broker starten
- `buttons.py` starten
- alles via Docker Compose opzetten

Na installatie kun je de status bekijken met:

```bash
cd ~/SimCockpit/SimulatorCockpit/Software/RPI
docker compose -f docker-compose.pi5.yml ps
docker compose -f docker-compose.pi5.yml logs -f
```

Als Docker nog `sudo` nodig heeft:

```bash
sudo docker compose -f docker-compose.pi5.yml ps
sudo docker compose -f docker-compose.pi5.yml logs -f
```

## Pi 4 starten met Docker

Voor de Pi 4 interface:

```bash
cd ~/SimCockpit/SimulatorCockpit
bash install/pi4.sh
```

De Pi 4 moet de Pi 5 broker kunnen bereiken op `10.10.229.190:1883`.

## Handmatig starten zonder Docker

Doe dit alleen als je bewust zonder Docker wil werken.

### Python omgeving

```bash
python3 -m venv --system-site-packages venv
source venv/bin/activate
pip install -r requirements.txt
```

Als `venv` nog niet beschikbaar is:

```bash
sudo apt update
sudo apt install python3-venv
```

Snelle test:

```bash
python3 -c "import tkinter; import paho.mqtt.client as mqtt; print('ok')"
```

Als `tkinter` ontbreekt:

```bash
sudo apt update
sudo apt install python3-tk
```

### Mosquitto zonder Docker

```bash
sudo apt update
sudo apt install mosquitto mosquitto-clients -y
sudo systemctl start mosquitto
sudo systemctl enable mosquitto
```

Controle:

```bash
sudo systemctl status mosquitto
```

Je wil `active (running)` zien.

Als externe toegang geblokkeerd is, pas dan `/etc/mosquitto/mosquitto.conf` aan:

```text
listener 1883
allow_anonymous true
```

en herstart:

```bash
sudo systemctl restart mosquitto
```

## Hardware opmerking

Voor de ADC/ADS1115: gebruik `3.3V`, niet `5V`.
