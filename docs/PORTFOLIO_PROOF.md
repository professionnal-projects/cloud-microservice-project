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

## Resume / LinkedIn Bullet Points

- Built and deployed a production-style Flask microservice on AWS EC2 behind Nginx, with Docker Compose orchestration and HTTPS via Let's Encrypt.
- Implemented CI/CD on GitHub Actions to run unit tests, validate Docker builds, and optionally push container images to Docker Hub.
- Added health checks, runtime metrics, and an operational dashboard to improve service observability and reliability validation.
- Hardened deployment with firewall policies (UFW), intrusion prevention (fail2ban), and TLS termination using domain-based certificates.

## Interview Talking Points

- Explain why AWS default hostnames cannot be used for Let's Encrypt issuance and why a real domain is required.
- Explain the difference between local-build deployment and remote-image deployment modes.
- Discuss SPOF risk on a single EC2 instance and how to evolve toward ALB + Auto Scaling + multi-AZ.
- Describe horizontal scaling behavior (`docker compose --scale`) and reverse proxy routing implications.
