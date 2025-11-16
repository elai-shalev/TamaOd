#!/bin/bash
# Generate self-signed SSL certificate for local development
# This creates certificates that work for both localhost and 127.0.0.1

CERT_DIR=".ssl"
CERT_FILE="$CERT_DIR/localhost.crt"
KEY_FILE="$CERT_DIR/localhost.key"

# Create .ssl directory if it doesn't exist
mkdir -p "$CERT_DIR"

# Check if OpenSSL is available
if ! command -v openssl &> /dev/null; then
    echo "Error: openssl is not installed. Please install it first."
    echo "  On Fedora/RHEL: sudo dnf install openssl"
    echo "  On Ubuntu/Debian: sudo apt-get install openssl"
    exit 1
fi

# Generate certificate if it doesn't exist
if [ ! -f "$CERT_FILE" ] || [ ! -f "$KEY_FILE" ]; then
    echo "Generating self-signed SSL certificate for local development..."
    openssl req -x509 -newkey rsa:4096 -nodes \
        -keyout "$KEY_FILE" \
        -out "$CERT_FILE" \
        -days 365 \
        -subj "/C=US/ST=State/L=City/O=Development/CN=localhost" \
        -addext "subjectAltName=DNS:localhost,DNS:*.localhost,IP:127.0.0.1,IP:::1"
    
    echo "Certificate generated successfully!"
    echo "  Certificate: $CERT_FILE"
    echo "  Private Key: $KEY_FILE"
    echo ""
    echo "Note: Your browser will show a security warning for self-signed certificates."
    echo "This is normal for local development. Click 'Advanced' and 'Proceed' to continue."
else
    echo "SSL certificate already exists at $CERT_FILE"
    echo "To regenerate, delete the certificate files and run this script again."
fi

