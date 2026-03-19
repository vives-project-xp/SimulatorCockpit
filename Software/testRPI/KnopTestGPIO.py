from gpiozero import Button
from signal import pause
import paho.mqtt.client as mqtt

BROKER = "localhost"
TOPIC_BATTERY = "cockpit/input/battery"

button = Button(17, pull_up=True)

client = mqtt.Client()
client.connect(BROKER, 1883, 60)
client.loop_start()

def pressed():
    client.publish(TOPIC_BATTERY, "1")
    print("Battery: 1")

def released():
    client.publish(TOPIC_BATTERY, "0")
    print("Battery: 0")

button.when_pressed = pressed
button.when_released = released

pause()