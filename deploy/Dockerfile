# Use Python 3.13 slim image
FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1 \
  DJANGO_ENV=production \
  PORT=8080 \
  PDM_USE_VENV=false

# Install system dependencies
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
  nginx \
  supervisor \
  curl \
  && rm -rf /var/lib/apt/lists/*

# Create app user
RUN useradd --create-home --shell /bin/bash app

# Set work directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml pdm.lock ./

# Install PDM and project dependencies
RUN pip install --no-cache-dir pdm \
  && pdm install --prod --without dev

# Copy project files
COPY . .

# Create necessary directories
RUN mkdir -p /var/log/supervisor \
  && mkdir -p /app/staticfiles \
  && mkdir -p /app/mediafiles \
  && mkdir -p /var/run

# Create PDM config directory for app user
RUN mkdir -p /home/app/.config/pdm \
  && chown -R app:app /home/app/.config

# Set proper permissions
RUN chown -R app:app /app \
  && chown -R app:app /var/log/supervisor \
  && chown -R app:app /var/log/nginx \
  && chown -R app:app /var/lib/nginx \
  && chmod 755 /var/run

# Copy nginx configuration
COPY deploy/nginx.conf /etc/nginx/nginx.conf

# Copy supervisor configuration
COPY deploy/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Copy entrypoint script
COPY deploy/docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Copy gunicorn wrapper script
COPY deploy/run-gunicorn.sh /usr/local/bin/run-gunicorn.sh
RUN chmod +x /usr/local/bin/run-gunicorn.sh

# Collect static files (provide temporary SECRET_KEY for build)
RUN SECRET_KEY=build-time-key-only pdm run manage.py collectstatic --noinput

# Expose port
EXPOSE 8080

# Use entrypoint to validate environment and start supervisord
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
