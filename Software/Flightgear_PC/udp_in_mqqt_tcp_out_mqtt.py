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
TCP_CONNECT_TIMEOUT = float(os.getenv("TCP_CONNECT_TIMEOUT", "2.0"))
TCP_RECONNECT_INTERVAL = float(os.getenv("TCP_RECONNECT_INTERVAL", "1.0"))
STATE_RESEND_INTERVAL = float(os.getenv("STATE_RESEND_INTERVAL", "1.0"))

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
INPUT_TOPICS = (
    "cockpit/input/battery",
    "cockpit/input/master-alt",
    "cockpit/input/alt",
    "cockpit/input/carb-heat",
    *PRIMER_TOPICS,
    MAGNETOS_ENABLE_TOPIC,
    *MAGNETOS_SWITCH_TOPICS.keys(),
    "cockpit/input/fuelmixer",
)

# =========================
# TCP CONNECTIE (INPUT)
# =========================
tcp_sock = None
tcp_next_retry = 0.0
tcp_last_error = ""
tcp_lock = threading.Lock()
state_lock = threading.Lock()

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


def close_tcp_socket():
    global tcp_sock

    if tcp_sock is None:
        return

    try:
        tcp_sock.close()
    except OSError:
        pass

    tcp_sock = None


def ensure_tcp_connection():
    global tcp_sock, tcp_next_retry, tcp_last_error

    if tcp_sock is not None:
        return True

    now = time.monotonic()
    if now < tcp_next_retry:
        return False

    sock = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(TCP_CONNECT_TIMEOUT)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        sock.connect((FG_TCP_IP, FG_TCP_PORT))
        tcp_sock = sock
        tcp_last_error = ""
        tcp_next_retry = 0.0
        print("[TCP] Verbonden met FlightGear")
        return True
    except OSError as exc:
        if sock is not None:
            try:
                sock.close()
            except OSError:
                pass
        close_tcp_socket()
        tcp_next_retry = now + TCP_RECONNECT_INTERVAL
        error_text = str(exc)
        if error_text != tcp_last_error:
            print(f"[TCP] Wachten op FlightGear ({FG_TCP_IP}:{FG_TCP_PORT}) - {error_text}")
            tcp_last_error = error_text
        return False


def send_to_flightgear(datastr, log_send=True):
    global tcp_next_retry

    with tcp_lock:
        if not ensure_tcp_connection():
            return False

        try:
            tcp_sock.sendall(datastr.encode("utf-8"))
        except (OSError, socket.timeout) as exc:
            print(f"[TCP] Verbinding verloren, reconnect volgt - {exc}")
            close_tcp_socket()
            tcp_next_retry = 0.0
            return False

    if log_send:
        print("[TCP SEND]", datastr.strip())

    return True


def build_datastr_unlocked():
    starter_value = "1" if current_starter else "0"
    return (
        f"{current_battery}:{current_master_alt}:{current_carb_heat}:"
        f"{current_primer_lever}:{current_primer}:{current_magnetos}:{starter_value}:{current_fuel_mixture}\n"
    )


def send_current_state(force=False, log_send=True):
    global old_hash

    with state_lock:
        datastr = build_datastr_unlocked()
        new_hash = hashlib.md5(datastr.encode()).digest()
        if not force and new_hash == old_hash:
            return

    if send_to_flightgear(datastr, log_send=log_send):
        with state_lock:
            old_hash = new_hash


def state_resend_loop():
    while True:
        send_current_state(force=True, log_send=False)
        time.sleep(STATE_RESEND_INTERVAL)

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

    with state_lock:
        current_primer = 0
        primer_reset_timer = None

    send_current_state(force=True, log_send=True)


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
        with state_lock:
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

            current_magnetos = calculate_magnetos()
            previous_starter = current_starter
            current_starter = calculate_starter()
            sync_primer_reset_timer(previous_starter, current_starter)

    except ValueError:
        return

    send_current_state(log_send=True)


def on_connect(client, userdata, flags, reason_code, properties=None):
    if reason_code != 0:
        print(f"[MQTT] Verbinden mislukt: {reason_code}")
        return

    for topic in INPUT_TOPICS:
        client.subscribe(topic)

    print("[MQTT] Verbonden met broker")


def on_disconnect(client, userdata, reason_code, properties=None):
    print(f"[MQTT] Verbinding verbroken: {reason_code}")

# =========================
# MQTT SETUP
# =========================
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_disconnect = on_disconnect
mqtt_client.on_message = on_message
mqtt_client.reconnect_delay_set(min_delay=1, max_delay=10)

while True:
    try:
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        break
    except OSError as exc:
        print(f"[MQTT] Wachten op broker ({MQTT_BROKER}:{MQTT_PORT}) - {exc}")
        time.sleep(2)

mqtt_client.loop_start()

resend_thread = threading.Thread(target=state_resend_loop, daemon=True)
resend_thread.start()

# =========================
# UDP LISTENER (OUTPUT)
# =========================
def udp_listener():
    global current_attitude_pitch, current_attitude_roll
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        udp_sock.bind((UDP_IP, UDP_PORT))
    except OSError as exc:
        print(f"[UDP] Kan niet luisteren op {UDP_IP}:{UDP_PORT} - {exc}")
        return

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
