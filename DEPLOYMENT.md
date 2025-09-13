# TamaOd Deployment Guide

This guide covers building, deploying, and running the TamaOd Django application in a containerized environment.

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
   git clone <repository-url>
   cd TamaOd
   ```

2. **Build and run locally**:

   `pdm run python manage.py runserver`

3. **Access the application**:
   - Main application: http://localhost:8080
   - Health check: http://localhost:8080/health/

### Manual Docker Build

1. **Build the image**:

   ```bash
   podman build -t tamaod:latest .
   ```

2. **Run the container**:
   ```bash
   podman run -it -p 0.0.0.0:8080:8080 \
     -e SECRET_KEY="your-secret-key-here" \
     -e DEBUG=False \
     -e ALLOWED_HOSTS="localhost,127.0.0.1,0.0.0.0" \
     quay.io/<username>/tamaod:latest
   ```

## Production Deployment

### Building for Production

1. **Set production environment variables**:

   ```bash
   # Copy template and edit
   cp env.prod.template .env.prod
   # Edit .env.prod with your production values
   ```

2. **Build production image**:
   ```bash
   podman build -t tamaod:production .
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
podman run -d \
  --name tamaod-app \
  -p 0.0.0.0:8080:8080 \
  -e SECRET_KEY="your-very-secure-secret-key" \
  -e DEBUG=False \
  -e ALLOWED_HOSTS="yourdomain.com,www.yourdomain.com" \
  -e USE_MOCK_NOMINATIVE=False \
  -e USE_MOCK_GISN=False \
  --restart unless-stopped \
  quay.io/your-username/tamaod:latest
```

## Environment Variables

| Variable              | Default                       | Description                   |
| --------------------- | ----------------------------- | ----------------------------- |
| `SECRET_KEY`          | _required_                    | Django secret key             |
| `DEBUG`               | `False`                       | Enable Django debug mode      |
| `DJANGO_ENV`          | `production`                  | Environment setting           |
| `ALLOWED_HOSTS`       | `localhost,127.0.0.1,0.0.0.0` | Comma-separated allowed hosts |
| `USE_MOCK_NOMINATIVE` | `True`                        | Use mock nominative service   |
| `USE_MOCK_GISN`       | `True`                        | Use mock GISN service         |

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
