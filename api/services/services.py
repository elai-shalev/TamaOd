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

    # Check if Nominative service returned an error (JsonResponse)
    # Use type name check to avoid import issues
    if hasattr(address_coordinate, '__class__') and 'JsonResponse' in str(type(address_coordinate)):
        # Extract error message from JsonResponse
        try:
            error_data = address_coordinate.content.decode('utf-8')
            import json
            error_dict = json.loads(error_data)
            error_msg = error_dict.get('error', 'Unknown error from Nominatim service')
        except Exception:
            error_msg = 'Error from Nominatim service'
        raise Exception(f"Nominatim error: {error_msg}")

    # Verify coordinate is a tuple or list with 2 elements
    if not isinstance(address_coordinate, tuple | list) or len(address_coordinate) != 2:
        raise Exception(f"Invalid coordinate format from Nominatim: {address_coordinate}")

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
        # Handle both full place objects and attributes-only objects
        if isinstance(place, dict) and "attributes" in place:
            attributes = place["attributes"]
        else:
            # If place is already just attributes, use it directly
            attributes = place

        if attributes.get("building_stage") in dangerous_stage:
            geometry = place.get("geometry") if isinstance(place, dict) else None
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
                # For test data without geometry, return consistent structure
                # Create a simple point geometry so the frontend can display it
                dangerous_results.append({
                    "attributes": attributes,
                    "geometry": None  # No geometry available
                })
    return dangerous_results
