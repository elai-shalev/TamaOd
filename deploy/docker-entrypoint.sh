#!/bin/bash
set -e

# Check for required environment variables
if [ -z "$SECRET_KEY" ]; then
    echo "ERROR: SECRET_KEY environment variable is required"
    echo "Generate one with: python3 -c \"from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())\""
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

# SSL Configuration
# Options: 'true' (require SSL), 'false' (disable SSL), 'auto' (enable if certs present)
export SSL_ENABLED="${SSL_ENABLED:-auto}"

SSL_CERT="/etc/ssl/certs/app.crt"
SSL_KEY="/etc/ssl/private/app.key"

# Determine which nginx config to use based on SSL settings
configure_ssl() {
    local use_ssl=false

    if [ "$SSL_ENABLED" = "true" ]; then
        # SSL explicitly required
        if [ -f "$SSL_CERT" ] && [ -f "$SSL_KEY" ]; then
            use_ssl=true
        else
            echo "ERROR: SSL_ENABLED=true but certificates not found!"
            echo ""
            echo "Expected certificate locations:"
            echo "  Certificate: $SSL_CERT"
            echo "  Private Key: $SSL_KEY"
            echo ""
            echo "Mount your certificates using docker/podman volume mounts:"
            echo ""
            echo "Examples:"
            echo "  Let's Encrypt:"
            echo "    -v /etc/letsencrypt/live/domain.com/fullchain.pem:/etc/ssl/certs/app.crt:ro \\"
            echo "    -v /etc/letsencrypt/live/domain.com/privkey.pem:/etc/ssl/private/app.key:ro"
            echo ""
            echo "  Custom CA:"
            echo "    -v /path/to/custom.crt:/etc/ssl/certs/app.crt:ro \\"
            echo "    -v /path/to/custom.key:/etc/ssl/private/app.key:ro"
            exit 1
        fi
    elif [ "$SSL_ENABLED" = "auto" ]; then
        # Auto-detect SSL based on certificate presence
        if [ -f "$SSL_CERT" ] && [ -f "$SSL_KEY" ]; then
            use_ssl=true
        fi
    fi
    # SSL_ENABLED=false means use_ssl stays false

    if [ "$use_ssl" = true ]; then
        echo "SSL certificates found - enabling HTTPS mode"
        # Try to copy to /etc/nginx if writable, otherwise use /tmp
        if cp /etc/nginx/nginx-ssl.conf /etc/nginx/nginx.conf 2>/dev/null; then
            export NGINX_CONF="/etc/nginx/nginx.conf"
        else
            cp /etc/nginx/nginx-ssl.conf /tmp/nginx.conf
            export NGINX_CONF="/tmp/nginx.conf"
        fi
        export SSL_ACTIVE="true"
    else
        echo "SSL disabled - using HTTP-only mode"
        # Try to copy to /etc/nginx if writable, otherwise use /tmp
        if cp /etc/nginx/nginx-http.conf /etc/nginx/nginx.conf 2>/dev/null; then
            export NGINX_CONF="/etc/nginx/nginx.conf"
        else
            cp /etc/nginx/nginx-http.conf /tmp/nginx.conf
            export NGINX_CONF="/tmp/nginx.conf"
        fi
        export SSL_ACTIVE="false"
    fi
}

# Configure SSL
configure_ssl

echo ""
echo "Starting TamaOd application..."
echo "  ALLOWED_HOSTS: $ALLOWED_HOSTS"
echo "  DEBUG: $DEBUG"
echo "  SSL_ACTIVE: $SSL_ACTIVE"
echo "  USE_MOCK_NOMINATIVE: $USE_MOCK_NOMINATIVE"
echo "  USE_MOCK_GISN: $USE_MOCK_GISN"
echo ""

# Execute the main command (supervisord)
exec "$@"
