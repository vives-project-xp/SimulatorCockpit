import socket
import paho.mqtt.client as mqtt
import hashlib
import threading

# =========================
# CONFIG
# =========================
FG_TCP_IP = "127.0.0.1"
FG_TCP_PORT = 5600

UDP_IP = "127.0.0.1"
UDP_PORT = 5500

MQTT_BROKER = "10.10.232.162"
MQTT_PORT = 1883

# =========================
# TCP CONNECTIE (INPUT)
# =========================
tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_sock.connect((FG_TCP_IP, FG_TCP_PORT))
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

    except ValueError:
        return

    # BELANGRIJK: volgorde moet exact overeenkomen met XML chunks
    datastr = f"{current_battery}:{current_throttle}\n"

    new_hash = hashlib.md5(datastr.encode()).digest()

    if new_hash != old_hash:
        tcp_sock.sendall(datastr.encode("utf-8"))
        print("[TCP SEND]", datastr.strip())
        old_hash = new_hash

# =========================
# MQTT SETUP
# =========================
mqtt_client = mqtt.Client()
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
mqtt_client.subscribe("cockpit/input/battery")
mqtt_client.subscribe("cockpit/input/throttle")
mqtt_client.loop_start()
print("[MQTT] Verbonden met broker")

# =========================
# UDP LISTENER (OUTPUT)
# =========================
def udp_listener():
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.bind((UDP_IP, UDP_PORT))
    print(f"[UDP] Luisteren op {UDP_IP}:{UDP_PORT}")

    while True:
        data, _ = udp_sock.recvfrom(1024)
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            continue

        lines = text.splitlines()
        for line in lines:
            line = line.strip()
            if "=" not in line:
                continue
            key, value_str = line.split("=", 1)
            try:
                value = float(value_str)
            except ValueError:
                continue

            if key == "AIRSPEED":
                mqtt_client.publish("cockpit/airspeed", value)
                # print(f"[MQTT] AIRSPEED = {value}")
            elif key == "HEADING":
                mqtt_client.publish("cockpit/heading", value)
                # print(f"[MQTT] HEADING = {value0.8}")

# Start UDP listener in aparte thread
udp_thread = threading.Thread(target=udp_listener, daemon=True)
udp_thread.start()

# Houd script draaiende
try:
    while True:
        pass
except KeyboardInterrupt:
    print("Stopping bridge")