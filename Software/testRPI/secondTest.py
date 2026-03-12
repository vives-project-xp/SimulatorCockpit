import tkinter as tk
import paho.mqtt.client as mqtt
import math

# ---------------- MQTT instellingen ----------------
BROKER = "localhost"

TOPIC_THROTTLE = "cockpit/input/throttle"
TOPIC_BATTERY = "cockpit/input/battery"
TOPIC_AIRSPEED = "cockpit/airspeed"
TOPIC_MONITOR = "#"

# ---------------- globale variabelen ----------------
battery_state = 0
airspeed_value = 0.0  # knots
throttle_value = 0.0  # motorvermogen 0-1

# ---------------- GUI ----------------
root = tk.Tk()
root.title("COCKPIT CONTROL PANEL")
root.attributes("-fullscreen", True)

frame = tk.Frame(root)
frame.pack(expand=True)

title = tk.Label(frame, text="COCKPIT CONTROL", font=("Arial", 40))
title.pack(pady=20)

# ---------------- Battery toggle ----------------
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

# ---------------- Throttle slider ----------------
def send_throttle(value):
    global throttle_value
    throttle_value = round(float(value), 2)
    client.publish(TOPIC_THROTTLE, str(throttle_value))
    throttle_label.config(text=f"THROTTLE: {throttle_value}")

throttle_label = tk.Label(frame, text="THROTTLE: 0.0", font=("Arial", 30))
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

# ---------------- AIRSPEED GAUGE ----------------
GAUGE_SIZE = 500
CENTER = GAUGE_SIZE // 2
RADIUS = 200

gauge_canvas = tk.Canvas(frame, width=GAUGE_SIZE, height=GAUGE_SIZE, bg="black")
gauge_canvas.pack(pady=30)

def speed_to_angle(speed):
    # 0 - 180 knots mapped to -210° → 30°
    return -210 + (speed / 180) * 240

def draw_gauge():
    gauge_canvas.delete("all")

    # Outer circle
    gauge_canvas.create_oval(
        CENTER-RADIUS-20, CENTER-RADIUS-20,
        CENTER+RADIUS+20, CENTER+RADIUS+20,
        outline="white", width=4
    )

    # Green arc: 0-120
    gauge_canvas.create_arc(
        CENTER-RADIUS, CENTER-RADIUS,
        CENTER+RADIUS, CENTER+RADIUS,
        start=-210, extent=160,
        style="arc", outline="lime", width=18
    )

    # Yellow arc: 120-160
    gauge_canvas.create_arc(
        CENTER-RADIUS, CENTER-RADIUS,
        CENTER+RADIUS, CENTER+RADIUS,
        start=-50, extent=80,
        style="arc", outline="yellow", width=18
    )

    # Red arc: 160-180
    gauge_canvas.create_arc(
        CENTER-RADIUS, CENTER-RADIUS,
        CENTER+RADIUS, CENTER+RADIUS,
        start=30, extent=30,
        style="arc", outline="red", width=18
    )

    # Tick marks + numbers (0-180 elke 20 knots)
    for speed in range(0, 181, 20):
        angle = math.radians(speed_to_angle(speed))
        outer = RADIUS
        inner = RADIUS - 20
        x1 = CENTER + inner * math.cos(angle)
        y1 = CENTER + inner * math.sin(angle)
        x2 = CENTER + outer * math.cos(angle)
        y2 = CENTER + outer * math.sin(angle)
        gauge_canvas.create_line(x1, y1, x2, y2, fill="white", width=2)

        tx = CENTER + (RADIUS-50) * math.cos(angle)
        ty = CENTER + (RADIUS-50) * math.sin(angle)
        gauge_canvas.create_text(
            tx, ty,
            text=str(speed),
            fill="white",
            font=("Arial", 14, "bold")
        )

def draw_needle(speed):
    gauge_canvas.delete("needle")
    angle = math.radians(speed_to_angle(speed))
    x = CENTER + (RADIUS-50) * math.cos(angle)
    y = CENTER + (RADIUS-50) * math.sin(angle)
    gauge_canvas.create_line(
        CENTER, CENTER,
        x, y,
        fill="red",
        width=4,
        tags="needle"
    )
    gauge_canvas.create_oval(
        CENTER-8, CENTER-8,
        CENTER+8, CENTER+8,
        fill="white",
        tags="needle"
    )

draw_gauge()

# ---------------- GUI update loop ----------------
def update_gauge():
    draw_needle(airspeed_value)
    root.after(50, update_gauge)

update_gauge()

# ---------------- Log window ----------------
log = tk.Text(frame, height=10, width=80, font=("Arial", 12))
log.pack(pady=20)

# ---------------- MQTT ----------------
client = mqtt.Client()

def on_message(client, userdata, msg):
    global airspeed_value
    message = msg.payload.decode()

    if msg.topic == TOPIC_AIRSPEED:
        try:
            # max 180 knots voor gauge
            airspeed_value = min(max(float(message), 0), 180)
        except:
            pass

    log.insert(tk.END, f"{msg.topic}: {message}\n")
    log.see(tk.END)

client.on_message = on_message
client.connect(BROKER, 1883, 60)
client.subscribe(TOPIC_MONITOR)
client.loop_start()

# ---------------- Start GUI ----------------
root.mainloop()