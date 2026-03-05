import socket
import paho.mqtt.client as mqtt
import hashlib

# =========================
# CONFIG
# =========================
FGADDR = "127.0.0.1"
FGPORT = 5600

MQTT_BROKER = "mqtt.devbit.be"
MQTT_PORT = 1883

# =========================
# TCP CONNECTIE NAAR FG
# =========================
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((FGADDR, FGPORT))
print("[TCP] Verbonden met FlightGear")

# =========================
# STATE
# =========================
current_battery = 0
current_throttle = 0.0
old_hash = b""

# =========================
# MQTT CALLBACK
# =========================
def on_message(client, userdata, msg):
    global current_battery, current_throttle, old_hash

    topic = msg.topic
    payload = msg.payload.decode().strip()

    try:
        if topic == "cockpit/input/battery":
            current_battery = int(payload)
        elif topic == "cockpit/input/throttle":
            current_throttle = float(payload)
    except:
        return

    # Combineer waarden in juiste volgorde voor FG
    datastr = f"{current_battery}:{current_throttle}\n"

    # Alleen sturen als iets veranderd is
    new_hash = hashlib.md5(datastr.encode()).digest()
    if new_hash != old_hash:
        sock.sendall(datastr.encode("utf-8"))
        print("[SEND]", datastr.strip())
        old_hash = new_hash

# =========================
# MQTT SETUP
# =========================
mqtt_client = mqtt.Client()
mqtt_client.on_message = on_message

mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
mqtt_client.subscribe("cockpit/input/battery")
mqtt_client.subscribe("cockpit/input/throttle")

mqtt_client.loop_forever()