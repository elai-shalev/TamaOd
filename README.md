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

3. **Run the application:**
   ```bash
   pdm run manage.py runserver
   ```

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
