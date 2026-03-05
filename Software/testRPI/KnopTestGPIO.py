import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
import time

# ========================
# CONFIG
# ========================
BROKER = "10.10.232.162"   # of IP van je broker
TOPIC_BATTERY = "cockpit/input/battery"

BUTTON_PIN = 17

battery_state = 0

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

# ========================
# BUTTON LOOP
# ========================
try:
    while True:
        if GPIO.input(BUTTON_PIN) == GPIO.LOW:  # knop ingedrukt
            battery_state = 1 - battery_state
            client.publish(TOPIC_BATTERY, str(battery_state))
            print("Battery:", battery_state)
            time.sleep(0.3)  # debounce delay

        time.sleep(0.05)

except KeyboardInterrupt:
    print("Stopping...")
    GPIO.cleanup()