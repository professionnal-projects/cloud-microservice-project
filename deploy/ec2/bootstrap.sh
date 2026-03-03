#!/usr/bin/env bash

set -euo pipefail

echo "[1/6] Updating apt cache..."
sudo apt-get update -y

echo "[2/6] Installing system dependencies..."
sudo apt-get install -y \
  ca-certificates \
  curl \
  git \
  gnupg \
  lsb-release

echo "[3/6] Installing Docker Engine and Compose plugin..."
sudo apt-get install -y docker.io docker-compose-v2

echo "[4/6] Enabling Docker service..."
sudo systemctl enable docker
sudo systemctl start docker

echo "[5/6] Adding current user to docker group..."
sudo usermod -aG docker "$USER"

echo "[6/6] Verifying installation..."
docker --version || true
docker compose version || true

echo
echo "Bootstrap completed."
echo "Open a new shell session (or reconnect SSH) so docker group membership is applied."
