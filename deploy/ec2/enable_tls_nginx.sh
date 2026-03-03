#!/usr/bin/env bash

set -euo pipefail

DOMAIN="${DOMAIN:-}"

if [[ -z "${DOMAIN}" ]]; then
  echo "ERROR: DOMAIN is required."
  echo "Example: export DOMAIN=api.yourdomain.com"
  exit 1
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TEMPLATE="${ROOT_DIR}/nginx/nginx.ssl.conf"
TARGET="${ROOT_DIR}/nginx/nginx.conf"

if [[ ! -f "${TEMPLATE}" ]]; then
  echo "ERROR: TLS template not found at ${TEMPLATE}"
  exit 1
fi

sed "s|\${DOMAIN_NAME}|${DOMAIN}|g" "${TEMPLATE}" > "${TARGET}"

echo "Generated ${TARGET} for domain ${DOMAIN}."
echo "Next: docker compose -f docker-compose.prod.yml up -d"
