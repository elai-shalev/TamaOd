# Environment Configuration Guide

This project uses environment files (`.env.*`) to configure settings. The application automatically loads the appropriate file based on priority.

## Environment File Priority

The application loads environment files in the following order (first found wins):

1. **`.env.prod`** - Production settings (also used locally)
2. **`.env.test`** - Test environment settings
3. **`.env`** - Fallback/default development settings

You can also override this by setting the `ENV_FILE` environment variable:

```bash
ENV_FILE=.env.custom pdm run manage.py runserver
```

## Environment Files

### `.env.prod` (Production)

**Purpose:** Production configuration, also used for local development when you want production-like settings.

**When to use:**

- Running the app locally with production settings
- Deploying to production (copy values to container environment variables)

**Location:** Should be in `.gitignore` (contains secrets)

**Example setup:**

```bash
cp .env.template .env.prod
# Edit .env.prod with your actual values
```

### `.env.test` (Testing)

**Purpose:** Configuration for running tests.

**When to use:**

- Running `pytest` or other test suites
- CI/CD test environments

**Location:** Can be committed (uses test values, no real secrets)

**Features:**

- Uses mock services by default
- DEBUG=True for test output
- Test-specific secret key

### `.env` (Development Fallback)

**Purpose:** Default development settings (lowest priority).

**When to use:**

- Quick local development
- When `.env.prod` and `.env.test` don't exist

**Location:** Should be in `.gitignore` (may contain secrets)

### `.env.template` (Template)

**Purpose:** Template file for new users to copy and configure.

**When to use:**

- Starting a new project setup
- Documenting required environment variables

**Location:** Committed to git (no secrets, safe to share)

**Usage:**

```bash
cp .env.template .env.prod
# Edit .env.prod with your actual values
```

## Required Environment Variables

### Essential Variables

- **`SECRET_KEY`** - Django secret key (required)

  - Generate one: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
  - See [SECURITY.md](SECURITY.md) for more details

- **`DEBUG`** - Debug mode (default: `False`)

  - Set to `True` only for development
  - Always `False` in production

- **`ALLOWED_HOSTS`** - Comma-separated list of allowed hosts
  - Example: `localhost,127.0.0.1,yourdomain.com`

### Optional Variables

- **`USE_MOCK_NOMINATIVE`** - Use mock nominative service (default: `False`)
- **`USE_MOCK_GISN`** - Use mock GISN service (default: `False`)
- **`REFERRER`** - Referrer header for API requests
- **`USER_AGENT`** - User agent string for API requests
- **`SECURE_SSL_REDIRECT`** - Enable SSL redirect (default: `False`, only enable when HTTPS is configured)
- **`SECURE_HSTS_ENABLE`** - Enable HSTS headers (default: `False`, only enable when HTTPS is configured)

## Quick Start

1. **Copy the template:**

   ```bash
   cp .env.template .env.prod
   ```

2. **Generate a secret key:**

   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

3. **Edit `.env.prod`** with your values

4. **Run the application:**
   ```bash
   pdm run manage.py runserver
   ```
   The app will automatically use `.env.prod` (highest priority).

## Running Tests

Tests automatically use `.env.test` if it exists. To run tests:

```bash
pytest
```

## Production Deployment

For production deployment, you should:

1. **Use environment variables** (not `.env.prod` file) in your container/orchestration
2. **Set required variables** in your deployment configuration
3. **Never commit** `.env.prod` or `.env` files to git

Example Docker/Podman run:

```bash
podman run -d \
  -e SECRET_KEY="your-secret-key" \
  -e DEBUG=False \
  -e ALLOWED_HOSTS="yourdomain.com,www.yourdomain.com" \
  your-image:tag
```

## Notes

- All `.env.*` files (except `.env.template`) should be in `.gitignore`
- Boolean values can be: `True`, `true`, `1`, `Yes`, `yes` (case-insensitive)
- The application provides secure defaults - you only need to override what's necessary
- See [SECURITY.md](SECURITY.md) for security best practices
