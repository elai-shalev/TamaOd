# TamaOd OpenShift Deployment Guide

## Overview

This document provides context and lessons learned from deploying the TamaOd Django application to OpenShift. It serves as a reference for anyone deploying this application to Kubernetes or OpenShift clusters in the future.

## Application Architecture

The TamaOd application uses a multi-process containerized architecture:

- **nginx**: Reverse proxy handling static files and request routing
- **gunicorn**: WSGI application server running Django (2 workers)
- **supervisord**: Process manager running both nginx and gunicorn in a single container
- **Django**: The main application framework

## Key OpenShift/Kubernetes Concepts

### Security Context Constraints (OpenShift)

OpenShift enforces stricter security than standard Kubernetes:

- **Random UID assignment**: Containers run with random high UIDs (e.g., 1000660000-1000669999)
- **Cannot specify runAsUser**: Don't set `runAsUser` or `fsGroup` in deployment specs
- **Non-root required**: All containers must run as non-root users
- **Limited write access**: Only `/tmp` is reliably writable

**Solution**: Design containers to work with any UID and write only to `/tmp`.

### File System Permissions

In OpenShift, you cannot rely on specific user ownership from your Dockerfile.

**Problematic locations**:
- `/var/log/` - Not writable
- `/var/lib/` - Not writable
- `/etc/nginx/` - Not writable
- `/home/app/` - Not writable

**Solution**: Use `/tmp` for all runtime files:
```bash
# nginx temp directories
/tmp/nginx_client_body
/tmp/nginx_proxy
/tmp/nginx.conf
/tmp/nginx.pid

# Application logs
/tmp/django_stderr.log
/tmp/nginx_stderr.log
/tmp/supervisord.log

# PDM configuration
PDM_HOME=/tmp/pdm
HOME=/tmp
```

### Container Configuration Changes Required

**1. Remove user directives from supervisord.conf**:
```ini
# ❌ Don't do this (fails in OpenShift)
[supervisord]
user=app

[program:nginx]
user=app

# ✅ Do this instead
[supervisord]
# No user directive

[program:nginx]
# No user directive
```

**2. Configure nginx temporary paths**:
```nginx
http {
    client_body_temp_path /tmp/nginx_client_body;
    proxy_temp_path /tmp/nginx_proxy;
    fastcgi_temp_path /tmp/nginx_fastcgi;
    uwsgi_temp_path /tmp/nginx_uwsgi;
    scgi_temp_path /tmp/nginx_scgi;
}
```

**3. Set PDM environment variables**:
```bash
export PDM_HOME="/tmp/pdm"
export HOME="/tmp"
mkdir -p "$PDM_HOME"
```

**4. Remove runAsUser from deployment.yaml**:
```yaml
# ❌ Don't do this
securityContext:
  runAsUser: 1000
  fsGroup: 1000

# ✅ Do this instead
securityContext:
  runAsNonRoot: true
  seccompProfile:
    type: RuntimeDefault
```

## Resource Constraints

Lab and test clusters often have limited resources. The application was successfully deployed with minimal resource requests:

```yaml
resources:
  requests:
    memory: "32Mi"   # Minimal to get scheduled
    cpu: "25m"
  limits:
    memory: "256Mi"  # Can grow if available
    cpu: "200m"
```

**Important**: Check cluster capacity before deployment:
```bash
oc describe node | grep -A 10 "Allocated resources"
```

## External Access Options

### OpenShift Route (Recommended for OpenShift)

OpenShift Routes provide simpler SSL termination than Kubernetes Ingress:

```yaml
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: tamaod
  namespace: tamaod
spec:
  to:
    kind: Service
    name: tamaod
  tls:
    termination: edge  # OpenShift handles SSL
    insecureEdgeTerminationPolicy: Redirect
```

**Benefits**:
- Automatic SSL certificates (OpenShift default CA)
- No additional cert-manager setup required
- Automatic HTTP to HTTPS redirect

### Kubernetes Ingress (Alternative)

For standard Kubernetes clusters, use Ingress with cert-manager:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - tamaod.example.com
    secretName: tamaod-tls
```

**Note**: Let's Encrypt requires public internet access for ACME HTTP-01 challenges. Internal/lab clusters behind VPNs cannot use Let's Encrypt.

## Django Configuration

### ALLOWED_HOSTS

Django validates the HTTP `Host` header. You must include your OpenShift route hostname:

```python
# In settings.py (via environment variable)
ALLOWED_HOSTS = [
    'tamaod-namespace.apps.cluster-domain.com',  # Full OpenShift route hostname
    'localhost',
    '127.0.0.1'
]
```

**Getting your route hostname**:
```bash
oc get route -n tamaod -o jsonpath='{.items[0].spec.host}'
```

### SECRET_KEY

Always generate a unique SECRET_KEY for production:

```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Store it in a Kubernetes Secret:
```bash
echo -n 'your-secret-key-here' | base64
```

### Environment Variables

Non-sensitive configuration can go in ConfigMaps:
- `DEBUG=False` (always in production)
- `SSL_ENABLED=false` (when using OpenShift edge termination)
- Feature flags

Sensitive data must go in Secrets:
- `SECRET_KEY`
- `ALLOWED_HOSTS`
- Database credentials
- API keys

## Container Registry

### Quay.io Considerations

Quay.io repositories are **private by default**:

**Option 1**: Make repository public (easiest for testing)
- Go to Quay.io → Repository Settings → Make Public

**Option 2**: Create image pull secret (production)
```bash
oc create secret docker-registry quay-secret \
  --docker-server=quay.io \
  --docker-username=<username> \
  --docker-password=<token> \
  -n tamaod

# Reference in deployment
spec:
  imagePullSecrets:
  - name: quay-secret
```

## SSL/TLS Strategy

### Internal Clusters (Lab/VPN-only)

**Use**: OpenShift's default certificates with edge termination

**Pros**:
- Works immediately
- No external dependencies
- Acceptable for internal applications

**Cons**:
- Browser warnings (self-signed or internal CA)
- Not trusted by external clients

### Public Clusters

**Use**: cert-manager with Let's Encrypt

**Requirements**:
- Domain must be publicly accessible
- HTTP-01 challenge must reach `http://domain/.well-known/acme-challenge/`
- Not suitable for VPN-only or internal networks

**Setup**:
```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.3/cert-manager.yaml

# Create ClusterIssuer
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-prod-key
    solvers:
    - http01:
        ingress:
          class: nginx
```

## Common Deployment Issues

### Pod Stuck in "Pending"
**Cause**: Insufficient cluster resources
**Solution**: Reduce resource requests or free up cluster capacity

### ImagePullBackOff
**Cause**: Cannot access container registry (private repository)
**Solution**: Make repository public or create image pull secret

### CrashLoopBackOff
**Cause**: Application error (check logs)
**Solution**:
```bash
oc logs -n tamaod -l app=tamaod --tail=100
oc exec -n tamaod deployment/tamaod -- cat /tmp/django_stderr.log
```

### HTTP 400 Bad Request
**Cause**: Django ALLOWED_HOSTS doesn't include route hostname
**Solution**: Update secret with full route hostname

### 502 Bad Gateway
**Cause**: Django/gunicorn not running
**Solution**: Check Django logs and PDM configuration

### Permission Denied Errors
**Cause**: Trying to write to non-writable directories
**Solution**: Move all runtime files to `/tmp/`

## Deployment Workflow

### Initial Deployment

1. **Build and push container image**:
```bash
podman build -f deploy/Dockerfile -t quay.io/username/tamaod:latest .
podman push quay.io/username/tamaod:latest
```

2. **Create Kubernetes resources**:
   - Namespace
   - ConfigMap (non-sensitive config)
   - Secret (SECRET_KEY, ALLOWED_HOSTS)
   - Deployment
   - Service (ClusterIP)
   - Route/Ingress

3. **Get the route hostname**:
```bash
oc get route -n tamaod
```

4. **Update ALLOWED_HOSTS** with route hostname and redeploy

5. **Verify deployment**:
```bash
oc get pods -n tamaod
oc logs -n tamaod -l app=tamaod
curl https://your-route-hostname/health/
```

### Redeployment

```bash
# Build new image
podman build -f deploy/Dockerfile -t quay.io/username/tamaod:latest .
podman push quay.io/username/tamaod:latest

# Restart pods to pull new image
oc delete pods -l app=tamaod -n tamaod
```

## Security Best Practices

### Secrets Management
✅ Store secrets in Kubernetes Secrets (not in code)
✅ Use `.gitignore` to prevent committing secrets
✅ Provide template files for documentation
✅ Base64-encode secret values (Kubernetes standard)

### Container Security
✅ Run as non-root user (OpenShift enforces this)
✅ Drop all capabilities
✅ Use seccomp profile
✅ Minimize writable locations (use /tmp only)

### Network Security
✅ Use ClusterIP service (not exposed directly)
✅ Enable TLS encryption via Route/Ingress
✅ Redirect insecure HTTP to HTTPS
✅ Validate Host headers (ALLOWED_HOSTS)

### Application Security
✅ Generate unique SECRET_KEY
✅ Set DEBUG=False in production
✅ Configure ALLOWED_HOSTS validation
✅ Use security headers (X-Content-Type-Options, X-Frame-Options)

## Production Readiness Checklist

Before deploying to production:

- [ ] Generate unique SECRET_KEY
- [ ] Set DEBUG=False
- [ ] Configure ALLOWED_HOSTS with actual domain
- [ ] Set appropriate resource limits
- [ ] Configure SSL certificates
- [ ] Set up monitoring and logging
- [ ] Configure database (if needed, currently SQLite)
- [ ] Configure backup strategy
- [ ] Review replica count
- [ ] Set up health check alerts
- [ ] Scan container image for vulnerabilities
- [ ] Configure RBAC permissions
- [ ] Set up network policies (if needed)
- [ ] Configure persistent storage (if needed)

## Key Takeaways

1. **OpenShift is more restrictive than Kubernetes** - this is good for security
2. **All writable paths should use `/tmp`** in OpenShift
3. **Test locally with podman/docker first**, but expect OpenShift to behave differently
4. **OpenShift Routes are simpler than Kubernetes Ingress** for basic SSL
5. **Let's Encrypt requires public internet access** - won't work for internal networks
6. **Resource constraints matter** - always check cluster capacity
7. **ALLOWED_HOSTS must match the route hostname** - including the full generated domain
8. **Security Context Constraints are strictly enforced** - work with them, not against them
9. **Never commit actual secrets** - use templates and .gitignore
10. **Iterate quickly** - Build → Push → Deploy → Debug → Fix

## Additional Resources

- [OpenShift Routes Documentation](https://docs.openshift.com/container-platform/latest/networking/routes/route-configuration.html)
- [Security Context Constraints](https://docs.openshift.com/container-platform/latest/authentication/managing-security-context-constraints.html)
- [cert-manager Documentation](https://cert-manager.io/docs/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [nginx Documentation](https://nginx.org/en/docs/)
- [gunicorn Documentation](https://docs.gunicorn.org/)

---

**Document Version**: 1.0
**Last Updated**: December 31, 2025
**Deployment Target**: OpenShift 4.x / Kubernetes 1.25+
