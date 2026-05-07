# Software Architectuur — Simulator Cockpit

## Overzicht

Het systeem bestaat uit 3 grote onderdelen die via **MQTT** met elkaar communiceren:
- **Raspberry Pi** — leest knoppen/schakelaars en toont de cockpit display
- **MQTT Broker** — centrale berichtenbus (IP: `10.10.229.190`)
- **PC (FlightGear)** — de vluchtsimulatorsoftware

---

## Architectuurschema

```mermaid
flowchart TD

    %% ─── HARDWARE INPUTS ───
    subgraph HW["🎮 Hardware Inputs (cockpit)"]
        direction TB
        BAT["🔋 Battery schakelaar\nGPIO 17"]
        CARB["🌡️ Carb-heat schakelaar\nGPIO 27"]
        ALT["✈️ Alt schakelaar\nGPIO 22"]
        SLEUTEL["🔑 Sleutel (magneto)\nGPIO 23"]
        PRIMER["💉 Primer knop\nGPIO 18"]
        SW1["⚡ Switch 1 (magneto)\nGPIO 24"]
        SW2["⚡ Switch 2 (magneto)\nGPIO 25"]
        SW3["⚡ Switch 3 (magneto)\nGPIO 5"]
        FUEL["⛽ Fuelmixer schakelaar\nGPIO 6"]
        THROTTLE["🎚️ Throttle\n(potentiometer)"]
    end

    %% ─── RASPBERRY PI SCRIPTS ───
    subgraph RPI["🖥️ Raspberry Pi"]
        direction TB
        BUTTONS["buttons.py\nLeest GPIO inputs"]
        DISPLAY["interface.py\nTkinter display\n(Airspeed · Attitude · Heading)"]
    end

    %% ─── MQTT BROKER ───
    subgraph MQTT["📡 MQTT Broker\n10.10.229.190 : 1883"]
        direction TB
        IN_TOPICS["INPUT topics\n──────────────\ncockpit/input/battery\ncockpit/input/carb-heat\ncockpit/input/alt\ncockpit/input/primer\ncockpit/input/magnetos/sleutel\ncockpit/input/magnetos/switch1\ncockpit/input/magnetos/switch2\ncockpit/input/magnetos/switch3\ncockpit/input/fuelmixer\ncockpit/input/throttle"]
        OUT_TOPICS["OUTPUT topics\n──────────────\ncockpit/airspeed\ncockpit/heading\ncockpit/attitude"]
    end

    %% ─── PC ───
    subgraph PC["💻 PC (FlightGear)"]
        direction TB
        BRIDGE["udp_in_mqtt_tcp_out_mqtt.py\nBrug tussen MQTT en FlightGear"]
        FG["FlightGear\nVluchtsimulatorsoftware"]
    end

    %% ─── VERBINDINGEN ───

    HW --> BUTTONS

    BUTTONS -->|"publiceert naar"| IN_TOPICS

    IN_TOPICS -->|"ontvangt"| BRIDGE
    BRIDGE -->|"TCP :5600\nbattery · alt · carb-heat\nprimer · magnetos · throttle"| FG

    FG -->|"UDP :5500\nairspeed · heading\npitch · roll"| BRIDGE
    BRIDGE -->|"publiceert naar"| OUT_TOPICS

    OUT_TOPICS -->|"ontvangt"| DISPLAY

    %% ─── KLEUREN ───
    style HW fill:#2d4a6e,color:#ffffff,stroke:#4a90d9
    style RPI fill:#1a5c1a,color:#ffffff,stroke:#4caf50
    style MQTT fill:#6e3d00,color:#ffffff,stroke:#ff9800
    style PC fill:#5c1a1a,color:#ffffff,stroke:#f44336
    style IN_TOPICS fill:#4a3000,color:#ffcc80,stroke:#ff9800
    style OUT_TOPICS fill:#4a3000,color:#ffcc80,stroke:#ff9800
    style BUTTONS fill:#0d3d0d,color:#a5d6a7,stroke:#4caf50
    style DISPLAY fill:#0d3d0d,color:#a5d6a7,stroke:#4caf50
    style BRIDGE fill:#3d0d0d,color:#ef9a9a,stroke:#f44336
    style FG fill:#3d0d0d,color:#ef9a9a,stroke:#f44336
```

---

## Dataflow uitgelegd

### ➡️ Input: Cockpit → FlightGear

| Stap | Van | Naar | Protocol |
|------|-----|------|----------|
| 1 | Hardware knoppen/schakelaars | `buttons.py` (GPIO read) | GPIO |
| 2 | `buttons.py` | MQTT Broker (input topics) | MQTT publish |
| 3 | MQTT Broker | `udp_in_mqtt_tcp_out_mqtt.py` | MQTT subscribe |
| 4 | Bridge script | FlightGear | TCP poort 5600 |

### ⬅️ Output: FlightGear → Cockpit display

| Stap | Van | Naar | Protocol |
|------|-----|------|----------|
| 1 | FlightGear | Bridge script | UDP poort 5500 |
| 2 | Bridge script | MQTT Broker (output topics) | MQTT publish |
| 3 | MQTT Broker | `interface.py` | MQTT subscribe |
| 4 | `interface.py` | Scherm (Tkinter) | Tekent gauges |

---

## MQTT Topics

### Input topics (Pi → PC)

| Topic | Waarden | Omschrijving |
|-------|---------|--------------|
| `cockpit/input/battery` | `0` / `1` | Batterijschakelaar |
| `cockpit/input/carb-heat` | `0` / `1` | Carburateur verwarming |
| `cockpit/input/alt` | `0` / `1` | Alternatieve schakelaar |
| `cockpit/input/primer` | `0` / `1` | Primer knop (toggle) |
| `cockpit/input/magnetos/sleutel` | `0` / `1` | Contactsleutel (omgekeerd) |
| `cockpit/input/magnetos/switch1` | `0` / `1` | Magneto schakelaar 1 |
| `cockpit/input/magnetos/switch2` | `0` / `1` | Magneto schakelaar 2 |
| `cockpit/input/magnetos/switch3` | `0` / `1` | Magneto schakelaar 3 |
| `cockpit/input/fuelmixer` | `0` / `1` | Brandstofmengschakelaar |
| `cockpit/input/throttle` | `0.0` – `1.0` | Gashandel positie |

### Output topics (PC → Pi)

| Topic | Waarden | Omschrijving |
|-------|---------|--------------|
| `cockpit/airspeed` | `float` | Luchtsnelheid (km/u) |
| `cockpit/heading` | `0` – `360` | Kompasrichting (graden) |
| `cockpit/attitude` | `pitch,roll` | Vliegtuighouding |
