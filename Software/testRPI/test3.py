import tkinter as tk
import paho.mqtt.client as mqtt
import math
import time

BROKER = "localhost"

TOPIC_THROTTLE = "cockpit/input/throttle"
TOPIC_BATTERY = "cockpit/input/battery"
TOPIC_AIRSPEED = "cockpit/airspeed"
TOPIC_MONITOR = "#"

battery_state = 0
airspeed_value = 0.0
throttle_value = 0.0

last_sent_throttle = None
last_send_time = 0
pending_logs = []

# ---------------- WINDOW ----------------

root = tk.Tk()
root.title("COCKPIT CONTROL PANEL")
root.attributes("-fullscreen", True)

frame = tk.Frame(root)
frame.pack(expand=True)

title = tk.Label(frame, text="COCKPIT CONTROL", font=("Arial", 40))
title.pack(pady=20)

# ---------------- BATTERY ----------------

def toggle_battery():
    global battery_state
    battery_state = 1 - battery_state
    client.publish(TOPIC_BATTERY, str(battery_state), qos=1)
    update_battery_ui()

def update_battery_ui():
    if battery_state == 1:
        battery_btn.config(text="BATTERY: ON", bg="green")
    else:
        battery_btn.config(text="BATTERY: OFF", bg="red")

battery_btn = tk.Button(
    frame,
    text="BATTERY: OFF",
    command=toggle_battery,
    font=("Arial", 30),
    width=15,
    height=2,
    bg="red"
)
battery_btn.pack(pady=20)

# ---------------- THROTTLE ----------------

def send_throttle(value):
    global throttle_value, last_sent_throttle, last_send_time

    throttle_value = round(float(value), 2)
    now = time.time()

    if throttle_value != last_sent_throttle and (now - last_send_time) > 0.1:
        client.publish(TOPIC_THROTTLE, str(throttle_value), qos=0)
        throttle_label.config(text=f"THROTTLE: {throttle_value}")
        last_sent_throttle = throttle_value
        last_send_time = now

throttle_label = tk.Label(frame, text="THROTTLE: 0.0", font=("Arial", 30))
throttle_label.pack(pady=10)

throttle_slider = tk.Scale(
    frame,
    from_=0,
    to=1,
    resolution=0.01,
    orient=tk.HORIZONTAL,
    length=600,
    command=send_throttle,
    font=("Arial", 20)
)
throttle_slider.pack(pady=20)

# ---------------- AIRSPEED GAUGE ----------------

GAUGE_SIZE = 500
CENTER = GAUGE_SIZE // 2
RADIUS = 200
TOTAL_SPEED = 180

gauge_canvas = tk.Canvas(frame, width=GAUGE_SIZE, height=GAUGE_SIZE, bg="black")
gauge_canvas.pack(pady=30)

def speed_to_angle(speed):
    return -210 + (speed / TOTAL_SPEED) * 240

def arc_coords():
    return (CENTER - RADIUS, CENTER - RADIUS, CENTER + RADIUS, CENTER + RADIUS)

def draw_gauge():
    gauge_canvas.delete("all")

    gauge_canvas.create_oval(
        CENTER - RADIUS - 20,
        CENTER - RADIUS - 20,
        CENTER + RADIUS + 20,
        CENTER + RADIUS + 20,
        outline="white",
        width=4
    )

    def draw_zone(start_speed, end_speed, color):
        start_angle = speed_to_angle(start_speed) + 180
        end_angle = speed_to_angle(end_speed) + 180

        gauge_canvas.create_arc(
            *arc_coords(),
            start=start_angle,
            extent=end_angle - start_angle,
            style="arc",
            outline=color,
            width=18
        )

    draw_zone(0, 120, "lime")
    draw_zone(120, 160, "yellow")
    draw_zone(160, 180, "red")

    for speed in range(0, TOTAL_SPEED + 1, 20):
        angle = math.radians(speed_to_angle(speed))

        outer = RADIUS
        inner = RADIUS - 20

        x1 = CENTER + inner * math.cos(angle)
        y1 = CENTER + inner * math.sin(angle)
        x2 = CENTER + outer * math.cos(angle)
        y2 = CENTER + outer * math.sin(angle)

        gauge_canvas.create_line(x1, y1, x2, y2, fill="white", width=2)

        tx = CENTER + (RADIUS - 50) * math.cos(angle)
        ty = CENTER + (RADIUS - 50) * math.sin(angle)

        gauge_canvas.create_text(
            tx,
            ty,
            text=str(speed),
            fill="white",
            font=("Arial", 14, "bold")
        )

def draw_needle(speed):
    gauge_canvas.delete("needle")

    speed = max(0, min(TOTAL_SPEED, speed))
    angle = math.radians(speed_to_angle(speed))

    x = CENTER + (RADIUS - 50) * math.cos(angle)
    y = CENTER + (RADIUS - 50) * math.sin(angle)

    gauge_canvas.create_line(
        CENTER,
        CENTER,
        x,
        y,
        fill="red",
        width=4,
        tags="needle"
    )

    gauge_canvas.create_oval(
        CENTER - 8,
        CENTER - 8,
        CENTER + 8,
        CENTER + 8,
        fill="white",
        tags="needle"
    )

draw_gauge()

def update_gauge():
    draw_needle(airspeed_value)
    root.after(50, update_gauge)

update_gauge()

# ---------------- LOG WINDOW ----------------

log = tk.Text(frame, height=10, width=80, font=("Arial", 12))
log.pack(pady=20)

MAX_LOG_LINES = 200

def flush_logs():
    while pending_logs:
        line = pending_logs.pop(0)
        log.insert(tk.END, line + "\n")
        log.see(tk.END)

    current_lines = int(log.index("end-1c").split(".")[0])
    if current_lines > MAX_LOG_LINES:
        log.delete("1.0", f"{current_lines - MAX_LOG_LINES}.0")

    root.after(100, flush_logs)

flush_logs()

# ---------------- MQTT ----------------

client = mqtt.Client()

def on_message(client, userdata, msg):
    global airspeed_value

    try:
        message = msg.payload.decode()
    except Exception:
        message = str(msg.payload)

    if msg.topic == TOPIC_AIRSPEED:
        try:
            airspeed_value = min(max(float(message), 0), 180)
        except ValueError:
            pass

    pending_logs.append(f"{msg.topic}: {message}")

client.on_message = on_message

client.connect(BROKER, 1883, 60)
client.subscribe(TOPIC_MONITOR)
client.loop_start()

# ---------------- CLOSE CLEANLY ----------------

def on_close():
    try:
        client.loop_stop()
        client.disconnect()
    except Exception:
        pass
    root.destroy()

root.bind("<Escape>", lambda event: on_close())
root.protocol("WM_DELETE_WINDOW", on_close)

root.mainloop()