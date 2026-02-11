import pytest
import respx
import httpx
from api.services.real import RealNominativeQuery, RealGISNQuery
from api.services.base import DataRetrievalError
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
            {
                'attributes': {
                    'addresses': 'מרכז בעלי מלאכה 19א',
                    'building_stage': 'קיים היתר',
                    'sw_tama_38': 'כן'
                }
            },
            {
                'attributes': {
                    'addresses': 'מרכז בעלי מלאכה 30',
                    'building_stage': 'בתהליך היתר',
                    'sw_tama_38': 'כן'
                }
            },
            {
                'attributes': {
                    'addresses': 'העבודה 19',
                    'building_stage': 'בתהליך היתר',
                    'sw_tama_38': 'כן'
                }
            },
            {
                'attributes': {
                    'addresses': 'מרכז בעלי מלאכה 25',
                    'building_stage': 'קיימת לפחות תעודת גמר אחת',
                    'sw_tama_38': 'לא'
                }
            },
            {
                'attributes': {
                    'addresses': 'מרכז בעלי מלאכה 36א',
                    'building_stage': 'בתהליך היתר',
                    'sw_tama_38': 'כן'
                }
            },
            {
                'attributes': {
                    'addresses': 'שינקין מנחם 32',
                    'building_stage': 'בתהליך היתר',
                    'sw_tama_38': 'לא'
                }
            },
            {
                'attributes': {
                    'addresses': 'מרכז בעלי מלאכה 25',
                    'building_stage': 'קיימת לפחות תעודת גמר אחת',
                    'sw_tama_38': 'לא'
                }
            },
        ]
    }


# Global setup for all tests
NOIMNATIVE_URL = "https://nominatim.openstreetmap.org/search"
GISN_QUERY_URL = ("https://gisn.tel-aviv.gov.il/arcgis/rest/services/"
                  "WM/IView2WM/MapServer/772/query")


# Nominative Query Tests

@respx.mock
def test_nominative_fetch_data_success():
    """Test successful Nominatim query with valid response"""
    mock_response = nominative_response_example()
    respx.get(NOIMNATIVE_URL).mock(
        return_value=httpx.Response(200, json=mock_response)
    )

    query = RealNominativeQuery()
    result = query.fetch_data("Herzl", "10")

    # Should return coordinates as floats
    assert result == (34.7735910, 32.0698820)


@respx.mock
def test_nominative_fetch_data_no_results():
    """Test Nominatim query when no results are found"""
    respx.get(NOIMNATIVE_URL).mock(
        return_value=httpx.Response(200, json=[])
    )

    query = RealNominativeQuery()

    with pytest.raises(DataRetrievalError) as exc_info:
        query.fetch_data("FakeStreet", "9999")

    assert exc_info.value.status_code == 500
    assert "could not locate address" in str(exc_info.value)


@respx.mock
def test_nominative_fetch_data_http_error():
    """Test Nominatim query when HTTP error occurs"""
    respx.get(NOIMNATIVE_URL).mock(
        return_value=httpx.Response(
            status_code=500,
            text="Internal Server Error"
        )
    )

    query = RealNominativeQuery()

    with pytest.raises(DataRetrievalError) as exc_info:
        query.fetch_data("BuggyStreet", "1")

    assert exc_info.value.status_code == 500
    assert "Nominatim API error: 500 Internal Server Error" in str(
        exc_info.value
    )


@respx.mock
def test_nominative_fetch_data_invalid_json():
    """Test Nominatim query when response contains invalid JSON"""
    respx.get(NOIMNATIVE_URL).mock(
        return_value=httpx.Response(200, content=b"{ not valid json")
    )

    query = RealNominativeQuery()

    with pytest.raises(DataRetrievalError) as exc_info:
        query.fetch_data("CorruptStreet", "2")

    assert exc_info.value.status_code == 500
    assert "Invalid JSON response from Nominatim" in str(exc_info.value)


@respx.mock
def test_nominative_fetch_data_timeout():
    """Test Nominatim query when request times out"""
    respx.get(NOIMNATIVE_URL).mock(
        side_effect=httpx.RequestError("Timeout")
    )

    query = RealNominativeQuery()

    with pytest.raises(DataRetrievalError) as exc_info:
        query.fetch_data("TimeoutStreet", "3")

    assert exc_info.value.status_code == 500
    assert "Nominatim request failed" in str(exc_info.value)


@respx.mock
def test_nominative_no_coordinates_in_response():
    """Test when Nominatim returns data but no valid lat/lon coordinates"""
    mock_response = [{
        'place_id': 194616086,
        'display_name': 'Some Place',
        # Missing 'lat' and 'lon' fields
    }]

    respx.get(NOIMNATIVE_URL).mock(
        return_value=httpx.Response(200, json=mock_response)
    )

    query = RealNominativeQuery()

    with pytest.raises(DataRetrievalError) as exc_info:
        query.fetch_data("TestStreet", "123")

    assert exc_info.value.status_code == 500
    assert "No valid lat/lon found in Nominatim results" in str(
        exc_info.value
    )


@respx.mock
def test_nominative_partial_coordinates():
    """Test when some results have coordinates and others don't"""
    mock_response = [
        {
            'place_id': 1,
            'display_name': 'Place without coords',
            # No lat/lon
        },
        {
            'place_id': 2,
            'lat': '32.0698820',
            'lon': '34.7735910',
            'display_name': 'Place with coords',
        }
    ]

    respx.get(NOIMNATIVE_URL).mock(
        return_value=httpx.Response(200, json=mock_response)
    )

    query = RealNominativeQuery()
    result = query.fetch_data("TestStreet", "123")

    # Should return the first valid coordinate pair as floats
    assert result == (34.7735910, 32.0698820)


# GISN Query Tests

@respx.mock
def test_gisn_fetch_data_success():
    """Test successful GISN query with valid response"""
    mock_response = gisn_response_example()
    respx.get(GISN_QUERY_URL).mock(
        return_value=httpx.Response(200, json=mock_response)
    )

    query = RealGISNQuery()
    result = query.fetch_data((34.7735910, 32.0698820), 100)

    assert isinstance(result, list)
    assert result == mock_response["features"]


@respx.mock
def test_gisn_fetch_data_empty_features():
    """Test GISN query when response has empty features list"""
    mock_response = {"features": []}
    respx.get(GISN_QUERY_URL).mock(
        return_value=httpx.Response(200, json=mock_response)
    )

    query = RealGISNQuery()
    result = query.fetch_data((34.7735910, 32.0698820), 100)

    assert isinstance(result, list)
    assert result == []


@respx.mock
def test_gisn_fetch_data_http_404_error():
    """Test GISN query when HTTP 404 error occurs"""
    respx.get(GISN_QUERY_URL).mock(
        return_value=httpx.Response(
            status_code=404,
            text="Not Found"
        )
    )

    query = RealGISNQuery()

    with pytest.raises(Exception) as exc_info:
        query.fetch_data((34.7735910, 32.0698820), 100)

    assert "GISN API error: 404 Not Found" in str(exc_info.value)


@respx.mock
def test_gisn_fetch_data_http_500_error():
    """Test GISN query when HTTP 500 error occurs"""
    respx.get(GISN_QUERY_URL).mock(
        return_value=httpx.Response(
            status_code=500,
            text="Internal Server Error"
        )
    )

    query = RealGISNQuery()

    with pytest.raises(Exception) as exc_info:
        query.fetch_data((34.7735910, 32.0698820), 100)

    assert "GISN API error: 500 Internal Server Error" in str(exc_info.value)


@respx.mock
def test_gisn_fetch_data_request_error():
    """Test GISN query when network/request error occurs"""
    respx.get(GISN_QUERY_URL).mock(
        side_effect=httpx.RequestError("Timeout")
    )

    query = RealGISNQuery()

    with pytest.raises(Exception) as exc_info:
        query.fetch_data((34.7735910, 32.0698820), 100)

    assert "GISN API request failed: Timeout" in str(exc_info.value)


@respx.mock
def test_gisn_missing_features_key():
    """Test when GISN API returns 200 but missing 'features' key"""
    mock_response = {"some_other_key": "value"}  # Missing 'features' key

    respx.get(GISN_QUERY_URL).mock(
        return_value=httpx.Response(200, json=mock_response)
    )

    query = RealGISNQuery()
    result = query.fetch_data((34.7735910, 32.0698820), 100)

    # Should return empty list when 'features' key is missing
    assert isinstance(result, list)
    assert result == []
