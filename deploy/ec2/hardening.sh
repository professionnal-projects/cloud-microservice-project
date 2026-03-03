#!/usr/bin/env bash

set -euo pipefail

DOMAIN="${DOMAIN:-}"
EMAIL="${EMAIL:-}"
SSH_PORT="${SSH_PORT:-22}"

if [[ -z "${DOMAIN}" ]]; then
  echo "ERROR: DOMAIN is required."
  echo "Example: export DOMAIN=api.yourdomain.com"
  exit 1
fi

if [[ -z "${EMAIL}" ]]; then
  echo "ERROR: EMAIL is required for Let's Encrypt registration."
  echo "Example: export EMAIL=you@example.com"
  exit 1
fi

echo "[1/7] Installing security packages..."
sudo apt-get update -y
sudo apt-get install -y ufw fail2ban certbot

echo "[2/7] Configuring UFW defaults..."
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow "${SSH_PORT}/tcp"
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

echo "[3/7] Enabling fail2ban..."
sudo systemctl enable fail2ban
sudo systemctl restart fail2ban

echo "[4/7] Creating minimal fail2ban jail.local..."
sudo tee /etc/fail2ban/jail.local >/dev/null <<EOF
[sshd]
enabled = true
port = ${SSH_PORT}
maxretry = 5
bantime = 1h
findtime = 10m
EOF

sudo systemctl restart fail2ban

echo "[5/7] Requesting TLS certificate from Let's Encrypt (standalone)..."
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

if [[ -f "${ROOT_DIR}/docker-compose.yml" ]]; then
  docker compose -f "${ROOT_DIR}/docker-compose.yml" down || true
fi
if [[ -f "${ROOT_DIR}/docker-compose.prod.yml" ]]; then
  docker compose -f "${ROOT_DIR}/docker-compose.prod.yml" down || true
fi

sudo certbot certonly --standalone \
  --agree-tos \
  --non-interactive \
  --email "${EMAIL}" \
  -d "${DOMAIN}"

echo "[6/7] Installing renewal cron job..."
CRON_LINE="0 3 * * * certbot renew --quiet"
(sudo crontab -l 2>/dev/null | grep -v 'certbot renew' || true; echo "${CRON_LINE}") | sudo crontab -

echo "[7/7] Final status"
sudo ufw status verbose
sudo fail2ban-client status sshd || true

echo
echo "Hardening completed."
echo "Next: run deploy script with TLS-enabled Nginx config (see README)."
