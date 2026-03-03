#!/usr/bin/env bash

set -euo pipefail

REPO_URL="${REPO_URL:-https://github.com/professionnal-projects/cloud-microservice-project.git}"
BRANCH="${BRANCH:-main}"
APP_DIR="${APP_DIR:-/opt/cloud-microservice-project}"
ENV_FILE_SOURCE="${ENV_FILE_SOURCE:-}"

if [[ -z "${DOCKER_IMAGE:-}" ]]; then
  echo "ERROR: DOCKER_IMAGE is required."
  echo "Example: export DOCKER_IMAGE=yourdockerhubusername/cloud-microservice-project:latest"
  exit 1
fi

echo "[1/6] Preparing application directory: ${APP_DIR}"
sudo mkdir -p "${APP_DIR}"
sudo chown -R "$USER":"$USER" "${APP_DIR}"

if [[ -d "${APP_DIR}/.git" ]]; then
  echo "[2/6] Updating existing repository..."
  git -C "${APP_DIR}" fetch origin
  git -C "${APP_DIR}" checkout "${BRANCH}"
  git -C "${APP_DIR}" reset --hard "origin/${BRANCH}"
else
  echo "[2/6] Cloning repository..."
  git clone --branch "${BRANCH}" "${REPO_URL}" "${APP_DIR}"
fi

cd "${APP_DIR}"

echo "[3/6] Preparing .env file..."
if [[ -n "${ENV_FILE_SOURCE}" ]]; then
  cp "${ENV_FILE_SOURCE}" .env
elif [[ ! -f .env ]]; then
  cp .env.example .env
fi

if ! grep -q '^DOCKER_IMAGE=' .env; then
  echo "DOCKER_IMAGE=${DOCKER_IMAGE}" >> .env
else
  sed -i "s|^DOCKER_IMAGE=.*|DOCKER_IMAGE=${DOCKER_IMAGE}|" .env
fi

echo "[4/6] Pulling images..."
docker compose -f docker-compose.prod.yml pull

echo "[5/6] Starting production stack..."
docker compose -f docker-compose.prod.yml up -d

echo "[6/6] Performing health check..."
sleep 5
curl -fsS http://localhost/health
echo

echo "Deployment completed successfully."
echo "Dashboard: http://$(curl -s ifconfig.me 2>/dev/null || echo '<EC2_PUBLIC_IP>')/"
