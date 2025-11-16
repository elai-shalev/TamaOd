# TamaOd Deployment Guide

This guide covers building, deploying, and running the TamaOd Django application in a containerized environment.

> **Note:** For general project information, local development setup, and testing, see [README.md](README.md). This document focuses exclusively on deployment and containerization.

## Overview

The application is containerized using Docker with:

- **nginx** for serving static files and reverse proxy (port 8080)
- **gunicorn** for running the Django application (port 8000)
- **supervisor** for process management
- Single container deployment for simplicity

### Architecture

```
Internet → Host:8080 → Container:8080 (nginx) → Container:8000 (gunicorn/Django)
```

- External traffic hits nginx on port 8080
- nginx serves static files directly
- nginx proxies dynamic requests to gunicorn on port 8000

## Prerequisites

- Podman installed on your system
- Docker Hub or Quay.io account for pushing images
- Git for version control

## Local Development

### Quick Start

1. **Clone the repository**:

   ```bash
   git clone https://github.com/elai-shalev/TamaOd
   cd TamaOd
   ```

2. **Build and run locally**:

   `pdm run python manage.py runserver`

3. **Access the application**:
   - Main application: http://localhost:8080
   - Health check: http://localhost:8080/health/

### Manual Docker Build

1. **Stop and remove existing container (if any)**:

   ```bash
   # Stop the container if it's running
   podman stop tamaod-app 2>/dev/null || true

   # Remove the container
   podman rm tamaod-app 2>/dev/null || true
   ```

2. **Create and configure environment file**:

   ```bash
   # Copy the template
   cp env.prod.template .env.prod

   # Edit .env.prod with your values
   # At minimum, you must set:
   # - SECRET_KEY (generate one with the command below)
   # - ALLOWED_HOSTS (your domain or localhost,127.0.0.1)
   # - USER_AGENT: Your application identifier
   # - REFERRER: Your site URL

   # Generate a secret key:
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

3. **Build the image**:

   ```bash
   podman build -f deploy/Dockerfile -t tamaod:latest .
   ```

4. **Run the container with environment file**:

   ```bash
   podman run -it -p 0.0.0.0:8080:8080 \
     --env-file .env.prod \
     --name tamaod-app \
     localhost/tamaod:latest
   ```

   **Note:**

   - The `--env-file .env.prod` flag loads all environment variables from the file
   - `SECRET_KEY` is required in the environment file
   - The container uses **REAL APIs by default** (Nominatim for geocoding, GISN for construction data)
   - Make sure `.env.prod` is in your `.gitignore` (it contains secrets)

## Production Deployment

### Building for Production

1. **Create production environment file**:

   ```bash
   # Copy the template
   cp env.prod.template .env.prod

   # Edit .env.prod with your production values:
   # - SECRET_KEY: Generate a strong secret key
   # - DEBUG: Set to False
   # - ALLOWED_HOSTS: Your production domain(s)
   # - USER_AGENT: Your application identifier
   # - REFERRER: Your site URL

   # Generate a secret key:
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

2. **Build production image**:

   ```bash
   podman build -f deploy/Dockerfile -t tamaod:production .
   ```

   Or use the build script:

   ```bash
   ./deploy/build-and-push.sh quay.io/your-username v1.0.0
   ```

### Pushing to Container Registry

#### Quay.io

1. **Tag the image**:

   ```bash
   docker tag tamaod:production quay.io/your-username/tamaod:latest
   docker tag tamaod:production quay.io/your-username/tamaod:v1.0.0
   ```

2. **Push to Quay.io**:
   ```bash
   docker login quay.io
   docker push quay.io/your-username/tamaod:latest
   docker push quay.io/your-username/tamaod:v1.0.0
   ```

#### Docker Hub

1. **Tag the image**:

   ```bash
   docker tag tamaod:production your-username/tamaod:latest
   docker tag tamaod:production your-username/tamaod:v1.0.0
   ```

2. **Push to Docker Hub**:
   ```bash
   docker login
   docker push your-username/tamaod:latest
   docker push your-username/tamaod:v1.0.0
   ```

### Running in Production

#### Basic Production Run

```bash
# Stop and remove existing container (if any)
podman stop tamaod-app 2>/dev/null || true
podman rm tamaod-app 2>/dev/null || true

# Ensure you have .env.prod configured (see "Building for Production" above)
# The environment file must contain at minimum:
# - SECRET_KEY (required)
# - ALLOWED_HOSTS (your domain)
# - DEBUG=False

podman run -d \
  --name tamaod-app \
  -p 0.0.0.0:8080:8080 \
  --env-file .env.prod \
  --restart unless-stopped \
  quay.io/your-username/tamaod:latest
```

**Important:**

- The `SECRET_KEY` in `.env.prod` is required. The container will not start without it.
- The container uses **REAL APIs by default** (Nominatim and GISN). Mock APIs are only used if explicitly enabled with `USE_MOCK_NOMINATIVE=True` and `USE_MOCK_GISN=True` in your `.env.prod` file.
- Never commit `.env.prod` to version control - it contains secrets.

## Environment Variables

| Variable              | Default                       | Description                                     |
| --------------------- | ----------------------------- | ----------------------------------------------- |
| `SECRET_KEY`          | _required_                    | Django secret key                               |
| `DEBUG`               | `False`                       | Enable Django debug mode                        |
| `DJANGO_ENV`          | `production`                  | Environment setting                             |
| `ALLOWED_HOSTS`       | `localhost,127.0.0.1,0.0.0.0` | Comma-separated allowed hosts                   |
| `USE_MOCK_NOMINATIVE` | `False`                       | Use mock nominative service (default: REAL API) |
| `USE_MOCK_GISN`       | `False`                       | Use mock GISN service (default: REAL API)       |

## Container Structure

- **Port**: 8080 (nginx frontend)
- **Health Check**: `/health/` endpoint
- **Static Files**: Served by nginx at `/static/`
- **Media Files**: Served by nginx at `/media/`
- **Application**: Django app behind nginx proxy (gunicorn on port 8000)

## Monitoring and Logs

### View Logs

```bash
# All logs
docker logs tamaod-app

# Follow logs
docker logs -f tamaod-app

# Supervisor logs (inside container)
docker exec tamaod-app tail -f /var/log/supervisor/supervisord.log
```

### Health Check

```bash
curl http://localhost:8080/health/
```

## Troubleshooting

### Common Issues

1. **Port already in use**:

   ```bash
   # Use different port
   podman run -p 0.0.0.0:8081:8080 tamaod:latest
   ```

2. **Permission issues**:

   ```bash
   # Check container logs
   docker logs tamaod-app
   ```

3. **Static files not loading**:
   - Ensure nginx configuration is correct
   - Check `/static/` path in container

### Debug Container

```bash
# Enter running container
docker exec -it tamaod-app /bin/bash

# Check processes
docker exec tamaod-app supervisorctl status

# Check nginx
docker exec tamaod-app nginx -t
```

## Security Considerations

- Always use strong `SECRET_KEY` in production
- Set `DEBUG=False` in production
- Configure proper `ALLOWED_HOSTS`
- Use HTTPS in production (configure reverse proxy)
- Regularly update base images and dependencies
- Consider using secrets management for sensitive environment variables
