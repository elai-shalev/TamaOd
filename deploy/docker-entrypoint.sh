#!/bin/bash
set -e

# Check for required environment variables
if [ -z "$SECRET_KEY" ]; then
    echo "ERROR: SECRET_KEY environment variable is required"
    echo "Generate one with: python -c \"from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())\""
    exit 1
fi

if [ -z "$ALLOWED_HOSTS" ]; then
    echo "WARNING: ALLOWED_HOSTS not set, defaulting to 'localhost,127.0.0.1'"
    export ALLOWED_HOSTS="localhost,127.0.0.1"
fi

# Set defaults if not provided
export DEBUG="${DEBUG:-False}"
export DJANGO_ENV="${DJANGO_ENV:-production}"

# Default to REAL APIs (not mock) - users can override if needed
export USE_MOCK_NOMINATIVE="${USE_MOCK_NOMINATIVE:-False}"
export USE_MOCK_GISN="${USE_MOCK_GISN:-False}"

echo "Starting TamaOd application..."
echo "  ALLOWED_HOSTS: $ALLOWED_HOSTS"
echo "  DEBUG: $DEBUG"
echo "  USE_MOCK_NOMINATIVE: $USE_MOCK_NOMINATIVE (using REAL Nominatim API)"
echo "  USE_MOCK_GISN: $USE_MOCK_GISN (using REAL GISN API)"
echo ""

# Execute the main command (supervisord)
exec "$@"

