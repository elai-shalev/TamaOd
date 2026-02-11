# TamaOd

A Django web application that queries Tel Aviv Municipality data to display approved and planned construction projects near any address.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Browser                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      nginx (SSL termination)                    │
│                         ports 80/443                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    gunicorn (WSGI server)                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Django Application                         │
│  ┌───────────────┐              ┌───────────────┐               │
│  │    ui app     │              │   api app     │               │
│  │  (frontend)   │───────────▶  │  (backend)    │               │
│  └───────────────┘              └───────────────┘               │
│                                        │                        │
│                          ┌─────────────┴─────────────┐          │
│                          ▼                           ▼          │
│                 ┌─────────────────┐       ┌─────────────────┐   │
│                 │   Nominatim    │       │   GISN API      │   │
│                 │  (geocoding)   │       │ (construction)  │   │
│                 └─────────────────┘       └─────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

## Project Structure

```
TamaOd/
├── api/                    # Backend API application
│   ├── services/           # External service integrations
│   │   ├── base.py         # Abstract base classes (Strategy pattern)
│   │   ├── real.py         # Production API clients
│   │   ├── mock.py         # Mock services for testing
│   │   └── services.py     # Service factory
│   ├── views.py            # API endpoints
│   └── data/
│       └── streets.json    # Tel Aviv street names
│
├── ui/                     # Frontend application
│   ├── templates/          # HTML templates
│   ├── static/             # CSS, JS, images
│   └── views.py            # Page rendering
│
├── tamaod/                 # Django project settings
│   ├── settings.py         # Configuration
│   ├── urls.py             # URL routing
│   └── wsgi.py             # WSGI entry point
│
├── deploy/                 # Container deployment
│   ├── Dockerfile          # Multi-service container
│   ├── nginx.conf          # HTTP configuration
│   ├── nginx-ssl.conf      # HTTPS configuration
│   ├── supervisord.conf    # Process manager
│   └── docker-entrypoint.sh
│
├── tests/                  # Test suite
└── scripts/                # Utility scripts
```

## Tech Stack

| Component        | Technology                 |
| ---------------- | -------------------------- |
| Backend          | Django 5.x, Python 3.13    |
| HTTP Client      | httpx (async-capable)      |
| WSGI Server      | gunicorn                   |
| Reverse Proxy    | nginx                      |
| Process Manager  | supervisord                |
| Containerization | Docker/Podman              |
| SSL/TLS          | TLS 1.2/1.3                |
| Testing          | pytest, pytest-django      |
| Linting          | ruff                       |

## External APIs

| Service   | Purpose                            | Documentation                                                             |
| --------- | ---------------------------------- | ------------------------------------------------------------------------- |
| Nominatim | Geocoding addresses to coordinates | [nominatim.org](https://nominatim.org/release-docs/latest/api/Overview/)  |
| GISN      | Tel Aviv construction permits      | [gisn.tel-aviv.gov.il](https://gisn.tel-aviv.gov.il/iView2js4/index.aspx) |

## Local Development

```bash
# Install dependencies
pdm install

# Run with HTTPS (default, uses self-signed cert)
pdm run runserver
# Access: https://localhost:8000/

# Run with HTTP (simpler, no cert warnings)
pdm run runserver-http
# Access: http://localhost:8000/
```

The HTTPS mode auto-generates a self-signed certificate on first run. Your browser will show a security warning - this is normal for local development.

## Production Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for Docker/Podman deployment with SSL/TLS support.

## Testing

```bash
pdm run pytest
```
