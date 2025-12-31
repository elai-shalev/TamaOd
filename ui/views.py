from django.shortcuts import render
from django.conf import settings
from django.views.decorators.csrf import ensure_csrf_cookie


@ensure_csrf_cookie
def home(request):
    """Home view - ensures CSRF cookie is set for AJAX requests."""
    context = {
        'debug': settings.DEBUG
    }
    return render(request, "index.html", context)
