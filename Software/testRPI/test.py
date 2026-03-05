import tkinter as tk
import paho.mqtt.client as mqtt

BROKER = "localhost"

TOPIC_THROTTLE = "cockpit/input/throttle"
TOPIC_BATTERY = "cockpit/input/battery"
TOPIC_MONITOR = "#"

battery_state = 0

# MQTT setup
client = mqtt.Client()

def on_message(client, userdata, msg):
    message = msg.payload.decode()
    log.insert(tk.END, f"{msg.topic}: {message}\n")
    log.see(tk.END)

client.on_message = on_message
client.connect(BROKER, 1883, 60)
client.subscribe(TOPIC_MONITOR)
client.loop_start()

# GUI
root = tk.Tk()
root.title("COCKPIT CONTROL PANEL")
root.attributes("-fullscreen", True)

frame = tk.Frame(root)
frame.pack(expand=True)

title = tk.Label(frame, text="COCKPIT CONTROL", font=("Arial", 40))
title.pack(pady=20)

# 🔋 Battery toggle
def toggle_battery():
    global battery_state
    battery_state = 1 - battery_state
    client.publish(TOPIC_BATTERY, str(battery_state))
    update_battery_ui()

def update_battery_ui():
    if battery_state == 1:
        battery_btn.config(text="BATTERY: ON", bg="green")
    else:
        battery_btn.config(text="BATTERY: OFF", bg="red")

battery_btn = tk.Button(frame,
                        text="BATTERY: OFF",
                        command=toggle_battery,
                        font=("Arial", 30),
                        width=15,
                        height=2,
                        bg="red")
battery_btn.pack(pady=20)

# 🚀 Throttle slider
def send_throttle(value):
    throttle_value = round(float(value), 2)
    client.publish(TOPIC_THROTTLE, str(throttle_value))
    throttle_label.config(text=f"THROTTLE: {throttle_value}")

throttle_label = tk.Label(frame, text="THROTTLE: 0.0",
                          font=("Arial", 30))
throttle_label.pack(pady=10)

throttle_slider = tk.Scale(frame,
                           from_=0,
                           to=1,
                           resolution=0.01,
                           orient=tk.HORIZONTAL,
                           length=600,
                           command=send_throttle,
                           font=("Arial", 20))
throttle_slider.pack(pady=20)

# 📡 Log window
log = tk.Text(frame, height=10, width=80, font=("Arial", 12))
log.pack(pady=20)

root.mainloop()
