# Security Information

## 🔒 Container Image Security

This Docker image is designed for public distribution and follows security best practices:

### ✅ What's Secure

- **No Hardcoded Secrets**: All sensitive data must be provided via environment variables
- **Environment Isolation**: No development files or git history included in image
- **Runtime Configuration**: All secrets configured at container runtime
- **Minimal Attack Surface**: Production-only dependencies included

### 🔧 Required Environment Variables

**CRITICAL**: The following environment variables are REQUIRED for secure operation:

```bash
SECRET_KEY=your-cryptographically-strong-secret-key-here
```

**Optional but Recommended**:

```bash
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DEBUG=False  # Default: False
```

### 🚨 Security Requirements for Users

#### 1. Generate a Strong SECRET_KEY

```bash
# Generate a secure secret key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

#### 2. Set Proper ALLOWED_HOSTS

```bash
# Only allow your domains
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

#### 3. Never Use Default Values in Production

```bash
# ❌ DON'T DO THIS
SECRET_KEY=django-insecure-change-this-in-production

# ✅ DO THIS
SECRET_KEY=your-generated-secure-key-here
```

### 🛡️ Security Features

- **HTTPS Headers**: Security headers configured in nginx
- **XSS Protection**: Built-in XSS filtering
- **CSRF Protection**: Django CSRF middleware enabled
- **Content Security**: Proper content-type headers
- **Frame Protection**: X-Frame-Options set to DENY

### 🔍 What's NOT Included

This image does NOT contain:

- Source code repository (.git)
- Development dependencies
- Environment files (.env)
- Database data (SQLite starts empty)
- Any hardcoded credentials

### 📋 Security Checklist for Deployment

- [ ] Set unique `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS` for your domain
- [ ] Set `DEBUG=False` (default)
- [ ] Use HTTPS in production (configure reverse proxy)
- [ ] Monitor container logs
- [ ] Keep base image updated
- [ ] Use proper database in production (not SQLite)

### 🚨 Reporting Security Issues

If you discover a security vulnerability in this image:

1. Do NOT create a public issue
2. Contact the maintainer privately
3. Provide detailed information about the vulnerability

### 📚 Additional Security Resources

- [Django Security Documentation](https://docs.djangoproject.com/en/stable/topics/security/)
- [Docker Security Best Practices](https://docs.docker.com/develop/security-best-practices/)
- [OWASP Container Security](https://owasp.org/www-project-container-security/)

---

**Remember**: This image provides the application code, but YOU are responsible for secure deployment configuration.
