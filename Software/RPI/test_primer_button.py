import time

import lgpio


PRIMER_PIN = 18


def main():
    chip = lgpio.gpiochip_open(0)
    lgpio.gpio_claim_input(chip, PRIMER_PIN, lgpio.SET_PULL_UP)

    print(f"GPIO{PRIMER_PIN} test gestart. Stop met Ctrl+C.")

    try:
        while True:
            print(lgpio.gpio_read(chip, PRIMER_PIN))
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nGestopt.")
    finally:
        lgpio.gpiochip_close(chip)


if __name__ == "__main__":
    main()
