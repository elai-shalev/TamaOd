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


def convert_rings_to_leaflet_format(rings):
    return [
        # Assuming GISN directly returns [Lat, Lon] for outSR=4326
        [[lon, lat] for lat, lon in ring]  # Flip them here
        for ring in rings
    ]


def risk_assessment(dangerous_places):
    """Filter dangerous places, convert geometry, return relevant data."""
    dangerous_results = []
    dangerous_stage = ["בבניה"]

    for place in dangerous_places:
        attributes = place["attributes"]
        if attributes.get("building_stage") in dangerous_stage:
            geometry = place.get("geometry")
            if geometry and "rings" in geometry:
                # For real API data with geometry
                rings = geometry["rings"]
                converted_rings = convert_rings_to_leaflet_format(rings)
                dangerous_results.append({
                    "attributes": attributes,
                    "geometry": {
                        "rings": converted_rings
                    }
                })
            else:
                # For test data without geometry, return attributes
                dangerous_results.append(attributes)
    return dangerous_results
