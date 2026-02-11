from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django_ratelimit.decorators import ratelimit
import json
from pathlib import Path
from api.services import handle_address
import bleach
import re


def sanitize_string(value, max_length=100):
    """Sanitize string input to prevent XSS and injection attacks.

    Args:
        value: The string to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        value = str(value)

    # Strip whitespace
    value = value.strip()

    # Limit length
    value = value[:max_length]

    # Remove any HTML tags
    value = bleach.clean(value, tags=[], strip=True)

    # Only allow alphanumeric, spaces, and common punctuation for addresses
    # Hebrew characters: \u0590-\u05FF
    # English letters, numbers, spaces, hyphens, apostrophes
    return re.sub(r'[^\u0590-\u05FF\w\s\-\'.,]', '', value)


@ratelimit(key='ip', rate='20/m', method='POST', block=False)
@require_http_methods(["POST"])
def analyze_address(request):
    """Analyze an address for nearby problematic buildings.

    Rate limited to 20 requests per minute per IP address.
    """
    # Check if rate limited
    if getattr(request, 'limited', False):
        return JsonResponse(
            {"error": "Too many requests. Please try again later."},
            status=429
        )

    try:
        data = json.loads(request.body)
        street = data.get("street")
        house_number = data.get("houseNumber")
        radius = data.get("radius")

        # Validate required fields
        if not street:
            return JsonResponse(
                {"error": "Missing 'street' field"}, status=400
            )
        if house_number is None or house_number == "":
            return JsonResponse(
                {"error": "Missing 'house number' field"}, status=400
            )

        # Sanitize street name
        street = sanitize_string(street, max_length=200)
        if not street:
            return JsonResponse(
                {
                    "error": (
                        "Invalid 'street' - contains invalid characters"
                    )
                },
                status=400,
            )

        # Sanitize house number as string (supports alphanumeric like "10A")
        house_number = sanitize_string(str(house_number), max_length=10)
        if not house_number or not re.search(r'\d', house_number):
            return JsonResponse(
                {"error": "Invalid 'houseNumber' - must contain at least one digit"},
                status=400,
            )

        # Convert radius to int, default to 100 if not provided
        if radius is None:
            radius = 100
        else:
            try:
                radius = int(radius)
                if radius < 10 or radius > 5000:
                    return JsonResponse(
                        {
                            "error": (
                                "Invalid 'radius' - "
                                "must be between 10 and 5000"
                            )
                        },
                        status=400,
                    )
            except (ValueError, TypeError):
                return JsonResponse(
                    {"error": "Invalid 'radius' - must be a number"},
                    status=400,
                )

        try:
            response_data = handle_address(street, house_number, radius)
            return JsonResponse(response_data, safe=False)
        except Exception:
            # Don't expose internal error details
            return JsonResponse(
                {"error": "An error occurred processing your request"},
                status=500,
            )

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)


@ratelimit(key='ip', rate='30/m', method='GET', block=False)
@require_http_methods(["GET"])
def get_streets(request):
    """Get list of available streets.

    Rate limited to 30 requests per minute per IP address.
    """
    # Check if rate limited
    if getattr(request, 'limited', False):
        return JsonResponse(
            {"error": "Too many requests. Please try again later."},
            status=429
        )

    try:
        data_dir = Path(__file__).resolve().parent / "data"
        streets_path = data_dir / "streets.json"
        with streets_path.open(encoding="utf-8") as f:
            street_data = json.load(f)
        street_names = street_data.get("t_rechov_values", [])

        # Sanitize street names before returning
        sanitized_streets = [
            sanitize_string(street, max_length=200)
            for street in street_names
        ]

        return JsonResponse({"streets": sanitized_streets})
    except FileNotFoundError:
        return JsonResponse({"error": "Data not available"}, status=500)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Data format error"}, status=500)
