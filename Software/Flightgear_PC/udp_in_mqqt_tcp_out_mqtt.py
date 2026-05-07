import socket
import paho.mqtt.client as mqtt
import hashlib
import threading
import time
import os


# =========================
# CONFIG
# =========================
FG_TCP_IP = os.getenv("FG_TCP_IP", "127.0.0.1")
FG_TCP_PORT = int(os.getenv("FG_TCP_PORT", "5600"))

UDP_IP = os.getenv("UDP_IP", "127.0.0.1")
UDP_PORT = int(os.getenv("UDP_PORT", "5500"))

MQTT_BROKER = os.getenv("MQTT_BROKER", "10.10.229.190")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
PRIMER_TOPICS = ("cockpit/input/primer-lever", "cockpit/input/primer")
PRIMER_RESET_SECONDS = 5.0
MAGNETOS_ENABLE_TOPIC = "cockpit/input/magnetos/sleutel"
MAGNETOS_SWITCH_TOPICS = {
    "cockpit/input/magnetos/switch1": 1,
    "cockpit/input/magnetos/switch2": 2,
    "cockpit/input/magnetos/switch3": 3,
}

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
current_master_alt = 0
current_carb_heat = 0
current_primer_lever = 0
current_primer = 0
primer_reset_timer = None
current_magnetos_enabled = 0
current_magnetos_switches = {
    1: 0,
    2: 0,
    3: 0,
}
current_magnetos = 0
current_starter = False
current_fuel_mixture = 0.0
current_attitude_pitch = 0.0
current_attitude_roll = 0.0
old_hash = b""

# =========================
# MQTT CALLBACK
# =========================
def calculate_magnetos():
    if current_magnetos_switches[3] == 1:
        return 3

    if current_magnetos_enabled == 0:
        return 0

    if current_magnetos_switches[2] == 1:
        return 2

    if current_magnetos_switches[1] == 1:
        return 1

    return 3


def calculate_starter():
    return current_magnetos_enabled == 1 and current_magnetos_switches[3] == 1


def reset_primer_state():
    global current_primer, primer_reset_timer
    current_primer = 0
    primer_reset_timer = None


def sync_primer_reset_timer(previous_starter, current_starter):
    global primer_reset_timer

    if previous_starter == current_starter:
        return

    if primer_reset_timer is not None:
        primer_reset_timer.cancel()
        primer_reset_timer = None

    if previous_starter and not current_starter:
        primer_reset_timer = threading.Timer(PRIMER_RESET_SECONDS, reset_primer_state)
        primer_reset_timer.daemon = True
        primer_reset_timer.start()


def on_message(client, userdata, msg):
    global current_battery, current_master_alt, current_carb_heat, current_primer_lever, current_primer
    global current_magnetos_enabled, current_magnetos, current_starter, current_fuel_mixture, old_hash

    topic = msg.topic
    payload = msg.payload.decode().strip()

    try:
        if topic == "cockpit/input/battery":
            current_battery = int(payload)

        elif topic in ("cockpit/input/master-alt", "cockpit/input/alt"):
            current_master_alt = int(payload)

        elif topic == "cockpit/input/carb-heat":
            current_carb_heat = int(payload)

        elif topic in PRIMER_TOPICS:
            new_primer_lever = int(payload)
            if current_primer_lever == 1 and new_primer_lever == 0:
                current_primer += 1
            current_primer_lever = new_primer_lever

        elif topic == MAGNETOS_ENABLE_TOPIC:
            current_magnetos_enabled = int(payload)

        elif topic in MAGNETOS_SWITCH_TOPICS:
            switch_number = MAGNETOS_SWITCH_TOPICS[topic]
            current_magnetos_switches[switch_number] = int(payload)

        elif topic == "cockpit/input/fuelmixer":
            current_fuel_mixture = float(payload)

    except ValueError:
        return

    current_magnetos = calculate_magnetos()
    previous_starter = current_starter
    current_starter = calculate_starter()
    sync_primer_reset_timer(previous_starter, current_starter)
    starter_value = "1" if current_starter else "0"

    # BELANGRIJK: volgorde moet exact overeenkomen met XML chunks
    datastr = (
        f"{current_battery}:{current_master_alt}:{current_carb_heat}:"
        f"{current_primer_lever}:{current_primer}:{current_magnetos}:{starter_value}:{current_fuel_mixture}\n"
    )

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
mqtt_client.subscribe("cockpit/input/master-alt")
mqtt_client.subscribe("cockpit/input/alt")
mqtt_client.subscribe("cockpit/input/carb-heat")
for primer_topic in PRIMER_TOPICS:
    mqtt_client.subscribe(primer_topic)
mqtt_client.subscribe(MAGNETOS_ENABLE_TOPIC)
for magnetos_switch_topic in MAGNETOS_SWITCH_TOPICS:
    mqtt_client.subscribe(magnetos_switch_topic)
mqtt_client.subscribe("cockpit/input/fuelmixer")
mqtt_client.loop_start()
print("[MQTT] Verbonden met broker")

# =========================
# UDP LISTENER (OUTPUT)
# =========================
def udp_listener():
    global current_attitude_pitch, current_attitude_roll
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
        attitude_changed = False
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
                mqtt_client.publish("cockpit/airspeed", value, qos=0)
                # print(f"[MQTT] AIRSPEED = {value}")
            elif key == "HEADING":
                mqtt_client.publish("cockpit/heading", value, qos=0)
                # print(f"[MQTT] HEADING = {value0.8}")
            elif key == "ATTITUDE_PITCH":
                current_attitude_pitch = value
                attitude_changed = True
            elif key == "ATTITUDE_ROLL":
                current_attitude_roll = value
                attitude_changed = True

        if attitude_changed:
            payload = f"{current_attitude_pitch:.3f},{current_attitude_roll:.3f}"
            mqtt_client.publish("cockpit/attitude", payload, qos=0)

# Start UDP listener in aparte thread
udp_thread = threading.Thread(target=udp_listener, daemon=True)
udp_thread.start()

# Houd script draaiende
try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    print("Stopping bridge")
