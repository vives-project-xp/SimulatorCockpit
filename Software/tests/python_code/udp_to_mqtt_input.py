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

UDP_INPUT_PORT = 5600
udp_input_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


# =========================
# MQTT SETUP
# =========================
mqtt_client = mqtt.Client(client_id=MQTT_CLIENT_ID, protocol=mqtt.MQTTv311)
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
mqtt_client.loop_start()

print(f"[MQTT] Verbonden met {MQTT_BROKER}")

# TEST INPUT

current_throttle = 0.0
current_heading_bug = 0.0


test = """
<?xml version="1.0"?>
<PropertyList>
  <generic>
    <input>
      <line_separator></line_separator>
      <var_separator></var_separator>

      <chunk>
        <node>/controls/engines/current-engine/throttle</node>
        <type>float</type>
        <format>THROTTLE=0.8</format>
      </chunk>

    </input>
  </generic>
</PropertyList>
"""


def on_message(client, userdata, msg):
    global current_throttle, current_heading_bug

    try:
        value = float(msg.payload.decode())
    except:
        return

    if msg.topic == "cockpit/input/throttle":
        current_throttle = value

    elif msg.topic == "cockpit/input/heading_bug":
        current_heading_bug = value

    # stuur ALTIJD beide waarden samen
    command = f"THROTTLE=0.8\n"
    udp_input_sock.sendto(command.encode(), ("127.0.0.1", UDP_INPUT_PORT))
    print(repr(command))
    print(f"[INPUT] {command.strip()}")

mqtt_client.on_message = on_message

mqtt_client.subscribe("cockpit/input/throttle")
mqtt_client.subscribe("cockpit/input/heading_bug")

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
            # print(f"[DATA] AIRSPEED = {value}")

        elif key == "HEADING":
            mqtt_client.publish("cockpit/heading", value)
            # print(f"[DATA] HEADING = {value}")
