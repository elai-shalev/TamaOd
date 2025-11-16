# TamaOd

Analyze addresses for possible construction

## Quick Start

1. **Set up environment file:**

   ```bash
   cp .env.template .env.prod
   # Edit .env.prod with your values (especially SECRET_KEY)
   ```

2. **Generate a secret key:**

   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

3. **Run the application locally:**

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
- **`.env.template`** - Template file (safe to commit, no secrets)

The app loads files in priority order: `.env.prod` → `.env.test` → `.env`

## Testing

To run tests:

```bash
pytest
```

Tests automatically use `.env.test` if it exists.

## Mock Services

Configure mock services in your environment file:

- `USE_MOCK_NOMINATIVE=True/False` - Use mock nominative service
- `USE_MOCK_GISN=True/False` - Use mock GISN service

See [ENV.md](ENV.md) for all configuration options.
