


### 🧱 Stap 1 — Verplaats je XML-bestand

Neem dit bestand:

```
udp_out.xml
```

en zet het **hier**:

```
C:/Users/user/FlightGear/Downloads/fgdata_2024_1/Protocol/udp_out.xml
```

⚠️ De naam **udp_out.xml** onthouden.

---

### 🧱 Stap 2 — Start FlightGear ZONDER pad en ZONDER .xml

Gebruik nu **exact dit**:

```powershell
.\fgfs.exe --generic=socket,out,2,127.0.0.1,5500,udp,udp_out
```

🔑 Let op:
✅ Waar moet je staan in de terminal?

Op jouw pc (zie eerdere output) staat FlightGear hier:

```powershell
C:\Program Files\FlightGear 2024.1\bin
```

* laatste argument = `udp_out`
* **geen** `.xml`
* **geen** pad

---

## 🧱 Stap 3 — run Python-script 








