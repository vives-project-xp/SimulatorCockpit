from PIL import Image, ImageDraw, ImageFont

img = Image.open(r"c:\Project exp\Project Experience 1.2\SimulatorCockpit\Documentatie\handleiding\paneel.jpg")
W, H = img.size
draw = ImageDraw.Draw(img)

try:
    font = ImageFont.truetype("arial.ttf", 42)
except:
    font = ImageFont.load_default()

buttons = [
    ("Primer",            int(W * 0.080), int(H * 0.452)),
    ("Battery 1",         int(W * 0.165), int(H * 0.325)),
    ("Alternate Battery", int(W * 0.245), int(H * 0.325)),
    ("Switch 1",          int(W * 0.160), int(H * 0.512)),
    ("Switch 2",          int(W * 0.195), int(H * 0.512)),
    ("Switch 3",          int(W * 0.229), int(H * 0.512)),
    ("Sleutel",           int(W * 0.285), int(H * 0.495)),
    ("Fuel Mixer",        int(W * 0.432), int(H * 0.348)),  # rechtsboven van de 6
    ("Carb Heater",       int(W * 0.650), int(H * 0.335)),
]

labels = [
    ("Primer",            int(W * 0.020), int(H * 0.820)),
    ("Battery 1",         int(W * 0.070), int(H * 0.875)),
    ("Alternate Battery", int(W * 0.195), int(H * 0.875)),
    ("Switch 1",          int(W * 0.060), int(H * 0.930)),
    ("Switch 2",          int(W * 0.180), int(H * 0.930)),
    ("Switch 3",          int(W * 0.300), int(H * 0.930)),
    ("Sleutel",           int(W * 0.400), int(H * 0.875)),
    ("Fuel Mixer",        int(W * 0.510), int(H * 0.875)),
    ("Carb Heater",       int(W * 0.630), int(H * 0.875)),
]

colors = {
    "Primer":            "#FF6B35",
    "Battery 1":         "#FFD700",
    "Alternate Battery": "#FFD700",
    "Switch 1":          "#00CFFF",
    "Switch 2":          "#00CFFF",
    "Switch 3":          "#00CFFF",
    "Sleutel":           "#FF4444",
    "Fuel Mixer":        "#00FF88",
    "Carb Heater":       "#FF44FF",
}

label_map = {name: (lx, ly) for name, lx, ly in labels}
DOT_R = 20
LINE_W = 5
PAD = 10

for name, bx, by in buttons:
    lx, ly = label_map[name]
    color  = colors[name]

    draw.ellipse([bx-DOT_R, by-DOT_R, bx+DOT_R, by+DOT_R], outline=color, width=5)
    draw.line([bx, by, lx+10, ly], fill=color, width=LINE_W)

    bbox = draw.textbbox((lx, ly), name, font=font)
    draw.rectangle([bbox[0]-PAD, bbox[1]-PAD, bbox[2]+PAD, bbox[3]+PAD], fill=(0,0,0,200))
    draw.text((lx, ly), name, fill=color, font=font)

out = r"c:\Project exp\Project Experience 1.2\SimulatorCockpit\Documentatie\handleiding\paneel_annotated.jpg"
img.save(out, quality=95)
print("Klaar")
