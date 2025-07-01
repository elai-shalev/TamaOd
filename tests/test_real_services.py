import pytest
import respx
import httpx
from django.http import JsonResponse
from api.services.real import RealNominativeQuery, RealGISNQuery
import os

# Set env vars required by headers
os.environ['USER_AGENT'] = 'test-agent'
os.environ['REFERRER'] = 'http://test-referrer'

def nominative_response_example():
    return [{
        'place_id': 194616086,
        'licence': 'Data © OpenStreetMap contributors',
        'osm_type': 'node',
        'osm_id': 2079017757,
        'lat': '32.0698820',
        'lon': '34.7735910',
        'class': 'place',
        'type': 'house',
        'place_rank': 30,
        'importance': 7.5e-05,
        'addresstype': 'place',
        'name': '',
        'display_name': '23, מרכז בעלי מלאכה, תל־אביב–יפו, ישראל',
        'boundingbox': ['32.0698320', '32.0699320', '34.7735410', '34.7736410']
    }]

def gisn_response_example():
    return {
        'features': [
        {'attributes': {'addresses': 'מרכז בעלי מלאכה 19א', 'building_stage': 'קיים היתר', 'sw_tama_38': 'כן'}},
        {'attributes': {'addresses': 'מרכז בעלי מלאכה 30', 'building_stage': 'בתהליך היתר', 'sw_tama_38': 'כן'}},
        {'attributes': {'addresses': 'העבודה 19', 'building_stage': 'בתהליך היתר', 'sw_tama_38': 'כן'}},
        {'attributes': {'addresses': 'מרכז בעלי מלאכה 25', 'building_stage': 'קיימת לפחות תעודת גמר אחת', 'sw_tama_38': 'לא'}},
        {'attributes': {'addresses': 'מרכז בעלי מלאכה 36א', 'building_stage': 'בתהליך היתר', 'sw_tama_38': 'כן'}},
        {'attributes': {'addresses': 'שינקין מנחם 32', 'building_stage': 'בתהליך היתר', 'sw_tama_38': 'לא'}},
        {'attributes': {'addresses': 'מרכז בעלי מלאכה 25', 'building_stage': 'קיימת לפחות תעודת גמר אחת', 'sw_tama_38': 'לא'}},
        ]
    }



# global setup for all tests
NOIMNATIVE_URL = "https://nominatim.openstreetmap.org/search"
GISN_QUERY_URL = "https://gisn.tel-aviv.gov.il/arcgis/rest/services/WM/IView2WM/MapServer/772/query"
nom_resp = nominative_response_example()
gisn_resp = gisn_response_example()


@pytest.mark.parametrize("street, house_number, mock_type, mock_data, expected", [
    # ✅ Happy path - valid response
    ("Herzl", 10, "success", nom_resp, ('34.7735910', '32.0698820')),

    # ❌ No results found
    ("FakeStreet", 9999, "success", [], JsonResponse({"error": "could not locate address"}, status=500)),

    # ❌ HTTP 500 error from Nominatim
    ("BuggyStreet", 1, "http_error", {"status_code": 500, "text": "Internal Server Error"},
     JsonResponse({"error": "Nominatim API error: 500 Internal Server Error"}, status=500)),

    # ❌ Malformed JSON (e.g. invalid syntax)
    ("CorruptStreet", 2, "invalid_json", None,
     JsonResponse({"error": "Invalid JSON response from Nominatim"}, status=500)),

    # ❌ Request timeout or network error
    ("TimeoutStreet", 3, "timeout", None,
     JsonResponse({"error": "Nominatim request failed"}, status=500)),
])
@respx.mock
def test_nominative_fetch_data_cases(street, house_number, mock_type, mock_data, expected):
    if mock_type == "success":
        respx.get(NOIMNATIVE_URL).mock(return_value=httpx.Response(200, json=mock_data))

    elif mock_type == "http_error":
        respx.get(NOIMNATIVE_URL).mock(
            return_value=httpx.Response(
                status_code=mock_data["status_code"],
                text=mock_data["text"]
            )
        )

    elif mock_type == "invalid_json":
        respx.get(NOIMNATIVE_URL).mock(
            return_value=httpx.Response(200, content=b"{ not valid json")
        )

    elif mock_type == "timeout":
        respx.get(NOIMNATIVE_URL).mock(side_effect=httpx.RequestError("Timeout"))

    query = RealNominativeQuery()
    result = query.fetch_data(street, house_number)

    if isinstance(expected, tuple):
        # Success case
        assert result == expected
    else:
        # Error case
        assert isinstance(result, JsonResponse)
        assert result.status_code == expected.status_code
        assert result.content == expected.content


@respx.mock
@pytest.mark.parametrize("coordinate, radius, mock_type, mock_data, expected", [
    # Happy path - returns features list
    ((34.7735910, 32.0698820), 100, "success", gisn_resp, gisn_resp["features"]),

    # Empty features list
    ((34.7735910, 32.0698820), 100, "success", {"features": []}, []),

    # HTTP 404 error
    ((34.7735910, 32.0698820), 100, "http_error", {"status_code": 404, "text": "Not Found"}, (404, b'{"error": "GISN API error: 404 Not Found"}')),

    # HTTP 500 error
    ((34.7735910, 32.0698820), 100, "http_error", {"status_code": 500, "text": "Internal Server Error"}, (500, b'{"error": "GISN API error: 500 Internal Server Error"}')),
])
def test_gisn_fetch_data_cases(coordinate, radius, mock_type, mock_data, expected):
    if mock_type == "success":
        respx.get(GISN_QUERY_URL).mock(
            return_value=httpx.Response(200, json=mock_data)
        )
    else:  # error case
        respx.get(GISN_QUERY_URL).mock(
            return_value=httpx.Response(
                status_code=mock_data["status_code"],
                text=mock_data["text"]
            )
        )

    query = RealGISNQuery()
    result = query.fetch_data(coordinate, radius)

    if isinstance(expected, tuple):
        # We expect a JsonResponse with specific content and status
        expected_status, expected_content = expected
        assert isinstance(result, JsonResponse), f"Expected JsonResponse, got {type(result)}"
        assert result.status_code == expected_status
        assert result.content == expected_content
    else:
        # We expect a list of features
        assert isinstance(result, list), f"Expected list, got {type(result)}"
        assert result == expected
