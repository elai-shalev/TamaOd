#!/bin/bash
# Wrapper script to run gunicorn with proper PDM environment

# Use /tmp for PDM config in OpenShift (random UID can't write to /home/app)
export PDM_HOME="/tmp/pdm"
export HOME="/tmp"
mkdir -p "$PDM_HOME"

# Run gunicorn via PDM
exec /usr/local/bin/pdm run gunicorn tamaod.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 120

