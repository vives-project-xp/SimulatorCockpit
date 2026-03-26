import lgpio
import paho.mqtt.client as mqtt
import time

# ========================
# CONFIG
# ========================
BROKER = "localhost"

TOPIC_BATTERY = "cockpit/input/battery"
TOPIC_TOGGLE = "cockpit/input/jouw_toggle_knop"      # <-- aanpassen
TOPIC_EXTRA = "cockpit/input/alt"       # <-- aanpassen

BUTTON_PIN = 17
TOGGLE_BUTTON_PIN = 27
EXTRA_BUTTON_PIN = 22

# ========================
# GPIO SETUP (lgpio)
# ========================
chip = lgpio.gpiochip_open(0)  # open gpiochip0

# Batterij knop
lgpio.gpio_claim_input(chip, BUTTON_PIN, lgpio.SET_PULL_UP)

# Toggle knop
lgpio.gpio_claim_input(chip, TOGGLE_BUTTON_PIN, lgpio.SET_PULL_UP)

# Extra gewone knop
lgpio.gpio_claim_input(chip, EXTRA_BUTTON_PIN, lgpio.SET_PULL_UP)

# ========================
# MQTT SETUP
# ========================
client = mqtt.Client()
client.connect(BROKER, 1883, 60)
client.loop_start()

print("Battery + toggle + extra input started (lgpio)...")

# ========================
# STATES
# ========================
last_battery_state = None
last_extra_state = None

toggle_state = 0
last_toggle_gpio = 1

try:
    while True:
        # ========================
        # 1) BATTERY BUTTON
        # ========================
        current_battery_gpio = lgpio.gpio_read(chip, BUTTON_PIN)
        battery_state = 1 if current_battery_gpio == 1 else 0

        if battery_state != last_battery_state:
            client.publish(TOPIC_BATTERY, str(battery_state))
            print("Battery:", battery_state)
            last_battery_state = battery_state

        # ========================
        # 2) TOGGLE BUTTON
        # ========================
        current_toggle_gpio = lgpio.gpio_read(chip, TOGGLE_BUTTON_PIN)

        if current_toggle_gpio == 0 and last_toggle_gpio == 1:
            toggle_state = 0 if toggle_state == 1 else 1
            client.publish(TOPIC_TOGGLE, str(toggle_state))
            print("Toggle knop:", toggle_state)

            time.sleep(0.2)  # debounce

        last_toggle_gpio = current_toggle_gpio

        # ========================
        # 3) EXTRA BUTTON (zoals batterij)
        # ========================
        current_extra_gpio = lgpio.gpio_read(chip, EXTRA_BUTTON_PIN)
        extra_state = 1 if current_extra_gpio == 1 else 0

        if extra_state != last_extra_state:
            client.publish(TOPIC_EXTRA, str(extra_state))
            print("Alt:", extra_state)
            last_extra_state = extra_state

        time.sleep(0.05)

except KeyboardInterrupt:
    print("Stopping...")
    lgpio.gpiochip_close(chip)