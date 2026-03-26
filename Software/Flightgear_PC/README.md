### Stap 1 — Verplaats XML-bestand

Neem deze bestanden:


 **[input_protocol.xml](xml/input_protocol.xml)**

 **[udp_out.xml](xml/udp_out.xml)**


en zet ze **hier**:

```
C:/Users/user/FlightGear/Downloads/fgdata_2024_1/Protocol
```

---

### Stap 2 — Start FlightGear 


Ga naar deze plek in je terminal:
```powershell
C:\Program Files\FlightGear 2024.1\bin
```
en voer daar dit commando uit:
```powershell
.\fgfs.exe --generic=socket,out,10,127.0.0.1,5500,udp,udp_out ^ --generic=socket,in,10,127.0.0.1,5600,tcp,input_protocol
```

---
### Stap 3 — run Python-script 

run **[udp_in_mqqt_tcp_out_mqtt.py](udp_in_mqqt_tcp_out_mqtt.py)**








