# Raspberry Pi

Deze map bevat de Pi-kant van het cockpitproject:

- `buttons.py`: leest GPIO-inputs en publiceert ze via MQTT
- `interface.py`: cockpitinterface voor het scherm
- `docker-compose.pi5.yml`: Pi 5 setup met Mosquitto en `buttons.py`
- `docker-compose.pi4.yml`: Pi 4 setup voor de interface

## Python setup zonder Docker

Maak een virtual environment aan met toegang tot system packages voor GPIO:

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

## Mosquitto zonder Docker

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
