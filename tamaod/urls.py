"""
URL configuration for TamaOd project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('', include('ui.urls')),
]

# Serve static and media files
# In production, these should ideally be served by nginx/web server,
# but we serve them here for local development (e.g., when using .env.prod)
# All static files are in ui/static/ (defined in STATICFILES_DIRS)

# Serve static files from ui/static/
# Using 'static/<path:path>' since STATIC_URL is '/static/'
urlpatterns += [
    path(
        'static/<path:path>',
        serve,
        {'document_root': settings.STATICFILES_DIRS[0]},
    ),
]

# Serve media files
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
