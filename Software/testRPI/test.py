import tkinter as tk
import paho.mqtt.client as mqtt
import math

# =========================
# MQTT CONFIG
# =========================
BROKER = "localhost"

TOPIC_THROTTLE = "cockpit/input/throttle"
TOPIC_BATTERY = "cockpit/input/battery"
TOPIC_MONITOR = "#"

battery_state = 0

client = mqtt.Client()

# =========================
# GAUGE SETTINGS
# =========================
GAUGE_MIN = 0
GAUGE_MAX = 200
GAUGE_START_ANGLE = 210   # linker onderkant
GAUGE_END_ANGLE = -30     # rechter onderkant

def speed_to_angle(speed):
    ratio = (speed - GAUGE_MIN) / (GAUGE_MAX - GAUGE_MIN)
    return GAUGE_START_ANGLE + ratio * (GAUGE_END_ANGLE - GAUGE_START_ANGLE)

def draw_gauge(canvas):
    canvas.delete("all")
    w = 500
    h = 500
    cx = w // 2
    cy = h // 2
    radius = 200

    # Buitenste cirkel
    canvas.create_oval(cx-radius, cy-radius, cx+radius, cy+radius, width=4)

    # Schaalverdeling
    for speed in range(0, 201, 20):
        angle = speed_to_angle(speed)
        x1 = cx + (radius - 20) * math.cos(math.radians(angle))
        y1 = cy + (radius - 20) * math.sin(math.radians(angle))
        x2 = cx + radius * math.cos(math.radians(angle))
        y2 = cy + radius * math.sin(math.radians(angle))

        canvas.create_line(x1, y1, x2, y2, width=3)
        canvas.create_text(
            cx + (radius - 40) * math.cos(math.radians(angle)),
            cy + (radius - 40) * math.sin(math.radians(angle)),
            text=str(speed),
            font=("Arial", 12, "bold")
        )

def update_needle(canvas, speed):
    canvas.delete("needle")
    w = 500
    h = 500
    cx = w // 2
    cy = h // 2
    radius = 180

    angle = speed_to_angle(speed)
    x = cx + radius * math.cos(math.radians(angle))
    y = cy + radius * math.sin(math.radians(angle))

    canvas.create_line(cx, cy, x, y, width=5, fill="red", tags="needle")
    canvas.create_oval(cx-10, cy-10, cx+10, cy+10, fill="black", tags="needle")

# =========================
# MQTT CALLBACK
# =========================
log = tk.Text(frame, height=10, width=80, font=("Arial", 12))
def on_message(client, userdata, msg):
    message = msg.payload.decode()

    if msg.topic == "cockpit/airspeed":
        try:
            speed = float(message)
            update_needle(gauge_canvas, speed)
        except:
            pass

    log.insert(tk.END, f"{msg.topic}: {message}\n")
    log.see(tk.END)

client.on_message = on_message
client.connect(BROKER, 1883, 60)
client.subscribe(TOPIC_MONITOR)
client.loop_start()

# =========================
# TKINTER GUI
# =========================
root = tk.Tk()
root.title("COCKPIT CONTROL PANEL")
root.attributes("-fullscreen", True)

frame = tk.Frame(root)
frame.pack(expand=True)

title = tk.Label(frame, text="COCKPIT CONTROL", font=("Arial", 40))
title.pack(pady=20)

# -------------------------
# Battery toggle
# -------------------------
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

# -------------------------
# Throttle slider
# -------------------------
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

# -------------------------
# Airspeed Gauge
# -------------------------
gauge_canvas = tk.Canvas(frame, width=500, height=500, bg="white")
gauge_canvas.pack(pady=20)
draw_gauge(gauge_canvas)
update_needle(gauge_canvas, 0)

# -------------------------
# Log window
# -------------------------

log.pack(pady=20)

root.mainloop()