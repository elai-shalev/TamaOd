#!/bin/bash
# Build and obfuscate JavaScript for production

set -e

echo "Building and obfuscating JavaScript..."

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing npm dependencies..."
    npm install
fi

# Build production JavaScript
npm run build

echo "✅ JavaScript built and obfuscated successfully!"
echo "Output: ui/static/js/dist/script.min.js"
echo ""
echo "Update your HTML templates to use:"
echo '<script src="{% static 'js/dist/script.min.js' %}"></script>'
