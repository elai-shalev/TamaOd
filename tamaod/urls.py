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
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib.staticfiles.views import serve as staticfiles_serve
from django.views.decorators.cache import never_cache

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('', include('ui.urls')),
]

# Serve static and media files
# In production, these should ideally be served by nginx/web server,
# but we serve them here for local development (e.g., when using .env.prod)
# Static files are automatically discovered from the 'ui' app's static directory

# Serve static files from ui/static/ (for development)
# Using 'static/<path:path>' since STATIC_URL is '/static/'
if settings.DEBUG:
    # In DEBUG mode, use the standard staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()
else:
    # In production/non-DEBUG mode, use staticfiles finders explicitly
    # This allows serving files from ui/static/ without requiring
    # collectstatic. The serve view uses staticfiles finders to locate
    # files in app directories
    urlpatterns += [
        path(
            'static/<path:path>',
            never_cache(staticfiles_serve),
        ),
    ]

# Serve media files
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
