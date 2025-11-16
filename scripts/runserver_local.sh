#!/bin/bash
# Run Django development server for local development
# Defaults to HTTPS (recommended). Set USE_HTTP=1 to use HTTP instead.

export DEBUG=True
export SECURE_SSL_REDIRECT=False
export SECURE_HSTS_ENABLE=False

# Use localhost instead of 127.0.0.1 to avoid HSTS issues in some browsers
HOST="${HOST:-localhost}"
PORT="${PORT:-8000}"

# Check if HTTP mode is requested
if [ "${USE_HTTP:-0}" = "1" ]; then
    echo "Starting Django development server with HTTP..."
    echo "Access the application at: http://$HOST:$PORT/"
    echo ""
    
    # Use a local .env file if it exists, otherwise use .env.prod but override DEBUG
    if [ -f .env ]; then
        ENV_FILE=.env DEBUG=True SECURE_SSL_REDIRECT=False SECURE_HSTS_ENABLE=False \
            pdm run python manage.py runserver "$HOST:$PORT"
    else
        ENV_FILE=.env.prod DEBUG=True SECURE_SSL_REDIRECT=False SECURE_HSTS_ENABLE=False \
            pdm run python manage.py runserver "$HOST:$PORT"
    fi
else
    # HTTPS mode (default)
    CERT_DIR=".ssl"
    CERT_FILE="$CERT_DIR/localhost.crt"
    KEY_FILE="$CERT_DIR/localhost.key"
    
    # Check if certificates exist, generate if not
    if [ ! -f "$CERT_FILE" ] || [ ! -f "$KEY_FILE" ]; then
        echo "SSL certificates not found. Generating them now..."
        ./scripts/generate_ssl_cert.sh
        echo ""
    fi
    
    # Verify certificates exist
    if [ ! -f "$CERT_FILE" ] || [ ! -f "$KEY_FILE" ]; then
        echo "Error: SSL certificates not found. Please run ./scripts/generate_ssl_cert.sh first."
        exit 1
    fi
    
    echo "Starting Django development server with HTTPS..."
    echo "Access the application at: https://$HOST:$PORT/"
    echo "Note: Your browser will show a security warning for the self-signed certificate."
    echo "This is normal for local development. Click 'Advanced' and 'Proceed' to continue."
    echo ""
    
    # Use a local .env file if it exists, otherwise use .env.prod but override DEBUG
    if [ -f .env ]; then
        ENV_FILE=.env DEBUG=True SECURE_SSL_REDIRECT=False SECURE_HSTS_ENABLE=False \
            pdm run python manage.py runserver_plus \
            --cert-file "$CERT_FILE" \
            --key-file "$KEY_FILE" \
            "$HOST:$PORT"
    else
        ENV_FILE=.env.prod DEBUG=True SECURE_SSL_REDIRECT=False SECURE_HSTS_ENABLE=False \
            pdm run python manage.py runserver_plus \
            --cert-file "$CERT_FILE" \
            --key-file "$KEY_FILE" \
            "$HOST:$PORT"
    fi
fi

