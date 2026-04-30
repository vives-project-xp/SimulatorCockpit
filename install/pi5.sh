#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RPI_DIR="$REPO_DIR/Software/RPI"

echo "[cockpit] Pi 5 installatie gestart"

if ! command -v docker >/dev/null 2>&1; then
  echo "[cockpit] Docker installeren"
  curl -fsSL https://get.docker.com -o /tmp/get-docker.sh
  sudo sh /tmp/get-docker.sh
else
  echo "[cockpit] Docker is al geinstalleerd"
fi

sudo systemctl enable docker
sudo systemctl start docker

if ! groups "$USER" | grep -q '\bdocker\b'; then
  echo "[cockpit] Gebruiker toevoegen aan docker groep"
  sudo usermod -aG docker "$USER"
fi

if [ ! -e /dev/gpiochip0 ]; then
  echo "[cockpit] WAARSCHUWING: /dev/gpiochip0 niet gevonden. Controleer of dit op de Pi 5 draait."
fi

echo "[cockpit] Containers bouwen en starten"
cd "$RPI_DIR"
sudo docker compose -f docker-compose.pi5.yml up -d --build

echo "[cockpit] Status"
sudo docker compose -f docker-compose.pi5.yml ps

echo
echo "[cockpit] Klaar. Na opnieuw inloggen kun je docker zonder sudo gebruiken."
echo "[cockpit] Logs bekijken:"
echo "  cd '$RPI_DIR'"
echo "  docker compose -f docker-compose.pi5.yml logs -f"
