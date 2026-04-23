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

# Haal de schermgrootte op
root.update_idletasks()
SCREEN_W = root.winfo_screenwidth()
SCREEN_H = root.winfo_screenheight()

# Het scherm is fysiek liggend maar wordt getoond als staand (of omgekeerd).
# We tekenen alles alsof het scherm 90° gedraaid is:
# - Beschikbare breedte (voor ons: SCREEN_H) wordt verdeeld in 3 gauges
# - Beschikbare hoogte (voor ons: SCREEN_W) is de hoogte van elke gauge

# Gauge grootte berekening: 3 gauges naast elkaar op het geroteerde scherm
GAUGE_SIZE = SCREEN_H // 3
CENTER = GAUGE_SIZE // 2
RADIUS = int(CENTER * 0.72)
TOTAL_SPEED = 180

# Hoofdframe op volledig scherm, zwart
main_frame = tk.Frame(root, bg="black")
main_frame.pack(fill="both", expand=True)

# Canvas dat het volledige scherm beslaat, waarop alles geroteerd wordt getekend
CANVAS_W = SCREEN_W
CANVAS_H = SCREEN_H

master_canvas = tk.Canvas(main_frame, width=CANVAS_W, height=CANVAS_H, bg="black", highlightthickness=0)
master_canvas.pack(fill="both", expand=True)

# De drie sub-canvassen worden als "windows" in de master canvas geplaatst.
# We plaatsen ze GEROTEERD: ze komen horizontaal naast elkaar,
# maar omdat het scherm 90° gedraaid is, lijken ze verticaal gestapeld.

# Positie van de 3 gauge-vensters op het geroteerde scherm:
# Elk gauge neemt 1/3 van de hoogte in beslag (SCREEN_H // 3)
# De breedte is het volledige scherm (SCREEN_W)
GAUGE_W = SCREEN_W
GAUGE_H = SCREEN_H // 3

# ================= AIRSPEED =================

airspeed_canvas = tk.Canvas(master_canvas, width=GAUGE_W, height=GAUGE_H, bg="black", highlightthickness=0)
master_canvas.create_window(0, 0, anchor="nw", window=airspeed_canvas)

AS_CX = GAUGE_W // 2
AS_CY = GAUGE_H // 2
AS_R = min(AS_CX, AS_CY) - 20

def speed_to_angle(speed):
    return -210 + (speed / TOTAL_SPEED) * 240

def draw_airspeed():
    airspeed_canvas.delete("all")
    airspeed_canvas.create_oval(
        AS_CX - AS_R - 15, AS_CY - AS_R - 15,
        AS_CX + AS_R + 15, AS_CY + AS_R + 15,
        outline="white", width=4
    )

    def draw_zone(start, end, color):
        start_angle = speed_to_angle(start) + 180
        end_angle = speed_to_angle(end) + 180
        airspeed_canvas.create_arc(
            AS_CX - AS_R, AS_CY - AS_R,
            AS_CX + AS_R, AS_CY + AS_R,
            start=start_angle,
            extent=end_angle - start_angle,
            style="arc",
            outline=color,
            width=12
        )

    draw_zone(0, 120, "lime")
    draw_zone(120, 160, "yellow")
    draw_zone(160, 180, "red")

    for speed in range(0, TOTAL_SPEED + 1, 20):
        angle = math.radians(speed_to_angle(speed))
        x1 = AS_CX + (AS_R - 12) * math.cos(angle)
        y1 = AS_CY + (AS_R - 12) * math.sin(angle)
        x2 = AS_CX + AS_R * math.cos(angle)
        y2 = AS_CY + AS_R * math.sin(angle)
        airspeed_canvas.create_line(x1, y1, x2, y2, fill="white", width=2)
        tx = AS_CX + (AS_R - 32) * math.cos(angle)
        ty = AS_CY + (AS_R - 32) * math.sin(angle)
        airspeed_canvas.create_text(tx, ty, text=str(speed), fill="white", font=("Arial", max(10, AS_R // 14)))

    airspeed_canvas.create_text(AS_CX, AS_CY + AS_R // 2, text="AIRSPEED", fill="white", font=("Arial", max(10, AS_R // 10), "bold"))

def draw_airspeed_needle(speed):
    airspeed_canvas.delete("needle")
    angle = math.radians(speed_to_angle(speed))
    x = AS_CX + (AS_R - 30) * math.cos(angle)
    y = AS_CY + (AS_R - 30) * math.sin(angle)
    airspeed_canvas.create_line(AS_CX, AS_CY, x, y, fill="red", width=3, tags="needle")
    airspeed_canvas.create_oval(AS_CX - 5, AS_CY - 5, AS_CX + 5, AS_CY + 5, fill="white", tags="needle")

draw_airspeed()

# ================= ATTITUDE =================

att_canvas = tk.Canvas(master_canvas, width=GAUGE_W, height=GAUGE_H, bg="black", highlightthickness=0)
master_canvas.create_window(0, GAUGE_H, anchor="nw", window=att_canvas)

ATT_CX = GAUGE_W // 2
ATT_CY = GAUGE_H // 2
ATT_R = min(ATT_CX, ATT_CY) - 20

def draw_attitude(p, r):
    att_canvas.delete("all")

    # Clipping via ovaal simuleren met pixel-per-pixel invulling (originele aanpak)
    # Maar nu aangepast aan het nieuwe canvas formaat
    offset = p * 2
    for y in range(GAUGE_H):
        color = "#4da6ff" if y < ATT_CY + offset else "#8B4513"
        att_canvas.create_line(0, y, GAUGE_W, y, fill=color)

    rad = math.radians(r)

    def rot(x, y):
        dx = x - ATT_CX
        dy = y - ATT_CY
        rx = dx * math.cos(rad) - dy * math.sin(rad)
        ry = dx * math.sin(rad) + dy * math.cos(rad)
        return ATT_CX + rx, ATT_CY + ry + offset

    x1, y1 = rot(0, ATT_CY)
    x2, y2 = rot(GAUGE_W, ATT_CY)
    att_canvas.create_line(x1, y1, x2, y2, fill="white", width=6)
    att_canvas.create_line(ATT_CX - 30, ATT_CY, ATT_CX + 30, ATT_CY, fill="white", width=4)
    att_canvas.create_line(ATT_CX, ATT_CY - 15, ATT_CX, ATT_CY + 15, fill="white", width=4)
    att_canvas.create_oval(
        ATT_CX - ATT_R, ATT_CY - ATT_R,
        ATT_CX + ATT_R, ATT_CY + ATT_R,
        outline="white", width=3
    )
    att_canvas.create_text(ATT_CX, ATT_CY + ATT_R + 15, text="ATTITUDE", fill="white", font=("Arial", max(10, ATT_R // 10), "bold"))

# ================= COMPASS =================

compass_canvas = tk.Canvas(master_canvas, width=GAUGE_W, height=GAUGE_H, bg="black", highlightthickness=0)
master_canvas.create_window(0, GAUGE_H * 2, anchor="nw", window=compass_canvas)

COMP_CX = GAUGE_W // 2
COMP_CY = GAUGE_H // 2
COMP_R = min(COMP_CX, COMP_CY) - 20

def draw_compass(heading):
    compass_canvas.delete("all")
    compass_canvas.create_oval(
        COMP_CX - COMP_R, COMP_CY - COMP_R,
        COMP_CX + COMP_R, COMP_CY + COMP_R,
        outline="white", width=3
    )
    for deg in range(0, 360, 5):
        angle = math.radians(deg - heading - 90)
        if deg % 30 == 0:
            inner = COMP_R - 22; width = 3
        elif deg % 10 == 0:
            inner = COMP_R - 15; width = 2
        else:
            inner = COMP_R - 10; width = 1
        x1 = COMP_CX + inner * math.cos(angle)
        y1 = COMP_CY + inner * math.sin(angle)
        x2 = COMP_CX + COMP_R * math.cos(angle)
        y2 = COMP_CY + COMP_R * math.sin(angle)
        compass_canvas.create_line(x1, y1, x2, y2, fill="white", width=width)
        if deg % 30 == 0:
            tx = COMP_CX + (COMP_R - 40) * math.cos(angle)
            ty = COMP_CY + (COMP_R - 40) * math.sin(angle)
            text = {0: "N", 90: "O", 180: "Z", 270: "W"}.get(deg, str(deg))
            color = "yellow" if deg in [0, 90, 180, 270] else "white"
            compass_canvas.create_text(tx, ty, text=text, fill=color, font=("Arial", max(10, COMP_R // 10), "bold"))
    compass_canvas.create_polygon(
        COMP_CX, COMP_CY - int(COMP_R * 0.55),
        COMP_CX - 8, COMP_CY - int(COMP_R * 0.37),
        COMP_CX + 8, COMP_CY - int(COMP_R * 0.37),
        fill="red"
    )
    compass_canvas.create_line(COMP_CX, COMP_CY - int(COMP_R * 0.37), COMP_CX, COMP_CY + int(COMP_R * 0.37), fill="red", width=3)
    compass_canvas.create_text(COMP_CX, COMP_CY + COMP_R + 15, text="HEADING", fill="white", font=("Arial", max(10, COMP_R // 10), "bold"))

# ================= CONTROLS (verborgen overlay rechtsonder) =================

# Kleine log en controls in een klein frame rechtsonder (overlay op master canvas)
control_frame = tk.Frame(master_canvas, bg="black")
master_canvas.create_window(CANVAS_W, CANVAS_H, anchor="se", window=control_frame)

def toggle_battery():
    global battery_state
    battery_state = 1 - battery_state
    label = "ON" if battery_state else "OFF"
    battery_btn.config(text=f"BATTERY: {label}")
    client.publish(TOPIC_BATTERY, str(battery_state))

battery_btn = tk.Button(control_frame, text="BATTERY: OFF", command=toggle_battery,
                        font=("Arial", 12), bg="#222", fg="white")
battery_btn.pack(pady=4)

def send_throttle(value):
    val = round(float(value), 2)
    client.publish(TOPIC_THROTTLE, str(val))

tk.Scale(control_frame, from_=0, to=1, resolution=0.01,
         orient=tk.HORIZONTAL, length=200,
         command=send_throttle, bg="black", fg="white",
         troughcolor="#333", highlightthickness=0).pack(pady=4)

log = tk.Text(control_frame, height=5, width=35, bg="#111", fg="#0f0", font=("Courier", 9))
log.pack()

# ================= UPDATE =================

def update_ui():
    global display_heading
    diff = heading_value - display_heading
    if diff > 180:
        diff -= 360
    elif diff < -180:
        diff += 360
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
    log.insert(tk.END, f"{msg.topic}: {message}\n")
    log.see(tk.END)

client.on_message = on_message
client.connect(BROKER, 1883, 60)
client.subscribe(TOPIC_MONITOR)
client.loop_start()

root.mainloop()