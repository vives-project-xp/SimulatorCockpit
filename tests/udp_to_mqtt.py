import socket
import paho.mqtt.client as mqtt

# =========================
# CONFIG
# =========================
UDP_IP = "127.0.0.1"
UDP_PORT = 5500

MQTT_BROKER = "mqtt.devbit.be"
MQTT_PORT = 1883
MQTT_CLIENT_ID = "flightgear-udp-bridge"

# =========================
# MQTT SETUP
# =========================
mqtt_client = mqtt.Client(client_id=MQTT_CLIENT_ID, protocol=mqtt.MQTTv311)
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
mqtt_client.loop_start()

print(f"[MQTT] Verbonden met {MQTT_BROKER}")

# =========================
# UDP SETUP
# =========================
udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_sock.bind((UDP_IP, UDP_PORT))

print(f"[UDP] Luisteren op {UDP_IP}:{UDP_PORT}")

# =========================
# MAIN LOOP
# =========================
while True:
    data, _ = udp_sock.recvfrom(1024)

    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        continue

    # Eén UDP packet kan meerdere regels bevatten
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
            print(f"[DATA] AIRSPEED = {value}")

        elif key == "HEADING":
            mqtt_client.publish("cockpit/heading", value)
            print(f"[DATA] HEADING = {value}")
