import lgpio
import paho.mqtt.client as mqtt
import time

# ========================
# CONFIG
# ========================
BROKER = "localhost"
TOPIC_BATTERY = "cockpit/input/battery"

BUTTON_PIN = 17

# ========================
# GPIO SETUP (lgpio)
# ========================
chip = lgpio.gpiochip_open(0)  # open gpiochip0

# Zet pin als input met pull-up
lgpio.gpio_claim_input(chip, BUTTON_PIN)
lgpio.gpio_set_pull(chip, BUTTON_PIN, lgpio.SET_PULL_UP)

# ========================
# MQTT SETUP
# ========================
client = mqtt.Client()
client.connect(BROKER, 1883, 60)
client.loop_start()

print("Battery hardware control started (lgpio)...")

last_state = None

try:
    while True:
        current_gpio = lgpio.gpio_read(chip, BUTTON_PIN)

        # zelfde logica als je vorige code
        battery_state = 1 if current_gpio == 1 else 0

        if battery_state != last_state:
            client.publish(TOPIC_BATTERY, str(battery_state))
            print("Battery:", battery_state)
            last_state = battery_state

        time.sleep(0.05)

except KeyboardInterrupt:
    print("Stopping...")
    lgpio.gpiochip_close(chip)