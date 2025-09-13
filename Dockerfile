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
  && mkdir -p /app/mediafiles

# Set proper permissions
RUN chown -R app:app /app \
  && chown -R app:app /var/log/supervisor \
  && chown -R app:app /var/log/nginx \
  && chown -R app:app /var/lib/nginx

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Copy supervisor configuration
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Collect static files (provide temporary SECRET_KEY for build)
RUN SECRET_KEY=build-time-key-only pdm run manage.py collectstatic --noinput

# Expose port
EXPOSE 8080

# Use supervisor to run both nginx and gunicorn
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
