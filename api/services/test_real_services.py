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

@pytest.mark.parametrize("street, house_number, mock_data, expected", [
    # Happy path only
    ("Herzl", 10, nom_resp, ('34.7735910', '32.0698820')),
    ("FakeStreet", 9999, [], JsonResponse({"error": "could not locate address"}, status=500)),
])
@respx.mock
def test_nominative_fetch_data_cases(street, house_number, mock_data, expected):
    """Tests RealNominativeQuery.fetch_data for happy scenario only."""
    
    respx.get(NOIMNATIVE_URL).mock(
        return_value=httpx.Response(200, json=mock_data)
    )

    query = RealNominativeQuery()
    result = query.fetch_data(street, house_number)

    if isinstance(expected, tuple):
        # Success: should return (lon, lat)
        assert result == expected
    else:
        # Error: should return JsonResponse
        assert isinstance(result, JsonResponse)
        assert result.status_code == expected.status_code
        assert result.content == expected.content


@pytest.mark.parametrize("coordinate, radius, mock_data, expected", [
    # Happy path - returns features list
    ((34.7735910, 32.0698820), 100, gisn_resp, gisn_resp["features"]),

    # Empty features list
    ((34.7735910, 32.0698820), 100, {"features": []}, []),
])
@respx.mock
def test_gisn_fetch_data_cases(coordinate, radius, mock_data, expected):
    
    respx.get(GISN_QUERY_URL).mock(
        return_value=httpx.Response(200, json=mock_data)
    )
    # Optionally add error case later

    query = RealGISNQuery()
    result = query.fetch_data(coordinate, radius)

    # Basic type check
    assert isinstance(result, list), f"Result should be a list but got {type(result)}"

    assert len(result) == len(expected), f"Expected {len(expected)} features but got {len(result)}"
    for feature in result:
        assert "attributes" in feature, "Each feature should contain 'attributes' key"