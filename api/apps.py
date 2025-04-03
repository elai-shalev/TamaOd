from django.apps import AppConfig
from django.conf import settings


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        """Register the appropriate API service."""
        from api.services import RealNominativeQuery
        from api.services import MockNominativeQuery
        from api.services import MockGISNQuery
        from api.services import RealGISNQuery

        nominative_class = MockNominativeQuery if getattr(settings, "USE_MOCK_NOMINATIVE", False) else RealNominativeQuery
        gisn_class = MockGISNQuery if getattr(settings, "USE_MOCK_GISN", False) else RealGISNQuery
        
        self.nominative_service = nominative_class()
        self.gisn_service = gisn_class()
