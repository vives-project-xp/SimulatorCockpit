import lgpio
import paho.mqtt.client as mqtt
import time

# ========================
# CONFIG
# ========================
BROKER = "localhost"

TOPIC_BATTERY = "cockpit/input/battery"
TOPIC_TOGGLE = "cockpit/input/carb-heat"   # <-- aanpassen
TOPIC_EXTRA = "cockpit/input/alt"          # <-- alt
TOPIC_SLEUTEL = "cockpit/input/sleutel"    # <-- nieuw
TOPIC_PRIMER = "cockpit/input/primer"

TOPIC_SWITCH_1 = "cockpit/input/switch1"
TOPIC_SWITCH_2 = "cockpit/input/switch2"
TOPIC_SWITCH_3 = "cockpit/input/switch3"

BUTTON_PIN = 17
TOGGLE_BUTTON_PIN = 27
EXTRA_BUTTON_PIN = 22
SLEUTEL_PIN = 23
PRIMER_PIN = 18

SWITCH_1_PIN = 24
SWITCH_2_PIN = 25
SWITCH_3_PIN = 5

# ========================
# GPIO SETUP (lgpio)
# ========================
chip = lgpio.gpiochip_open(0)  # open gpiochip0

# Batterij knop
lgpio.gpio_claim_input(chip, BUTTON_PIN, lgpio.SET_PULL_UP)

# Toggle knop (gewone knop)
lgpio.gpio_claim_input(chip, TOGGLE_BUTTON_PIN, lgpio.SET_PULL_UP)

# Extra gewone knop
lgpio.gpio_claim_input(chip, EXTRA_BUTTON_PIN, lgpio.SET_PULL_UP)

# Sleutel knop (momentary)
lgpio.gpio_claim_input(chip, SLEUTEL_PIN, lgpio.SET_PULL_UP)

# Primer knop
lgpio.gpio_claim_input(chip, PRIMER_PIN, lgpio.SET_PULL_UP)

# Extra schakelaars
lgpio.gpio_claim_input(chip, SWITCH_1_PIN, lgpio.SET_PULL_UP)
lgpio.gpio_claim_input(chip, SWITCH_2_PIN, lgpio.SET_PULL_UP)
lgpio.gpio_claim_input(chip, SWITCH_3_PIN, lgpio.SET_PULL_UP)

# ========================
# MQTT SETUP
# ========================
client = mqtt.Client()
client.connect(BROKER, 1883, 60)
client.loop_start()

print("Battery + toggle + extra + sleutel + primer + 3 switches input started (lgpio)...")

# ========================
# STATES
# ========================
last_battery_state = None
last_toggle_state = None
last_extra_state = None
last_sleutel_state = None

primer_state = 0
last_primer_gpio = 1

last_switch_1_state = None
last_switch_2_state = None
last_switch_3_state = None

try:
    while True:
        # ========================
        # 1) BATTERY BUTTON
        # ========================
        current_battery_gpio = lgpio.gpio_read(chip, BUTTON_PIN)
        battery_state = 1 if current_battery_gpio == 1 else 0

        if battery_state != last_battery_state:
            client.publish(TOPIC_BATTERY, str(battery_state))
            print("Battery:", battery_state)
            last_battery_state = battery_state

        # ========================
        # 2) TOGGLE BUTTON (gewone knop)
        # ========================
        current_toggle_gpio = lgpio.gpio_read(chip, TOGGLE_BUTTON_PIN)
        toggle_state = 1 if current_toggle_gpio == 1 else 0

        if toggle_state != last_toggle_state:
            client.publish(TOPIC_TOGGLE, str(toggle_state))
            print("Carb-heat:", toggle_state)
            last_toggle_state = toggle_state

        # ========================
        # 3) EXTRA BUTTON (gewone knop)
        # ========================
        current_extra_gpio = lgpio.gpio_read(chip, EXTRA_BUTTON_PIN)
        extra_state = 1 if current_extra_gpio == 1 else 0

        if extra_state != last_extra_state:
            client.publish(TOPIC_EXTRA, str(extra_state))
            print("Alt:", extra_state)
            last_extra_state = extra_state

        # ========================
        # 4) SLEUTEL (momentary start key)
        # ========================
        current_sleutel_gpio = lgpio.gpio_read(chip, SLEUTEL_PIN)
        sleutel_state = 1 if current_sleutel_gpio == 1 else 0

        if sleutel_state != last_sleutel_state:
            client.publish(TOPIC_SLEUTEL, str(sleutel_state))
            print("Sleutel:", sleutel_state)
            last_sleutel_state = sleutel_state

        # ========================
        # 5) PRIMER (toggle bij elke druk)
        # ========================
        current_primer_gpio = lgpio.gpio_read(chip, PRIMER_PIN)

        if current_primer_gpio == 0 and last_primer_gpio == 1:
            primer_state = 0 if primer_state == 1 else 1
            client.publish(TOPIC_PRIMER, str(primer_state))
            print("Primer:", primer_state)
            time.sleep(0.2)  # debounce

        last_primer_gpio = current_primer_gpio

        # ========================
        # 6) SWITCH 1 (schakelaar)
        # ========================
        current_switch_1_gpio = lgpio.gpio_read(chip, SWITCH_1_PIN)
        switch_1_state = 1 if current_switch_1_gpio == 1 else 0

        if switch_1_state != last_switch_1_state:
            client.publish(TOPIC_SWITCH_1, str(switch_1_state))
            print("Switch 1:", switch_1_state)
            last_switch_1_state = switch_1_state

        # ========================
        # 7) SWITCH 2 (schakelaar)
        # ========================
        current_switch_2_gpio = lgpio.gpio_read(chip, SWITCH_2_PIN)
        switch_2_state = 1 if current_switch_2_gpio == 1 else 0

        if switch_2_state != last_switch_2_state:
            client.publish(TOPIC_SWITCH_2, str(switch_2_state))
            print("Switch 2:", switch_2_state)
            last_switch_2_state = switch_2_state

        # ========================
        # 8) SWITCH 3 (schakelaar)
        # ========================
        current_switch_3_gpio = lgpio.gpio_read(chip, SWITCH_3_PIN)
        switch_3_state = 1 if current_switch_3_gpio == 1 else 0

        if switch_3_state != last_switch_3_state:
            client.publish(TOPIC_SWITCH_3, str(switch_3_state))
            print("Switch 3:", switch_3_state)
            last_switch_3_state = switch_3_state

        time.sleep(0.05)

except KeyboardInterrupt:
    print("Stopping...")
    lgpio.gpiochip_close(chip)