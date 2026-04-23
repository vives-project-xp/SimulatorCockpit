# Raspberry Pi 5 pinnen schema

Gebaseerd op `Software/testRPI/Nieuweknoppen.py`.

Alle inputs gebruiken `lgpio.SET_PULL_UP`. Sluit daarom elke knop/schakelaar aan tussen de GPIO-pin en GND. De interne pull-up houdt de pin hoog; bij contact naar GND wordt de pin laag.

## Aansluitlijst

| Functie | Variabele in code | MQTT-topic | BCM/GPIO | Fysieke pin op 40-pin header | Aansluiting |
| --- | --- | --- | --- | --- | --- |
| Battery | `BUTTON_PIN` | `cockpit/input/battery` | GPIO17 | pin 11 | schakelaar tussen pin 11 en GND |
| Carb heat | `TOGGLE_BUTTON_PIN` | `cockpit/input/carb-heat` | GPIO27 | pin 13 | schakelaar tussen pin 13 en GND |
| Master alternator | `EXTRA_BUTTON_PIN` | `cockpit/input/alt` | GPIO22 | pin 15 | schakelaar tussen pin 15 en GND |
| Magnetos sleutel | `SLEUTEL_PIN` | `cockpit/input/magnetos/sleutel` | GPIO23 | pin 16 | schakelaar tussen pin 16 en GND |
| Primer | `PRIMER_PIN` | `cockpit/input/primer` | GPIO18 | pin 12 | drukknop tussen pin 12 en GND |
| Magnetos switch 1 | `SWITCH_1_PIN` | `cockpit/input/magnetos/switch1` | GPIO24 | pin 18 | schakelaar tussen pin 18 en GND |
| Magnetos switch 2 | `SWITCH_2_PIN` | `cockpit/input/magnetos/switch2` | GPIO25 | pin 22 | schakelaar tussen pin 22 en GND |
| Magnetos switch 3 | `SWITCH_3_PIN` | `cockpit/input/magnetos/switch3` | GPIO5 | pin 29 | schakelaar tussen pin 29 en GND |

## Bruikbare GND-pinnen

Je mag eender welke GND-pin gebruiken. Handige GND-pinnen op de 40-pin header zijn:

| Fysieke pin | Functie |
| --- | --- |
| pin 6 | GND |
| pin 9 | GND |
| pin 14 | GND |
| pin 20 | GND |
| pin 25 | GND |
| pin 30 | GND |
| pin 34 | GND |
| pin 39 | GND |

## Visueel overzicht

```text
Raspberry Pi 5 40-pin header

Linker rij                 Rechter rij
------------------------------------------------
 1  3V3                    2  5V
 3  GPIO2                  4  5V
 5  GPIO3                  6  GND
 7  GPIO4                  8  GPIO14
 9  GND                   10  GPIO15
11  GPIO17  Battery       12  GPIO18  Primer
13  GPIO27  Carb heat     14  GND
15  GPIO22  Master alt    16  GPIO23  Magnetos sleutel
17  3V3                   18  GPIO24  Magnetos switch 1
19  GPIO10                20  GND
21  GPIO9                 22  GPIO25  Magnetos switch 2
23  GPIO11                24  GPIO8
25  GND                   26  GPIO7
27  ID_SD                 28  ID_SC
29  GPIO5   Mag. switch 3 30  GND
31  GPIO6                 32  GPIO12
33  GPIO13                34  GND
35  GPIO19                36  GPIO16
37  GPIO26                38  GPIO20
39  GND                   40  GPIO21
```

## Belangrijk

Gebruik geen 5V of 3V3 voor deze schakelaars. Door de interne pull-up is alleen een verbinding van GPIO naar GND nodig.
