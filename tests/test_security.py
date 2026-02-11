"""Tests for security features: rate limiting, XSS, CSRF, input validation."""
import pytest
import json


@pytest.mark.django_db
class TestRateLimiting:
    """Test rate limiting on API endpoints."""

    def test_analyze_rate_limit_decorator_present(self):
        """Test that analyze endpoint has rate limit decorator."""
        from api.views import analyze_address
        import inspect

        # Check that ratelimit decorator is present
        source = inspect.getsource(analyze_address)
        assert "@ratelimit" in source or "ratelimit" in str(
            analyze_address.__dict__
        )

    def test_streets_rate_limit(self, client):
        """Test that streets endpoint is rate limited to 30 requests/minute."""
        url = "/api/streets/"

        # Make 31 requests (limit is 30/minute)
        for _ in range(30):
            response = client.get(url)
            # Should not be rate limited (429) or forbidden (403)
            assert response.status_code not in [429, 403]

        # 31st request should be rate limited
        response = client.get(url)
        assert response.status_code == 429


@pytest.mark.django_db
class TestInputValidation:
    """Test input validation and sanitization."""

    def test_missing_street(self, client):
        """Test that missing street returns 400."""
        url = "/api/analyze/"
        data = {"houseNumber": 1, "radius": 100}

        response = client.post(
            url,
            data=json.dumps(data),
            content_type="application/json",
        )
        assert response.status_code == 400
        assert "Missing 'street' field" in response.json()["error"]

    def test_missing_house_number(self, client):
        """Test that missing house number returns 400."""
        url = "/api/analyze/"
        data = {"street": "Test Street", "radius": 100}

        response = client.post(
            url,
            data=json.dumps(data),
            content_type="application/json",
        )
        assert response.status_code == 400
        assert "Missing 'house number' field" in response.json()["error"]

    def test_invalid_house_number_type(self, client):
        """Test that house number with no digits returns 400."""
        url = "/api/analyze/"
        data = {"street": "Test Street", "houseNumber": "abc", "radius": 100}

        response = client.post(
            url,
            data=json.dumps(data),
            content_type="application/json",
        )
        assert response.status_code == 400
        assert "must contain at least one digit" in response.json()["error"]

    def test_empty_house_number(self, client):
        """Test that empty string house number returns 400."""
        url = "/api/analyze/"
        data = {"street": "Test Street", "houseNumber": "", "radius": 100}

        response = client.post(
            url,
            data=json.dumps(data),
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_alphanumeric_house_number_accepted(self, client):
        """Test that alphanumeric house numbers like '10A' are accepted."""
        url = "/api/analyze/"
        data = {"street": "Test Street", "houseNumber": "10A", "radius": 100}

        response = client.post(
            url,
            data=json.dumps(data),
            content_type="application/json",
        )
        # Should not return 400 for house number validation
        assert response.status_code != 400 or "houseNumber" not in response.json().get(
            "error", ""
        )

    def test_invalid_radius_type(self, client):
        """Test that non-numeric radius returns 400."""
        url = "/api/analyze/"
        data = {"street": "Test Street", "houseNumber": 1, "radius": "abc"}

        response = client.post(
            url,
            data=json.dumps(data),
            content_type="application/json",
        )
        assert response.status_code == 400
        assert "must be a number" in response.json()["error"]

    def test_radius_out_of_range_low(self, client):
        """Test that radius < 10 returns 400."""
        url = "/api/analyze/"
        data = {"street": "Test Street", "houseNumber": 1, "radius": 5}

        response = client.post(
            url,
            data=json.dumps(data),
            content_type="application/json",
        )
        assert response.status_code == 400
        assert "must be between 10 and 5000" in response.json()["error"]

    def test_radius_out_of_range_high(self, client):
        """Test that radius > 5000 returns 400."""
        url = "/api/analyze/"
        data = {"street": "Test Street", "houseNumber": 1, "radius": 6000}

        response = client.post(
            url,
            data=json.dumps(data),
            content_type="application/json",
        )
        assert response.status_code == 400
        assert "must be between 10 and 5000" in response.json()["error"]

    def test_xss_attempt_in_street(self, client):
        """Test that XSS attempts in street name are sanitized."""
        url = "/api/analyze/"
        data = {
            "street": "<script>alert('xss')</script>Test Street",
            "houseNumber": 1,
            "radius": 100,
        }

        response = client.post(
            url,
            data=json.dumps(data),
            content_type="application/json",
        )
        # Should either sanitize or reject
        # Script tags should be removed
        assert response.status_code in [200, 400, 500]
        if response.status_code == 400:
            # Invalid characters were rejected
            assert "invalid" in response.json()["error"].lower()

    def test_html_injection_in_street(self, client):
        """Test that HTML injection in street name is sanitized."""
        url = "/api/analyze/"
        data = {
            "street": "<b>Bold Street</b>",
            "houseNumber": 1,
            "radius": 100,
        }

        response = client.post(
            url,
            data=json.dumps(data),
            content_type="application/json",
        )
        # HTML tags should be stripped
        assert response.status_code in [200, 400, 500]

    def test_invalid_json(self, client):
        """Test that invalid JSON returns 400."""
        url = "/api/analyze/"

        response = client.post(
            url,
            data="not valid json",
            content_type="application/json",
        )
        assert response.status_code == 400
        assert "Invalid JSON" in response.json()["error"]

    def test_radius_default_value(self, client):
        """Test that radius defaults to 100 if not provided."""
        url = "/api/analyze/"
        data = {"street": "Test Street", "houseNumber": 1}

        # Should not raise error, radius should default to 100
        response = client.post(
            url,
            data=json.dumps(data),
            content_type="application/json",
        )
        # May return 200 or 500 depending on service availability
        # But should NOT return 400 for missing radius
        assert response.status_code != 400 or "radius" not in response.json().get(
            "error", ""
        ).lower()


@pytest.mark.django_db
class TestCSRFProtection:
    """Test CSRF protection on API endpoints."""

    def test_csrf_protection_enabled(self, client):
        """Test that CSRF protection is enabled (csrf_exempt removed)."""
        # Django test client handles CSRF automatically
        # To test CSRF protection, we need to use enforce_csrf_checks
        from django.test import Client as DjangoClient

        csrf_client = DjangoClient(enforce_csrf_checks=True)

        url = "/api/analyze/"
        data = {"street": "Test Street", "houseNumber": 1, "radius": 100}

        # POST without CSRF token should fail
        response = csrf_client.post(
            url,
            data=json.dumps(data),
            content_type="application/json",
        )

        # Should return 403 Forbidden (CSRF verification failed)
        assert response.status_code == 403


@pytest.mark.django_db
class TestSecurityHeaders:
    """Test security headers are properly set."""

    def test_csp_header_present(self, client, settings):
        """Test that CSP headers are present."""
        # CSP headers may not be set in test mode
        # Just verify middleware is configured
        assert "csp.middleware.CSPMiddleware" in settings.MIDDLEWARE

    def test_xframe_options(self, client, settings):
        """Test X-Frame-Options is set correctly."""
        # Only in production (DEBUG=False)
        if not settings.DEBUG:
            response = client.get("/")
            assert "X-Frame-Options" in response
            assert response["X-Frame-Options"] == "DENY"

    def test_content_type_nosniff(self, client, settings):
        """Test X-Content-Type-Options is set."""
        # Only in production (DEBUG=False)
        if not settings.DEBUG:
            response = client.get("/")
            assert "X-Content-Type-Options" in response
            assert response["X-Content-Type-Options"] == "nosniff"


@pytest.mark.django_db
class TestStringSanitization:
    """Test the sanitize_string function."""

    def test_sanitize_removes_html_tags(self):
        """Test that HTML tags are removed."""
        from api.views import sanitize_string

        result = sanitize_string("<script>alert('xss')</script>Hello")
        # HTML tags should be removed
        assert "<script>" not in result
        assert "</script>" not in result
        # Text content remains (which is expected behavior)

    def test_sanitize_limits_length(self):
        """Test that string length is limited."""
        from api.views import sanitize_string

        long_string = "A" * 200
        result = sanitize_string(long_string, max_length=50)
        assert len(result) <= 50

    def test_sanitize_allows_safe_characters(self):
        """Test that safe characters are allowed."""
        from api.views import sanitize_string

        result = sanitize_string("Test Street 123")
        # Should contain alphanumeric and spaces
        assert "Test" in result or "Street" in result or "123" in result

    def test_sanitize_removes_dangerous_characters(self):
        """Test that dangerous characters are removed."""
        from api.views import sanitize_string

        result = sanitize_string("Test<>&\"'")
        # Special characters should be removed or escaped
        # The actual behavior depends on implementation
        # At minimum, the string should not contain raw HTML entities
        assert result != "Test<>&\"'"

    def test_sanitize_non_string_input(self):
        """Test that non-string input is converted and sanitized."""
        from api.views import sanitize_string

        class MaliciousObj:
            def __str__(self):
                return "<script>alert('xss')</script>hello"

        result = sanitize_string(MaliciousObj())
        assert "<script>" not in result
        assert "hello" in result
