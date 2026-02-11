# TamaOd Deployment Guide

This guide explains how to self-host your own instance of the TamaOd application using Docker/Podman containers with SSL support.

## Quick Start

### Development Mode (HTTP)

```bash
# Create environment file for development
cat > .env << 'EOF'
SECRET_KEY=dev-secret-key-not-for-production
DEBUG=True
DJANGO_ENV=development
ALLOWED_HOSTS=localhost,127.0.0.1
SSL_ENABLED=false
EOF

# Build and run
podman build -f deploy/Dockerfile -t tamaod:dev .
podman run -it --rm -p 8080:8080 --env-file .env tamaod:dev

# Access: http://localhost:8080/
```

### Production Mode (HTTPS)

```bash
# 1. Create production environment file
cp .env.example .env
# Edit .env with real values (especially SECRET_KEY and ALLOWED_HOSTS)

# 2. Build and run with SSL
podman build -f deploy/Dockerfile -t tamaod:prod .
podman run -d \
  --name tamaod-app \
  -p 80:8080 \
  -p 443:8443 \
  --env-file .env \
  -v /etc/letsencrypt/live/yourdomain.com/fullchain.pem:/etc/ssl/certs/app.crt:ro,z \
  -v /etc/letsencrypt/live/yourdomain.com/privkey.pem:/etc/ssl/private/app.key:ro,z \
  --restart unless-stopped \
  tamaod:prod

# Access: https://yourdomain.com/
```

---

## Architecture

```
Internet → nginx (SSL termination) → gunicorn → Django
              ↓
    Certs mounted at runtime:
    /etc/ssl/certs/app.crt
    /etc/ssl/private/app.key
```

- **nginx**: Reverse proxy, static files, SSL termination (ports 8080/8443)
- **gunicorn**: WSGI server for Django (port 8000 internal)
- **supervisor**: Process manager

---

## SSL Configuration

### SSL Modes

| `SSL_ENABLED`    | Behavior                               |
| ---------------- | -------------------------------------- |
| `auto` (default) | HTTPS if certs mounted, otherwise HTTP |
| `true`           | Require HTTPS (fails without certs)    |
| `false`          | HTTP only                              |

### Certificate Mount Points

| File        | Container Path             |
| ----------- | -------------------------- |
| Certificate | `/etc/ssl/certs/app.crt`   |
| Private Key | `/etc/ssl/private/app.key` |

### Certificate Options

Mount any SSL certificate using the standard paths. The container accepts certificates from any source: commercial certificate authorities, Let's Encrypt, corporate CAs, or self-signed.

**Generic mounting pattern:**

```bash
podman run -d \
  -p 80:8080 -p 443:8443 \
  --env-file .env \
  -v /path/to/cert.crt:/etc/ssl/certs/app.crt:ro,z \
  -v /path/to/key.pem:/etc/ssl/private/app.key:ro,z \
  tamaod:prod
```

**Example: Let's Encrypt**

```bash
# Get certificate
sudo certbot certonly --standalone -d yourdomain.com -m your@email.com

# Run container
podman run -d \
  -p 80:8080 -p 443:8443 \
  --env-file .env \
  -v /etc/letsencrypt/live/yourdomain.com/fullchain.pem:/etc/ssl/certs/app.crt:ro,z \
  -v /etc/letsencrypt/live/yourdomain.com/privkey.pem:/etc/ssl/private/app.key:ro,z \
  tamaod:prod

# Auto-renewal (add to crontab)
0 3 * * * certbot renew --quiet --deploy-hook 'podman restart tamaod-app'
```

**Example: Custom CA Certificate**

```bash
podman run -d \
  -p 80:8080 -p 443:8443 \
  --env-file .env \
  -v /path/to/cert.crt:/etc/ssl/certs/app.crt:ro,z \
  -v /path/to/key.pem:/etc/ssl/private/app.key:ro,z \
  tamaod:prod
```

**Example: Self-Signed (Testing Only)**

```bash
# Generate self-signed cert
./scripts/generate_ssl_cert.sh
chmod 644 .ssl/localhost.key  # Make readable

# Run container
podman run -it --rm \
  -p 8080:8080 -p 8443:8443 \
  --env-file .env \
  -v $(pwd)/.ssl/localhost.crt:/etc/ssl/certs/app.crt:ro,z \
  -v $(pwd)/.ssl/localhost.key:/etc/ssl/private/app.key:ro,z \
  tamaod:prod

# Access: https://localhost:8443/ (accept browser warning)
```

---

## Environment Variables

| Variable        | Default               | Description                          |
| --------------- | --------------------- | ------------------------------------ |
| `SECRET_KEY`    | _required_            | Django secret key                    |
| `DEBUG`         | `False`               | Debug mode                           |
| `DJANGO_ENV`    | `production`          | Environment: production, development |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | Allowed hostnames                    |
| `SSL_ENABLED`   | `auto`                | SSL mode                             |

Generate a secret key:

```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## Container Management

```bash
# View logs
podman logs -f tamaod-app

# Stop/start
podman stop tamaod-app
podman start tamaod-app

# Remove
podman stop tamaod-app && podman rm tamaod-app

# Enter container
podman exec -it tamaod-app /bin/bash

# Check processes
podman exec tamaod-app supervisorctl status

# Test nginx config
podman exec tamaod-app nginx -t
```

---

## Health Check

```bash
curl http://localhost:8080/health/
curl -k https://localhost:8443/health/
```

---

## Troubleshooting

### Port already in use

```bash
podman run -p 8081:8080 ...  # Use different port
```

### SSL certificate errors

```bash
# Check certs are mounted
podman exec tamaod-app ls -la /etc/ssl/certs/app.crt
podman exec tamaod-app ls -la /etc/ssl/private/app.key

# Check cert validity
podman exec tamaod-app openssl x509 -in /etc/ssl/certs/app.crt -noout -dates
```

### SELinux issues (Fedora/RHEL)

```bash
# Add :z to volume mounts
-v /path/to/cert:/etc/ssl/certs/app.crt:ro,z
```

### nginx won't start

```bash
# Debug mode
podman run -it --rm --entrypoint /bin/bash ... tamaod:prod
nginx -t  # Check config
cat /var/log/nginx/error.log
```

---

## Pushing to Registry

```bash
# Tag
podman tag tamaod:prod quay.io/username/tamaod:v1.0.0
podman tag tamaod:prod quay.io/username/tamaod:latest

# Push
podman login quay.io
podman push quay.io/username/tamaod:v1.0.0
podman push quay.io/username/tamaod:latest
```

---

## Security

### Container Security

- ✅ No hardcoded secrets - all sensitive data via environment variables
- ✅ No dev files or git history in image
- ✅ SSL certificates mounted at runtime, never baked in
- ✅ Runs as non-root user (`app`)
- ✅ Production-only dependencies

### SSL/TLS Features

| Feature      | Configuration            |
| ------------ | ------------------------ |
| TLS Versions | 1.2 and 1.3 only         |
| HSTS         | Enabled (2 year max-age) |
| Ciphers      | Modern ECDHE-based       |

### Security Headers (nginx)

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security` (HTTPS only)

### Production Checklist

- [ ] Generate unique `SECRET_KEY`
- [ ] Set `DEBUG=False`
- [ ] Configure `ALLOWED_HOSTS` with your domain(s)
- [ ] Enable HTTPS with trusted certificates
- [ ] Set up certificate auto-renewal
- [ ] Never commit `.env` (contains secrets)

### Reporting Vulnerabilities

Do NOT create public issues for security vulnerabilities. Contact the maintainer privately.
