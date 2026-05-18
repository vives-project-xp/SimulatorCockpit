import time

import lgpio


PRIMER_PIN = 18
POLL_INTERVAL_SECONDS = 0.01
DEBOUNCE_SECONDS = 0.05


def main():
    chip = lgpio.gpiochip_open(0)
    lgpio.gpio_claim_input(chip, PRIMER_PIN, lgpio.SET_PULL_UP)

    last_gpio_value = lgpio.gpio_read(chip, PRIMER_PIN)
    last_change_time = time.monotonic()
    press_count = 0

    print(f"Primer test gestart op GPIO{PRIMER_PIN}.")
    print("Druk op de knop. Stop met Ctrl+C.")
    print("Verwacht gedrag: idle = 1, ingedrukt = 0.")

    try:
        while True:
            gpio_value = lgpio.gpio_read(chip, PRIMER_PIN)

            if gpio_value != last_gpio_value:
                now = time.monotonic()
                if now - last_change_time >= DEBOUNCE_SECONDS:
                    last_change_time = now
                    last_gpio_value = gpio_value

                    if gpio_value == 0:
                        press_count += 1
                        print(f"[{press_count}] INGEDRUKT  gpio={gpio_value}")
                    else:
                        print(f"    LOSGELATEN gpio={gpio_value}")

            time.sleep(POLL_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        print(f"\nGestopt. Gedetecteerde drukken: {press_count}")
    finally:
        lgpio.gpiochip_close(chip)


if __name__ == "__main__":
    main()
