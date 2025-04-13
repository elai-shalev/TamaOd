import json
from api import app_state

def handle_address(street, house_number, radius):
    nominative_service = app_state.get_nominative_service()
    gisn_service = app_state.get_gisn_service()

    coordinates_list = nominative_service.fetch_data(street, house_number)
    coordinate_json = json.loads(coordinates_list)

    places = gisn_service.fetch_data(coordinate_json["0"], radius)
    return places


def analyze_places(data):
    """Filter and return 'dangerous' places from the GISN data."""
    data = json.loads(data)
    dangerous_addresses = []
    dangerous_stage = ["בבניה"]

    for item in data:
        attributes = item["attributes"]
        if attributes.get("building_stage") in dangerous_stage:
            dangerous_addresses.append(attributes)

    return dangerous_addresses
