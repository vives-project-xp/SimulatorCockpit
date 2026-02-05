

## ✅ ZO LOS JE HET OP (DEFINITIEF)

### 🧱 Stap 1 — Verplaats je XML-bestand

Neem dit bestand:

```
udp_out.xml
```

en zet het **hier**:

```
C:/Users/michi/FlightGear/Downloads/fgdata_2024_1/Protocol/udp_out.xml
```

⚠️ De naam **udp_out.xml** onthouden.

---

### 🧱 Stap 2 — Start FlightGear ZONDER pad en ZONDER .xml

Gebruik nu **exact dit**:

```powershell
.\fgfs.exe --generic=socket,out,2,127.0.0.1,5500,udp,udp_out
```

🔑 Let op:

* laatste argument = `udp_out`
* **geen** `.xml`
* **geen** pad

---

## 🧱 Stap 3 — Python-script (dit is al correct)

```python
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("127.0.0.1", 5500))

print("Wachten op data...")

while True:
    data, _ = sock.recvfrom(1024)
    print(data.decode(errors="ignore"))
```

Start dit **na** FlightGear.

---






