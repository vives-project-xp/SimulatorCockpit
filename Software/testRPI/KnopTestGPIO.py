import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
import time

# ========================
# CONFIG
# ========================
BROKER = "localhost"
TOPIC_BATTERY = "cockpit/input/battery"

BUTTON_PIN = 17

# ========================
# GPIO SETUP
# ========================
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# ========================
# MQTT SETUP
# ========================
client = mqtt.Client()
client.connect(BROKER, 1883, 60)
client.loop_start()

print("Battery hardware control started...")

last_state = None  # onthoud vorige stand

try:
    while True:
        current_gpio = GPIO.input(BUTTON_PIN)

        # Omdat we PULL_UP gebruiken:
        # LOW = 0 (schakelaar naar GND)
        # HIGH = 1
        battery_state = 1 if current_gpio == GPIO.HIGH else 0

        if battery_state != last_state:
            client.publish(TOPIC_BATTERY, str(battery_state))
            print("Battery:", battery_state)
            last_state = battery_state

        time.sleep(0.05)

except KeyboardInterrupt:
    print("Stopping...")
    GPIO.cleanup()