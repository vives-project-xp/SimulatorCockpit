#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RPI_DIR="$REPO_DIR/Software/RPI"
AUTOSTART_DIR="$HOME/.config/autostart"
AUTOSTART_FILE="$AUTOSTART_DIR/cockpit-interface.desktop"

echo "[cockpit] Pi 4 installatie gestart"

if ! command -v docker >/dev/null 2>&1; then
  echo "[cockpit] Docker installeren"
  curl -fsSL https://get.docker.com -o /tmp/get-docker.sh
  sudo sh /tmp/get-docker.sh
else
  echo "[cockpit] Docker is al geinstalleerd"
fi

sudo apt-get update
sudo apt-get install -y x11-xserver-utils

sudo systemctl enable docker
sudo systemctl start docker

if ! groups "$USER" | grep -q '\bdocker\b'; then
  echo "[cockpit] Gebruiker toevoegen aan docker groep"
  sudo usermod -aG docker "$USER"
fi

echo "[cockpit] Interface image bouwen"
cd "$RPI_DIR"
sudo docker compose -f docker-compose.pi4.yml build

mkdir -p "$AUTOSTART_DIR"
cat > "$AUTOSTART_FILE" <<EOF
[Desktop Entry]
Type=Application
Name=Cockpit Interface
Exec=sh -c 'xhost +local:docker; cd "$RPI_DIR"; docker compose -f docker-compose.pi4.yml up -d'
Terminal=false
X-GNOME-Autostart-enabled=true
EOF

if [ -n "${DISPLAY:-}" ]; then
  echo "[cockpit] Interface nu starten op display $DISPLAY"
  xhost +local:docker
  sudo docker compose -f docker-compose.pi4.yml up -d
else
  echo "[cockpit] Geen DISPLAY gevonden. De interface start automatisch na desktop-login."
fi

echo
echo "[cockpit] Klaar. Reboot of log opnieuw in zodat docker group actief is."
echo "[cockpit] Logs bekijken:"
echo "  cd '$RPI_DIR'"
echo "  docker compose -f docker-compose.pi4.yml logs -f"
