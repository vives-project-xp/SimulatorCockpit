import tkinter as tk
import paho.mqtt.client as mqtt
import math

BROKER = "localhost"

TOPIC_THROTTLE = "cockpit/input/throttle"
TOPIC_BATTERY = "cockpit/input/battery"
TOPIC_AIRSPEED = "cockpit/airspeed"
TOPIC_HEADING = "cockpit/heading"
TOPIC_ATTITUDE = "cockpit/attitude"
TOPIC_MONITOR = "#"

battery_state = 0
airspeed_value = 0.0
heading_value = 0.0
display_heading = 0.0
pitch = 0.0
roll = 0.0

# ---------------- WINDOW ----------------

root = tk.Tk()
root.title("COCKPIT CONTROL PANEL")
root.attributes("-fullscreen", True)
root.configure(bg="black")

# dynamic sizing
screen_w = root.winfo_screenwidth()
screen_h = root.winfo_screenheight()

GAUGE_SIZE = min(screen_w // 3, screen_h)
CENTER = GAUGE_SIZE // 2
RADIUS = int(GAUGE_SIZE * 0.4)
TOTAL_SPEED = 180

# ---------------- MAIN FRAME ----------------

main_frame = tk.Frame(root, bg="black")
main_frame.pack(fill="both", expand=True)

main_frame.columnconfigure(0, weight=1)
main_frame.columnconfigure(1, weight=1)
main_frame.columnconfigure(2, weight=1)

# ================= AIRSPEED =================

airspeed_canvas = tk.Canvas(main_frame, width=GAUGE_SIZE, height=GAUGE_SIZE, bg="black", highlightthickness=0)
airspeed_canvas.grid(row=0, column=0, sticky="nsew")

def speed_to_angle(speed):
    return -210 + (speed / TOTAL_SPEED) * 240

def draw_airspeed():
    airspeed_canvas.delete("all")

    airspeed_canvas.create_oval(
        CENTER-RADIUS-20, CENTER-RADIUS-20,
        CENTER+RADIUS+20, CENTER+RADIUS+20,
        outline="white", width=4
    )

    def draw_zone(start, end, color):
        airspeed_canvas.create_arc(
            CENTER-RADIUS, CENTER-RADIUS,
            CENTER+RADIUS, CENTER+RADIUS,
            start=speed_to_angle(start)+180,
            extent=speed_to_angle(end)-speed_to_angle(start),
            style="arc",
            outline=color,
            width=15
        )

    draw_zone(0, 120, "lime")
    draw_zone(120, 160, "yellow")
    draw_zone(160, 180, "red")

    for speed in range(0, TOTAL_SPEED+1, 20):
        angle = math.radians(speed_to_angle(speed))

        x1 = CENTER + (RADIUS-15) * math.cos(angle)
        y1 = CENTER + (RADIUS-15) * math.sin(angle)
        x2 = CENTER + RADIUS * math.cos(angle)
        y2 = CENTER + RADIUS * math.sin(angle)

        airspeed_canvas.create_line(x1, y1, x2, y2, fill="white", width=2)

        tx = CENTER + (RADIUS-40) * math.cos(angle)
        ty = CENTER + (RADIUS-40) * math.sin(angle)

        airspeed_canvas.create_text(tx, ty, text=str(speed), fill="white")

def draw_airspeed_needle(speed):
    airspeed_canvas.delete("needle")

    angle = math.radians(speed_to_angle(speed))

    x = CENTER + (RADIUS-50) * math.cos(angle)
    y = CENTER + (RADIUS-50) * math.sin(angle)

    airspeed_canvas.create_line(CENTER, CENTER, x, y, fill="red", width=3, tags="needle")
    airspeed_canvas.create_oval(CENTER-5, CENTER-5, CENTER+5, CENTER+5, fill="white", tags="needle")

draw_airspeed()

# ================= ATTITUDE =================

att_canvas = tk.Canvas(main_frame, width=GAUGE_SIZE, height=GAUGE_SIZE, bg="black", highlightthickness=0)
att_canvas.grid(row=0, column=1, sticky="nsew")

def draw_attitude(pitch, roll):
    att_canvas.delete("all")

    for y in range(GAUGE_SIZE):
        color = "#4da6ff" if y < CENTER + pitch*3 else "#8B4513"
        att_canvas.create_line(0, y, GAUGE_SIZE, y, fill=color)

    rad = math.radians(roll)

    def rot(x, y):
        dx = x - CENTER
        dy = y - CENTER
        rx = dx * math.cos(rad) - dy * math.sin(rad)
        ry = dx * math.sin(rad) + dy * math.cos(rad)
        return CENTER + rx, CENTER + ry

    x1, y1 = rot(0, CENTER + pitch*3)
    x2, y2 = rot(GAUGE_SIZE, CENTER + pitch*3)

    att_canvas.create_line(x1, y1, x2, y2, fill="white", width=6)

    # vliegtuig referentie (wit pijltje)
    att_canvas.create_line(CENTER-20, CENTER, CENTER+20, CENTER, fill="white", width=4)
    att_canvas.create_line(CENTER, CENTER-10, CENTER, CENTER+10, fill="white", width=4)

    att_canvas.create_oval(10,10,GAUGE_SIZE-10,GAUGE_SIZE-10,outline="white",width=3)

# ================= COMPASS =================

compass_canvas = tk.Canvas(main_frame, width=GAUGE_SIZE, height=GAUGE_SIZE, bg="black", highlightthickness=0)
compass_canvas.grid(row=0, column=2, sticky="nsew")

def draw_compass(heading):
    compass_canvas.delete("all")

    compass_canvas.create_oval(
        CENTER-RADIUS, CENTER-RADIUS,
        CENTER+RADIUS, CENTER+RADIUS,
        outline="white", width=3
    )

    for deg in range(0, 360, 5):
        angle = math.radians(deg - heading - 90)

        if deg % 30 == 0:
            inner = RADIUS - 25; width = 3
        elif deg % 10 == 0:
            inner = RADIUS - 18; width = 2
        else:
            inner = RADIUS - 12; width = 1

        x1 = CENTER + inner * math.cos(angle)
        y1 = CENTER + inner * math.sin(angle)
        x2 = CENTER + RADIUS * math.cos(angle)
        y2 = CENTER + RADIUS * math.sin(angle)

        compass_canvas.create_line(x1, y1, x2, y2, fill="white", width=width)

        if deg % 30 == 0:
            tx = CENTER + (RADIUS-45) * math.cos(angle)
            ty = CENTER + (RADIUS-45) * math.sin(angle)

            text = {0:"N",90:"O",180:"Z",270:"W"}.get(deg,str(deg))
            color = "yellow" if deg in [0,90,180,270] else "white"

            compass_canvas.create_text(tx, ty, text=text, fill=color, font=("Arial",14,"bold"))

    compass_canvas.create_polygon(CENTER, CENTER - 90, CENTER-10, CENTER-60, CENTER+10, CENTER-60, fill="red")
    compass_canvas.create_line(CENTER, CENTER-60, CENTER, CENTER+60, fill="red", width=3)

# ================= UPDATE =================

def update_ui():
    global display_heading

    diff = (heading_value - display_heading)
    if diff > 180: diff -= 360
    elif diff < -180: diff += 360

    display_heading += diff * 0.15

    draw_airspeed_needle(airspeed_value)
    draw_compass(display_heading)
    draw_attitude(pitch, roll)

    root.after(50, update_ui)

update_ui()

# ================= MQTT =================

client = mqtt.Client()

def on_message(client, userdata, msg):
    global airspeed_value, heading_value, pitch, roll

    message = msg.payload.decode()

    if msg.topic == TOPIC_AIRSPEED:
        airspeed_value = float(message)

    elif msg.topic == TOPIC_HEADING:
        heading_value = float(message)

    elif msg.topic == TOPIC_ATTITUDE:
        try:
            p, r = message.split(",")
            pitch = float(p)
            roll = float(r)
        except:
            pass

client.on_message = on_message
client.connect(BROKER, 1883, 60)
client.subscribe(TOPIC_MONITOR)
client.loop_start()

root.mainloop()