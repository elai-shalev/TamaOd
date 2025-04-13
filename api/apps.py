from django.apps import AppConfig
from django.conf import settings
from api.services import RealNominativeQuery, MockNominativeQuery
from api.services import RealGISNQuery, MockGISNQuery
from api import app_state

class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        """Register the appropriate API service."""
        use_mock_nominative = getattr(settings, "USE_MOCK_NOMINATIVE", False)
        print(use_mock_nominative)
        use_mock_gisn = getattr(settings, "USE_MOCK_GISN", False)
        print(use_mock_gisn)

        nominative_class = MockNominativeQuery if use_mock_nominative else RealNominativeQuery
        gisn_class = MockGISNQuery if use_mock_gisn else RealGISNQuery

        nominative_service = nominative_class()
        gisn_service = gisn_class()

        app_state.set_services(nominative_service, gisn_service)
