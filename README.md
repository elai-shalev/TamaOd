# TamaOd

Analyze addresses for possible construction near by.

## About

TamaOd is a Django application that analyzes addresses for possible new construction. The application integrates with external services for geocoding and construction data retrieval.

## Features

- Address analysis for construction opportunities
- Integration with Nominatim for geocoding addresses.
- Integration with [Tel Aviv Municipality GISN](https://gisn.tel-aviv.gov.il/iView2js4/index.aspx) for construction data about construction.
- Mock service support for testing
- Environment-based configuration

## Requirements

- Python 3.x
- PDM (Python Dependency Manager)
- See `pyproject.toml` for full dependency list

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/elai-shalev/TamaOd
   cd TamaOd
   ```

2. **Install dependencies:**

   ```bash
   pdm install
   ```

3. **Set up environment file:**

   ```bash
   cp .env.template .env.prod
   # Edit .env.prod with your values (especially SECRET_KEY)
   ```

4. **Generate a secret key:**

   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

## Local Development

### Running the Application

**Default (HTTPS - Recommended):**

```bash
pdm run runserver
# or
./scripts/runserver_local.sh
```

The server will automatically generate SSL certificates on first run if needed.
Access at: **`https://localhost:8000/`** or **`https://127.0.0.1:8000/`**

Note: Your browser will show a security warning for the self-signed certificate. This is normal for local development. Click "Advanced" and "Proceed" to continue.

**HTTP mode (if needed):**

```bash
pdm run runserver-http
# or
USE_HTTP=1 ./scripts/runserver_local.sh
```

Access at: **`http://localhost:8000/`** or **`http://127.0.0.1:8000/`**

Note: Use HTTPS (default) if your browser forces HTTPS connections.

The application automatically loads `.env.prod` (production settings, also used locally).

## Environment Configuration

This project uses environment files for configuration. See [ENV.md](ENV.md) for detailed documentation.

**Quick reference:**

- **`.env.prod`** - Production settings (highest priority, used locally)
- **`.env.test`** - Test environment settings
- **`.env`** - Fallback development settings
- **`.env.template.prod`** - Template file (safe to commit, no secrets)

The app loads files in priority order: `.env.prod` → `.env.test` → `.env`

## Testing

To run tests:

```bash
pdm run pytest
```

Tests automatically use `.env.test` if it exists.

## Mock Services

Configure mock services in your environment file:

- `USE_MOCK_NOMINATIVE=True/False` - Use mock nominative service
- `USE_MOCK_GISN=True/False` - Use mock GISN service

See [ENV.md](ENV.md) for all configuration options.

## Deployment

For deployment instructions, including Docker/Podman containerization and production setup, see [DEPLOYMENT.md](DEPLOYMENT.md).
