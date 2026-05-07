# FlightGear PC

Deze map bevat de pc-kant van het cockpitproject:

- `udp_in_mqqt_tcp_out_mqtt.py`: bridge tussen MQTT en FlightGear
- `xml/input_protocol.xml`: inkomend FlightGear generic input protocol
- `xml/udp_out.xml`: uitgaand FlightGear generic output protocol

## Setup

### 1. Kopieer de XML-bestanden

Kopieer deze bestanden:

- [input_protocol.xml](xml/input_protocol.xml)
- [udp_out.xml](xml/udp_out.xml)

naar:

```text
C:/Users/user/FlightGear/Downloads/fgdata_2024_1/Protocol
```

### 2. Start FlightGear

Ga in PowerShell naar:

```powershell
C:\Program Files\FlightGear 2024.1\bin
```

en start FlightGear met:

```powershell
.\fgfs.exe --generic=socket,out,20,127.0.0.1,5500,udp,udp_out ^ --generic=socket,in,20,127.0.0.1,5600,tcp,input_protocol
```

### 3. Installeer dependencies

```powershell
pip install -r requirements.txt
```

### 4. Start de bridge

```powershell
python udp_in_mqqt_tcp_out_mqtt.py
```

## Opmerking

De bridge probeert automatisch opnieuw te verbinden met FlightGear en met de MQTT broker als een van beide herstart.
