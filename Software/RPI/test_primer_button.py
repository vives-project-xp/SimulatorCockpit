import time

import lgpio


PRIMER_PIN = 16


def main():
    chip = lgpio.gpiochip_open(0)
    lgpio.gpio_claim_input(chip, PRIMER_PIN, lgpio.SET_PULL_UP)

    print(f"GPIO{PRIMER_PIN} test gestart. Stop met Ctrl+C.")
    last_value = lgpio.gpio_read(chip, PRIMER_PIN)
    print(last_value)

    try:
        while True:
            value = lgpio.gpio_read(chip, PRIMER_PIN)
            if value != last_value:
                print(value)
                last_value = value
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nGestopt.")
    finally:
        lgpio.gpiochip_close(chip)


if __name__ == "__main__":
    main()
