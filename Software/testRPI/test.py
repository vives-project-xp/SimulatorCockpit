import tkinter as tk
from tkinter import ttk
import paho.mqtt.client as mqtt

BROKER = "localhost"

TOPIC_THROTTLE = "cockpit/input/throttle"
TOPIC_BATTERY = "cockpit/input/battery"
TOPIC_MONITOR = "#"

battery_state = 0

# MQTT
client = mqtt.Client()

def on_message(client, userdata, msg):
    message = msg.payload.decode()
    log.insert(tk.END, f"{msg.topic} : {message}\n")
    log.see(tk.END)

client.on_message = on_message
client.connect(BROKER, 1883, 60)
client.subscribe(TOPIC_MONITOR)
client.loop_start()


# WINDOW
root = tk.Tk()
root.title("COCKPIT CONTROL")
root.attributes("-fullscreen", True)
root.configure(bg="#0f172a")


# STYLE
style = ttk.Style()
style.theme_use("clam")

style.configure("TScale", background="#0f172a")
style.configure("TFrame", background="#0f172a")
style.configure("TLabel", background="#0f172a", foreground="white")


# MAIN FRAME
main = ttk.Frame(root, padding=30)
main.grid(row=0, column=0, sticky="nsew")

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

# TITLE
title = tk.Label(main,
                 text="COCKPIT CONTROL PANEL",
                 font=("Arial", 42, "bold"),
                 bg="#0f172a",
                 fg="white")
title.grid(row=0, column=0, columnspan=2, pady=30)


# BATTERY PANEL
battery_frame = tk.Frame(main,
                         bg="#1e293b",
                         bd=3,
                         relief="ridge",
                         padx=30,
                         pady=30)

battery_frame.grid(row=1, column=0, padx=30, pady=20)

battery_title = tk.Label(battery_frame,
                         text="BATTERY",
                         font=("Arial", 26),
                         bg="#1e293b",
                         fg="white")

battery_title.pack(pady=10)


def toggle_battery():
    global battery_state
    battery_state = 1 - battery_state
    client.publish(TOPIC_BATTERY, str(battery_state))
    update_battery_ui()


def update_battery_ui():
    if battery_state == 1:
        battery_btn.config(text="ON", bg="#16a34a")
    else:
        battery_btn.config(text="OFF", bg="#dc2626")


battery_btn = tk.Button(battery_frame,
                        text="OFF",
                        command=toggle_battery,
                        font=("Arial", 28, "bold"),
                        width=10,
                        height=2,
                        bg="#dc2626",
                        fg="white",
                        activebackground="#ef4444",
                        relief="flat")

battery_btn.pack(pady=20)


# THROTTLE PANEL
throttle_frame = tk.Frame(main,
                          bg="#1e293b",
                          bd=3,
                          relief="ridge",
                          padx=30,
                          pady=30)

throttle_frame.grid(row=1, column=1, padx=30, pady=20)

throttle_title = tk.Label(throttle_frame,
                          text="THROTTLE",
                          font=("Arial", 26),
                          bg="#1e293b",
                          fg="white")

throttle_title.pack(pady=10)

throttle_label = tk.Label(throttle_frame,
                          text="0 %",
                          font=("Arial", 28),
                          bg="#1e293b",
                          fg="#38bdf8")

throttle_label.pack(pady=10)


def send_throttle(value):
    throttle_value = round(float(value), 2)
    client.publish(TOPIC_THROTTLE, str(throttle_value))
    percent = int(throttle_value * 100)
    throttle_label.config(text=f"{percent} %")


throttle_slider = ttk.Scale(throttle_frame,
                            from_=0,
                            to=1,
                            orient="horizontal",
                            length=400,
                            command=send_throttle)

throttle_slider.pack(pady=20)


# LOG PANEL
log_frame = tk.Frame(main,
                     bg="#1e293b",
                     bd=3,
                     relief="ridge",
                     padx=20,
                     pady=20)

log_frame.grid(row=2, column=0, columnspan=2, pady=30)

log_title = tk.Label(log_frame,
                     text="MQTT LOG",
                     font=("Arial", 20),
                     bg="#1e293b",
                     fg="white")

log_title.pack(pady=10)

log = tk.Text(log_frame,
              height=12,
              width=100,
              bg="#020617",
              fg="#22c55e",
              insertbackground="white",
              font=("Consolas", 12),
              bd=0)

log.pack()


root.mainloop()
