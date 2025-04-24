from api import app_state

def handle_address(street, house_number, radius):
    """
    Returns dangerous places near a given address.

    Uses Nominatim to get coordinates and GISN to find nearby places,
    then filters them through a risk assessment function.
    """
    nominative_service = app_state.get_nominative_service()
    gisn_service = app_state.get_gisn_service()

    address_coordinate = nominative_service.fetch_data(street, house_number)
    places_in_radius = gisn_service.fetch_data(address_coordinate, radius)
    return risk_assessment(places_in_radius)

def risk_assessment(dangerous_places):
    """Filter and return 'dangerous' places from the GISN data."""
    dangerous_addresses = []
    dangerous_stage = ["בבניה"]

    for place in dangerous_places:
        attributes = place["attributes"]
        if attributes.get("building_stage") in dangerous_stage:
            dangerous_addresses.append(attributes)

    return dangerous_addresses
