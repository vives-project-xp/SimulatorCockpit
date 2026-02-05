import requests
import time

URL = "http://localhost:8080/json/velocities/airspeed-kt"

while True:
    r = requests.get(URL)
    print("Airspeed:", r.json()["value"])
    time.sleep(0.2)