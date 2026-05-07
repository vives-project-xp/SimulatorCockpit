import os
import time

import lgpio
import paho.mqtt.client as mqtt

# ========================
# CONFIG
# ========================
BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))

TOPIC_BATTERY = "cockpit/input/battery"
TOPIC_TOGGLE = "cockpit/input/carb-heat"
TOPIC_EXTRA = "cockpit/input/alt"
TOPIC_PRIMER = "cockpit/input/primer"

# CORRECTE MAGNETOS STRUCTUUR
TOPIC_SWITCH_1 = "cockpit/input/magnetos/switch1"
TOPIC_SWITCH_2 = "cockpit/input/magnetos/switch2"
TOPIC_SWITCH_3 = "cockpit/input/magnetos/switch3"
TOPIC_SLEUTEL = "cockpit/input/magnetos/sleutel"  # aanpassen sleutel

BUTTON_PIN = 17
TOGGLE_BUTTON_PIN = 27
EXTRA_BUTTON_PIN = 22
SLEUTEL_PIN = 23
PRIMER_PIN = 18

SWITCH_1_PIN = 24
SWITCH_2_PIN = 25
SWITCH_3_PIN = 5

# ========================
# GPIO SETUP
# ========================
chip = lgpio.gpiochip_open(0)

lgpio.gpio_claim_input(chip, BUTTON_PIN, lgpio.SET_PULL_UP)
lgpio.gpio_claim_input(chip, TOGGLE_BUTTON_PIN, lgpio.SET_PULL_UP)
lgpio.gpio_claim_input(chip, EXTRA_BUTTON_PIN, lgpio.SET_PULL_UP)
lgpio.gpio_claim_input(chip, SLEUTEL_PIN, lgpio.SET_PULL_UP)
lgpio.gpio_claim_input(chip, PRIMER_PIN, lgpio.SET_PULL_UP)

lgpio.gpio_claim_input(chip, SWITCH_1_PIN, lgpio.SET_PULL_UP)
lgpio.gpio_claim_input(chip, SWITCH_2_PIN, lgpio.SET_PULL_UP)
lgpio.gpio_claim_input(chip, SWITCH_3_PIN, lgpio.SET_PULL_UP)

# ========================
# MQTT
# ========================
client = mqtt.Client()
client.connect(BROKER, MQTT_PORT, 60)
client.loop_start()

print("Cockpit input gestart (magnetos correct)...")

# ========================
# STATES
# ========================
last_battery_state = None
last_toggle_state = None
last_extra_state = None
last_sleutel_state = None

primer_state = 0
last_primer_gpio = 1

last_switch_1_state = None
last_switch_2_state = None
last_switch_3_state = None

try:
    while True:

        # ========================
        # BATTERY
        # ========================
        val = lgpio.gpio_read(chip, BUTTON_PIN)
        state = 1 if val == 1 else 0

        if state != last_battery_state:
            client.publish(TOPIC_BATTERY, str(state))
            print("Battery:", state)
            last_battery_state = state

        # ========================
        # TOGGLE
        # ========================
        val = lgpio.gpio_read(chip, TOGGLE_BUTTON_PIN)
        state = 1 if val == 1 else 0

        if state != last_toggle_state:
            client.publish(TOPIC_TOGGLE, str(state))
            print("Carb-heat:", state)
            last_toggle_state = state

        # ========================
        # EXTRA ALT
        # ========================
        val = lgpio.gpio_read(chip, EXTRA_BUTTON_PIN)
        state = 1 if val == 1 else 0

        if state != last_extra_state:
            client.publish(TOPIC_EXTRA, str(state))
            print("Alt:", state)
            last_extra_state = state

        # ========================
        # SLEUTEL
        # ========================
        val = lgpio.gpio_read(chip, SLEUTEL_PIN)
        state = 0 if val == 1 else 1

        if state != last_sleutel_state:
            client.publish(TOPIC_SLEUTEL, str(state))
            print("Sleutel:", state)
            last_sleutel_state = state

        # ========================
        # PRIMER
        # ========================
        val = lgpio.gpio_read(chip, PRIMER_PIN)

        if val == 0 and last_primer_gpio == 1:
            primer_state = 0 if primer_state == 1 else 1
            client.publish(TOPIC_PRIMER, str(primer_state))
            print("Primer:", primer_state)
            time.sleep(0.2)

        last_primer_gpio = val

        # ========================
        # SWITCH 1
        # ========================
        val = lgpio.gpio_read(chip, SWITCH_1_PIN)
        state = 1 if val == 1 else 0

        if state != last_switch_1_state:
            client.publish(TOPIC_SWITCH_1, str(state))
            print("Switch1:", state)
            last_switch_1_state = state

        # ========================
        # SWITCH 2
        # ========================
        val = lgpio.gpio_read(chip, SWITCH_2_PIN)
        state = 1 if val == 1 else 0

        if state != last_switch_2_state:
            client.publish(TOPIC_SWITCH_2, str(state))
            print("Switch2:", state)
            last_switch_2_state = state

        # ========================
        # SWITCH 3
        # ========================
        val = lgpio.gpio_read(chip, SWITCH_3_PIN)
        state = 1 if val == 1 else 0

        if state != last_switch_3_state:
            client.publish(TOPIC_SWITCH_3, str(state))
            print("Switch3:", state)
            last_switch_3_state = state

        time.sleep(0.05)

except KeyboardInterrupt:
    print("Stopping...")
    lgpio.gpiochip_close(chip)
