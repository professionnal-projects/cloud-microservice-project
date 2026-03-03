# Cloud Microservice Project (Flask + Docker + Nginx + CI/CD)

Production-ready Flask microservice designed for a DevOps portfolio.

## Project Structure

```text
.
├── app/
│   ├── app.py
│   ├── requirements.txt
│   └── tests/
│       └── test_app.py
├── .github/
│   └── workflows/
│       └── ci-cd.yml
├── nginx/
│   └── nginx.conf
├── Dockerfile
├── docker-compose.yml
├── docker-compose.prod.yml
├── .env.example
├── .gitignore
└── README.md
```

## Features

- Flask API routes: `/`, `/health`, `/info`, `/metrics`, `/echo` (POST)
- Beautiful HTML dashboard on `/` with:
  - Architecture diagram
  - Route live status checks
  - Live service metrics
  - Request counter
- Multi-stage Docker build (builder + production)
- Nginx reverse proxy (`:80` to Flask `:5000`)
- Docker health checks
- Pytest unit tests for all routes
- GitHub Actions CI/CD: test, build, push to Docker Hub
- Environment-based configuration (no sensitive hardcoded values)

## Architecture (ASCII)

```text
			 +---------------------------+
			 |   Browser / API Client    |
			 +-------------+-------------+
								|
								v
			 +---------------------------+
			 |     Nginx Reverse Proxy   |  :80
			 +-------------+-------------+
								|
								v
			 +---------------------------+
			 |   Flask API (Gunicorn)    |  :5000
			 +-------------+-------------+
								|
								v
			 +---------------------------+
			 | Health + Metrics Endpoints|
			 +---------------------------+
```

## API Routes

| Route | Method | Description |
|---|---|---|
| `/` | GET | HTML dashboard |
| `/health` | GET | Liveness/health status |
| `/info` | GET | Service metadata |
| `/metrics` | GET | Runtime metrics and counters |
| `/echo` | POST | Echoes JSON payload |

## Quick Start (Local)

1. Copy env template:

	```bash
	cp .env.example .env
	```

2. Build and run:

	```bash
	docker compose up --build -d
	```

3. Open:

	- Dashboard: `http://localhost`
	- Health: `http://localhost/health`

## Run Tests

```bash
python -m pip install -r app/requirements.txt
pytest app/tests -q
```

## Production Compose (EC2)

1. Set your published image in `.env`:

	```env
	DOCKER_IMAGE=yourdockerhubusername/cloud-microservice-project:latest
	```

2. Run production stack:

	```bash
	docker compose -f docker-compose.prod.yml up -d
	```

## CI/CD Pipeline (GitHub Actions)

Workflow: `.github/workflows/ci-cd.yml`

- On pull request to `main`:
  - Install dependencies
  - Run unit tests
  - Validate Docker production build
- On push to `main`:
  - Run test job
  - Build and push image to Docker Hub

Required GitHub Secrets:

- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN`

## DevOps Concepts Demonstrated

### 1) Reverse Proxy Pattern

Nginx sits in front of Flask and handles incoming traffic on port 80, forwarding requests to the internal Flask container on port 5000.

### 2) Health Checks

- Flask provides `/health`
- Docker health checks use this endpoint for container status

### 3) SPOF Awareness

Single EC2 host and single Nginx container are still potential single points of failure. This is suitable for portfolio demonstration but should be evolved for high availability (multi-AZ, load balancer, autoscaling).

### 4) Horizontal Scalability

Scale the Flask app replicas with Docker Compose:

```bash
docker compose up -d --scale app=3
```

Nginx routes traffic to the `app` service across replicas.

### 5) Environment-based Configuration

Service name, environment, ports, runtime settings, and image name are all configurable through environment variables.

## AWS EC2 Deployment Notes

- Provision an EC2 instance with Docker and Docker Compose plugin
- Open inbound ports `22` (SSH) and `80` (HTTP)
- Pull your image from Docker Hub
- Start stack using `docker-compose.prod.yml`

## AWS EC2 Deployment Playbook

### Why AWS account was not required yet

Until infrastructure is actually created, this project can be fully developed, tested, containerized, and published from local/CI environments.

Your AWS account is required only when you:

- Create EC2 instances and networking (VPC/Security Group)
- Attach an Elastic IP or domain DNS records
- Operate production infrastructure

### 1) Create AWS Infrastructure

- Launch an Ubuntu 24.04 EC2 instance
- Attach a Security Group with inbound rules:
	- `22/tcp` from your IP only
	- `80/tcp` from `0.0.0.0/0`
- Attach an IAM role only if you plan to pull secrets from AWS services

### 2) Configure GitHub Secrets (for CI push)

In your GitHub repository settings, add:

- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN`

Then push to `main`: the CI workflow will build and push your image.

### 3) Bootstrap EC2 Host

SSH into your server and run:

```bash
git clone https://github.com/professionnal-projects/cloud-microservice-project.git
cd cloud-microservice-project
chmod +x deploy/ec2/bootstrap.sh deploy/ec2/deploy.sh
./deploy/ec2/bootstrap.sh
```

Reconnect your SSH session to apply Docker group membership.

### 4) Deploy Application on EC2

```bash
cd cloud-microservice-project
export DOCKER_IMAGE=yourdockerhubusername/cloud-microservice-project:latest
./deploy/ec2/deploy.sh
```

### 5) Verify Deployment

```bash
curl http://localhost/health
curl http://localhost/info
curl http://localhost/metrics
```

From your machine:

```bash
curl http://<EC2_PUBLIC_IP>/health
```

### 6) Zero-Downtime Refresh Pattern (single-host approximation)

For portfolio demonstration, re-run deployment after each new image:

```bash
export DOCKER_IMAGE=yourdockerhubusername/cloud-microservice-project:latest
./deploy/ec2/deploy.sh
```

For stronger availability, move to multi-instance architecture with ALB + Auto Scaling Group.

## Production Security Hardening (Recommended)

The repository includes automation scripts in `deploy/ec2`:

- `bootstrap.sh`: installs Docker + Compose
- `deploy.sh`: deploys production stack from Docker image
- `hardening.sh`: configures UFW, fail2ban, and Let's Encrypt (standalone mode)
- `enable_tls_nginx.sh`: generates TLS-enabled `nginx.conf`

### Harden an EC2 instance

```bash
cd cloud-microservice-project
chmod +x deploy/ec2/*.sh

export DOMAIN=api.yourdomain.com
export EMAIL=you@example.com
export SSH_PORT=22

./deploy/ec2/hardening.sh
./deploy/ec2/enable_tls_nginx.sh
```

Then redeploy:

```bash
export DOCKER_IMAGE=yourdockerhubusername/cloud-microservice-project:latest
./deploy/ec2/deploy.sh
```

Verify HTTPS:

```bash
curl -I https://api.yourdomain.com/health
```

## License

This project is provided for portfolio and learning use.
