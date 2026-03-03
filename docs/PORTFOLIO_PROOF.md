# Portfolio Proof Pack

This file provides clear, recruiter-friendly evidence that the project is production-like and deployed.

## Live Service

- Primary endpoint: `https://api.nathanaelfetue.tech/health`
- Dashboard endpoint: `https://api.nathanaelfetue.tech/`

## Validation Commands (Public)

Run these from your local machine:

```bash
curl -I https://api.nathanaelfetue.tech/health
curl https://api.nathanaelfetue.tech/health
curl https://api.nathanaelfetue.tech/info
curl https://api.nathanaelfetue.tech/metrics
curl -X POST https://api.nathanaelfetue.tech/echo \
  -H "Content-Type: application/json" \
  -d '{"message":"portfolio-check"}'
```

Expected:

- `HTTP/2 200`
- JSON payload with `"status":"ok"` on `/health`
- Security headers from Nginx

## Validation Commands (Server-side)

Run these on EC2:

```bash
docker compose ps
docker compose logs --tail=80 nginx app
curl -vk https://127.0.0.1/health
```

## What This Project Demonstrates

- Flask microservice design with health/info/metrics/echo endpoints
- Nginx reverse proxy architecture
- Docker multi-stage build and container health checks
- Environment-driven configuration for deployment portability
- CI/CD pipeline with test/build/push stages (GitHub Actions)
- Production hardening baseline (UFW, fail2ban, TLS)

## Resume / LinkedIn (Clean Version)

- Deployed a Flask API on AWS EC2 behind Nginx with HTTPS (Let's Encrypt).
- Containerized the service with Docker multi-stage builds and Docker Compose.
- Added CI/CD with GitHub Actions (tests + Docker build validation + optional image push).
- Implemented operational endpoints (`/health`, `/metrics`) and production baseline hardening.
