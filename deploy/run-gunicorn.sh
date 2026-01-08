#!/bin/bash
# Wrapper script to run gunicorn with proper PDM environment

export PDM_HOME="/home/app/.config/pdm"
export HOME="/home/app"

# Run gunicorn via PDM
exec /usr/local/bin/pdm run gunicorn tamaod.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 120

