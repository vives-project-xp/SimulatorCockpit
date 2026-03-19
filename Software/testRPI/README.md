## Stap 1
maak een virtual environment aan.

```bash
python3 -m venv venv
```

Dat maakt een virtual environment aan in een map `venv`.

**Activeren:**

```bash
source venv/bin/activate
```

**Afsluiten:**

```bash
deactivate
```

Als `venv` nog niet beschikbaar is op je Pi:

```bash
sudo apt update
sudo apt install python3-venv
```

## Stap 2


Installeren in je venv;

```bash
pip install paho-mqtt
```



Je kunt het testen als alles correct is geïnstalleerd met dit commando;

```bash
python3 -c "import tkinter; import paho.mqtt.client as mqtt; print('ok')"
```

Als `tkinter` niet werkt, installeer je het systeempakket:

```bash
sudo apt update
sudo apt install python3-tk
```





## Stap 3 - Broker aanmaken op Pi

Op je Pi:

```bash
sudo apt update
sudo apt install mosquitto mosquitto-clients -y
```

---

Start de broker

```bash
sudo systemctl start mosquitto
```

Check of hij draait:

```bash
sudo systemctl status mosquitto
```

Je wil iets zien als:

```
active (running)
```

---

 Automatisch laten starten bij boot

```bash
sudo systemctl enable mosquitto
```

---



**⚠️ (BELANGRIJK) Default security gedrag**

Nieuwe Mosquitto versies blokkeren vaak externe toegang.


### Config aanpassen:

```bash
sudo nano /etc/mosquitto/mosquitto.conf
```

Voeg onderaan toe:

```bash
listener 1883
allow_anonymous true
```

Opslaan → dan:

```bash
sudo systemctl restart mosquitto
```

---

