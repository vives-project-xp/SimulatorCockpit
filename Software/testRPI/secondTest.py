import tkinter as tk
import paho.mqtt.client as mqtt
import math

BROKER = "localhost"

TOPIC_AIRSPEED = "cockpit/airspeed"
TOPIC_HEADING = "cockpit/heading"
TOPIC_ATTITUDE = "cockpit/attitude"
TOPIC_MONITOR = "#"

airspeed_value = 0.0
heading_value = 0.0
display_heading = 0.0
pitch = 0.0
roll = 0.0

# ---------------- WINDOW ----------------

root = tk.Tk()
root.title("COCKPIT")
root.attributes("-fullscreen", True)
root.configure(bg="black")

screen_w = root.winfo_screenwidth()
screen_h = root.winfo_screenheight()

# 👉 ROTATED LAYOUT (belangrijk)
GAUGE_SIZE = min(screen_h // 3, screen_w)
CENTER = GAUGE_SIZE // 2
RADIUS = int(GAUGE_SIZE * 0.42)
TOTAL_SPEED = 180

main_frame = tk.Frame(root, bg="black")
main_frame.pack(fill="both", expand=True)

# 3 rijen (verticale layout → lijkt gedraaid)
main_frame.rowconfigure(0, weight=1)
main_frame.rowconfigure(1, weight=1)
main_frame.rowconfigure(2, weight=1)

# ================= AIRSPEED =================

airspeed_canvas = tk.Canvas(main_frame, bg="black", highlightthickness=0)
airspeed_canvas.grid(row=0, column=0, sticky="nsew")

def speed_to_angle(speed):
    return -210 + (speed / TOTAL_SPEED) * 240

def draw_airspeed():
    airspeed_canvas.delete("all")

    airspeed_canvas.create_oval(
        CENTER-RADIUS, CENTER-RADIUS,
        CENTER+RADIUS, CENTER+RADIUS,
        outline="white", width=4
    )

    def zone(s, e, c):
        airspeed_canvas.create_arc(
            CENTER-RADIUS, CENTER-RADIUS,
            CENTER+RADIUS, CENTER+RADIUS,
            start=speed_to_angle(s)+180,
            extent=speed_to_angle(e)-speed_to_angle(s),
            style="arc",
            outline=c,
            width=15
        )

    zone(0,120,"lime")
    zone(120,160,"yellow")
    zone(160,180,"red")

    for s in range(0,181,20):
        a = math.radians(speed_to_angle(s))
        x = CENTER + (RADIUS-40)*math.cos(a)
        y = CENTER + (RADIUS-40)*math.sin(a)
        airspeed_canvas.create_text(x,y,text=s,fill="white")

def draw_airspeed_needle(v):
    airspeed_canvas.delete("needle")
    a = math.radians(speed_to_angle(v))
    x = CENTER + (RADIUS-50)*math.cos(a)
    y = CENTER + (RADIUS-50)*math.sin(a)
    airspeed_canvas.create_line(CENTER,CENTER,x,y,fill="red",width=3,tags="needle")

draw_airspeed()

# ================= ATTITUDE =================

att_canvas = tk.Canvas(main_frame, bg="black", highlightthickness=0)
att_canvas.grid(row=1, column=0, sticky="nsew")

def draw_attitude(pitch, roll):
    att_canvas.delete("all")

    # achtergrond (lucht/grond)
    for y in range(GAUGE_SIZE):
        color = "#4da6ff" if y < CENTER + pitch*3 else "#8B4513"
        att_canvas.create_line(0, y, GAUGE_SIZE, y, fill=color)

    rad = math.radians(roll)

    def rot(x,y):
        dx = x-CENTER
        dy = y-CENTER
        return (
            CENTER + dx*math.cos(rad) - dy*math.sin(rad),
            CENTER + dx*math.sin(rad) + dy*math.cos(rad)
        )

    x1,y1 = rot(0, CENTER + pitch*3)
    x2,y2 = rot(GAUGE_SIZE, CENTER + pitch*3)

    # dikke horizonlijn
    att_canvas.create_line(x1,y1,x2,y2,fill="white",width=6)

    # vliegtuig (wit pijltje)
    att_canvas.create_line(CENTER-20,CENTER,CENTER+20,CENTER,fill="white",width=4)
    att_canvas.create_line(CENTER,CENTER-10,CENTER,CENTER+10,fill="white",width=4)

    # mask buiten cirkel (maakt echte ronde gauge)
    att_canvas.create_oval(
        CENTER-RADIUS, CENTER-RADIUS,
        CENTER+RADIUS, CENTER+RADIUS,
        outline="white",
        width=3
    )

    # zwarte hoeken (mask)
    att_canvas.create_rectangle(0,0,GAUGE_SIZE,GAUGE_SIZE, outline="", fill="", tags="clip")

    # cirkel overlay (clipping effect)
    att_canvas.create_oval(
        CENTER-RADIUS, CENTER-RADIUS,
        CENTER+RADIUS, CENTER+RADIUS,
        outline="white",
        width=3
    )

# ================= COMPASS =================

compass_canvas = tk.Canvas(main_frame, bg="black", highlightthickness=0)
compass_canvas.grid(row=2, column=0, sticky="nsew")

def draw_compass(h):
    compass_canvas.delete("all")

    compass_canvas.create_oval(
        CENTER-RADIUS, CENTER-RADIUS,
        CENTER+RADIUS, CENTER+RADIUS,
        outline="white", width=3
    )

    for d in range(0,360,10):
        a = math.radians(d - h - 90)

        x = CENTER + (RADIUS-30)*math.cos(a)
        y = CENTER + (RADIUS-30)*math.sin(a)

        if d==0: txt,col="N","yellow"
        elif d==90: txt,col="O","yellow"
        elif d==180: txt,col="Z","yellow"
        elif d==270: txt,col="W","yellow"
        else: txt,col=str(d),"white"

        compass_canvas.create_text(x,y,text=txt,fill=col)

    compass_canvas.create_polygon(
        CENTER, CENTER-90,
        CENTER-10, CENTER-60,
        CENTER+10, CENTER-60,
        fill="red"
    )

# ================= UPDATE =================

def update_ui():
    global display_heading

    diff = heading_value - display_heading
    if diff > 180: diff -= 360
    if diff < -180: diff += 360

    display_heading += diff * 0.15

    draw_airspeed_needle(airspeed_value)
    draw_attitude(pitch, roll)
    draw_compass(display_heading)

    root.after(50, update_ui)

update_ui()

# ================= MQTT =================

client = mqtt.Client()

def on_message(client, userdata, msg):
    global airspeed_value, heading_value, pitch, roll

    m = msg.payload.decode()

    if msg.topic == TOPIC_AIRSPEED:
        airspeed_value = float(m)

    elif msg.topic == TOPIC_HEADING:
        heading_value = float(m)

    elif msg.topic == TOPIC_ATTITUDE:
        try:
            p, r = m.split(",")
            pitch = float(p)
            roll = float(r)
        except:
            pass

client.on_message = on_message
client.connect(BROKER,1883,60)
client.subscribe(TOPIC_MONITOR)
client.loop_start()

root.mainloop()