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

# Create necessary directories (including SSL and certbot directories)
RUN mkdir -p /var/log/supervisor \
  && mkdir -p /app/staticfiles \
  && mkdir -p /app/mediafiles \
  && mkdir -p /var/run \
  && mkdir -p /var/cache/nginx \
  && mkdir -p /var/lib/nginx/tmp \
  && mkdir -p /app/run \
  && mkdir -p /var/www/certbot \
  && mkdir -p /etc/ssl/certs \
  && mkdir -p /etc/ssl/private

# Create PDM config directory for app user
RUN mkdir -p /home/app/.config/pdm \
  && chown -R app:app /home/app/.config

# Set proper permissions
RUN chown -R app:app /app \
  && chown -R app:app /var/log/supervisor \
  && chown -R app:app /var/log/nginx \
  && chown -R app:app /var/lib/nginx \
  && chown -R app:app /var/cache/nginx \
  && chown -R app:app /var/run \
  && chown -R app:app /app/run \
  && chown -R app:app /var/www/certbot \
  && chown -R app:app /etc/ssl/certs \
  && chown -R app:app /etc/ssl/private

# Copy nginx configurations (entrypoint will choose based on SSL availability)
COPY deploy/nginx.conf /etc/nginx/nginx-http.conf
COPY deploy/nginx-ssl.conf /etc/nginx/nginx-ssl.conf

# Set nginx config permissions so app user can switch between HTTP/HTTPS configs
# Default to HTTP config, entrypoint will switch if SSL certs are present
RUN cp /etc/nginx/nginx-http.conf /etc/nginx/nginx.conf \
  && chown app:app /etc/nginx/nginx.conf \
  && chown app:app /etc/nginx/nginx-http.conf \
  && chown app:app /etc/nginx/nginx-ssl.conf

# Copy supervisor configuration
COPY deploy/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Copy entrypoint script
COPY deploy/docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Copy gunicorn wrapper script
COPY deploy/run-gunicorn.sh /usr/local/bin/run-gunicorn.sh
RUN chmod +x /usr/local/bin/run-gunicorn.sh

# Collect static files as app user (provide temporary SECRET_KEY for build)
# Note: We need to ensure app user owns /app before running collectstatic
RUN chown -R app:app /app
USER app
RUN SECRET_KEY=build-time-key-only pdm run manage.py collectstatic --noinput

# Expose HTTP and HTTPS ports
EXPOSE 8080 8443

# Run as app user (supervisord will also run as app user)
# Use entrypoint to validate environment and start supervisord
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
