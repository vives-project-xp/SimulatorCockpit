import tkinter as tk
import paho.mqtt.client as mqtt
import math

BROKER = "10.10.229.190"

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

TOTAL_SPEED = 180

# ---------------- WINDOW ----------------

root = tk.Tk()
root.title("COCKPIT")
root.attributes("-fullscreen", True)
root.configure(bg="black")
root.update_idletasks()

SCREEN_W = root.winfo_screenwidth()
SCREEN_H = root.winfo_screenheight()

# 3 gauges naast elkaar op een geroteerd display (OS y-as = fysieke x-as)
GAUGE_W = SCREEN_W
GAUGE_H = SCREEN_H // 3

GCX = GAUGE_W // 2
GCY = GAUGE_H // 2
GR  = min(GCX, GCY) - 15

def rot90(gx, gy, cx, cy):
    """Draai punt (gx,gy) 90 graden met de klok mee rond (cx,cy)."""
    dx = gx - cx
    dy = gy - cy
    return cx + dy, cy - dx

# ================= AIRSPEED =================

as_canvas = tk.Canvas(root, width=GAUGE_W, height=GAUGE_H, bg="black", highlightthickness=0)
as_canvas.place(x=0, y=0)

def speed_to_angle_deg(speed):
    return -210 + (speed / TOTAL_SPEED) * 240

def draw_airspeed_static():
    as_canvas.delete("static")
    cx, cy, r = GCX, GCY, GR

    as_canvas.create_oval(cx-r-12, cy-r-12, cx+r+12, cy+r+12,
                          outline="white", width=3, tags="static")

    def draw_zone(start, end, color):
        sa = 90 - speed_to_angle_deg(start)
        ea = 90 - speed_to_angle_deg(end)
        as_canvas.create_arc(cx-r, cy-r, cx+r, cy+r,
                             start=sa, extent=ea - sa,
                             style="arc", outline=color, width=10, tags="static")

    draw_zone(0, 120, "lime")
    draw_zone(120, 160, "yellow")
    draw_zone(160, 180, "red")

    for speed in range(0, TOTAL_SPEED + 1, 20):
        a_rad = math.radians(speed_to_angle_deg(speed))
        gx_out = cx + r * math.cos(a_rad)
        gy_out = cy + r * math.sin(a_rad)
        gx_in  = cx + (r - 14) * math.cos(a_rad)
        gy_in  = cy + (r - 14) * math.sin(a_rad)
        gx_txt = cx + (r - 34) * math.cos(a_rad)
        gy_txt = cy + (r - 34) * math.sin(a_rad)

        ox, oy = rot90(gx_out, gy_out, cx, cy)
        ix, iy = rot90(gx_in,  gy_in,  cx, cy)
        tx, ty = rot90(gx_txt, gy_txt, cx, cy)

        as_canvas.create_line(ix, iy, ox, oy, fill="white", width=2, tags="static")
        as_canvas.create_text(tx, ty, text=str(speed), fill="white",
                              font=("Arial", max(9, GR // 14)), angle=90, tags="static")

    lx, ly = rot90(cx, cy + GR + 20, cx, cy)
    as_canvas.create_text(lx, ly, text="AIRSPEED", fill="white",
                          font=("Arial", max(9, GR // 11), "bold"),
                          angle=90, tags="static")

def draw_airspeed_needle(speed):
    as_canvas.delete("needle")
    cx, cy, r = GCX, GCY, GR
    a_rad = math.radians(speed_to_angle_deg(speed))
    gx = cx + (r - 28) * math.cos(a_rad)
    gy = cy + (r - 28) * math.sin(a_rad)
    nx, ny = rot90(gx, gy, cx, cy)
    as_canvas.create_line(cx, cy, nx, ny, fill="red", width=3, tags="needle")
    as_canvas.create_oval(cx-5, cy-5, cx+5, cy+5, fill="white", tags="needle")

draw_airspeed_static()

# ================= ATTITUDE =================

att_canvas = tk.Canvas(root, width=GAUGE_W, height=GAUGE_H, bg="black", highlightthickness=0)
att_canvas.place(x=0, y=GAUGE_H)

def draw_attitude(p, r):
    att_canvas.delete("all")
    cx, cy = GCX, GCY
    radius = GR
    offset = int(p * 2)

    horizon_g = cy + offset
    rad_r = math.radians(r)
    margin = GAUGE_W + GAUGE_H

    hx1_g = cx - margin * math.cos(rad_r)
    hy1_g = horizon_g - margin * math.sin(rad_r)
    hx2_g = cx + margin * math.cos(rad_r)
    hy2_g = horizon_g + margin * math.sin(rad_r)

    sx = math.sin(rad_r)
    sy = -math.cos(rad_r)  # omhoog in gauge (lucht)

    ax1_g = hx1_g + margin * sx
    ay1_g = hy1_g + margin * sy
    ax2_g = hx2_g + margin * sx
    ay2_g = hy2_g + margin * sy

    def r90(gx, gy): return rot90(gx, gy, cx, cy)

    p1 = r90(hx1_g, hy1_g)
    p2 = r90(hx2_g, hy2_g)
    p3 = r90(ax2_g, ay2_g)
    p4 = r90(ax1_g, ay1_g)

    # Grond achtergrond
    att_canvas.create_rectangle(0, 0, GAUGE_W, GAUGE_H, fill="#8B4513", outline="")
    # Lucht polygon
    att_canvas.create_polygon(p1, p2, p3, p4, fill="#4da6ff", outline="")

    # Horizon-lijn
    hc1 = r90(hx1_g, hy1_g)
    hc2 = r90(hx2_g, hy2_g)
    att_canvas.create_line(hc1[0], hc1[1], hc2[0], hc2[1], fill="white", width=5)

    # Mask: zwart buiten de cirkel
    cover = max(GAUGE_W, GAUGE_H)
    att_canvas.create_oval(cx - radius - cover, cy - radius - cover,
                           cx + radius + cover, cy + radius + cover,
                           outline="black", width=cover * 2)

    # Buitenste cirkel
    att_canvas.create_oval(cx-radius, cy-radius, cx+radius, cy+radius,
                           outline="white", width=3)

    # Vast vliegtuigsymbool - beweegt niet mee met horizon
    lw = 4
    wl = int(GR * 0.40)
    wg = 12
    wt = max(6, GR // 14)
    att_canvas.create_line(cx, cy - wg, cx, cy - wl, fill="yellow", width=lw)
    att_canvas.create_line(cx - wt, cy - wl, cx + wt, cy - wl, fill="yellow", width=lw)
    att_canvas.create_line(cx, cy + wg, cx, cy + wl, fill="yellow", width=lw)
    att_canvas.create_line(cx - wt, cy + wl, cx + wt, cy + wl, fill="yellow", width=lw)
    att_canvas.create_oval(cx - 4, cy - 4, cx + 4, cy + 4, fill="yellow", outline="")
    att_canvas.create_line(cx + wg, cy, cx + wg + 12, cy, fill="yellow", width=lw)

    lx, ly = rot90(cx, cy + radius + 20, cx, cy)
    att_canvas.create_text(lx, ly, text="ATTITUDE", fill="white",
                           font=("Arial", max(9, GR // 11), "bold"), angle=90)

# ================= COMPASS =================

comp_canvas = tk.Canvas(root, width=GAUGE_W, height=GAUGE_H, bg="black", highlightthickness=0)
comp_canvas.place(x=0, y=GAUGE_H * 2)

def draw_compass(heading):
    comp_canvas.delete("all")
    cx, cy, r = GCX, GCY, GR

    comp_canvas.create_oval(cx-r, cy-r, cx+r, cy+r, outline="white", width=3)

    for deg in range(0, 360, 5):
        a_deg = deg - heading - 90
        a_rad = math.radians(a_deg)

        if deg % 30 == 0:
            inner = r - 22; lw = 3
        elif deg % 10 == 0:
            inner = r - 15; lw = 2
        else:
            inner = r - 10; lw = 1

        gx1 = cx + inner * math.cos(a_rad)
        gy1 = cy + inner * math.sin(a_rad)
        gx2 = cx + r * math.cos(a_rad)
        gy2 = cy + r * math.sin(a_rad)

        x1, y1 = rot90(gx1, gy1, cx, cy)
        x2, y2 = rot90(gx2, gy2, cx, cy)
        comp_canvas.create_line(x1, y1, x2, y2, fill="white", width=lw)

        if deg % 30 == 0:
            tx_g = cx + (r - 42) * math.cos(a_rad)
            ty_g = cy + (r - 42) * math.sin(a_rad)
            tx, ty = rot90(tx_g, ty_g, cx, cy)
            label = {0: "N", 90: "O", 180: "Z", 270: "W"}.get(deg, str(deg))
            color = "yellow" if deg in [0, 90, 180, 270] else "white"
            comp_canvas.create_text(tx, ty, text=label, fill=color,
                                    font=("Arial", max(9, r // 10), "bold"), angle=90)

    tip_g   = (cx, cy - int(r * 0.55))
    left_g  = (cx - 8, cy - int(r * 0.37))
    right_g = (cx + 8, cy - int(r * 0.37))
    down_g  = (cx, cy + int(r * 0.37))

    tip   = rot90(*tip_g,   cx, cy)
    left  = rot90(*left_g,  cx, cy)
    right = rot90(*right_g, cx, cy)
    down  = rot90(*down_g,  cx, cy)

    comp_canvas.create_polygon(tip, left, right, fill="red")
    comp_canvas.create_line(down[0], down[1], tip[0], tip[1], fill="red", width=3)

    lx, ly = rot90(cx, cy + r + 20, cx, cy)
    comp_canvas.create_text(lx, ly, text="HEADING", fill="white",
                            font=("Arial", max(9, GR // 11), "bold"), angle=90)

# ================= MQTT =================

client = mqtt.Client()

def on_message(mqttclient, userdata, msg):
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

# ================= UPDATE LOOP =================

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
root.mainloop()