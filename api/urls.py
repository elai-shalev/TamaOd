from django.urls import path
from .views import analyze_address, get_streets

urlpatterns = [
    path("analyze/", analyze_address, name="analyze_address"),
    path("streets/", get_streets, name="get_streets")
]

