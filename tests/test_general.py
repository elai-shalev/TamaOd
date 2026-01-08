from api.services import risk_assessment

def test_risk_assessment():
    # Test with a mix of places
    input_data = [
        {"attributes": {"addresses": "Place A", "building_stage": "בבניה"}},
        {"attributes": {"addresses": "Place B", "building_stage": "קיים היתר"}},
        {"attributes": {"addresses": "Place C", "building_stage": "בבניה"}},
        {"attributes": {"addresses": "Place D", "building_stage": "לא ידוע"}},
    ]

    expected_output = [
        {"attributes": {"addresses": "Place A", "building_stage": "בבניה"}, "geometry": None},
        {"attributes": {"addresses": "Place C", "building_stage": "בבניה"}, "geometry": None},
    ]

    assert risk_assessment(input_data) == expected_output

def test_risk_assessment_empty():
    # Test empty input returns empty list
    assert risk_assessment([]) == []

def test_risk_assessment_no_dangerous():
    # Test input with no dangerous stages returns empty list
    input_data = [
        {"attributes": {"addresses": "Place A", "building_stage": "קיים היתר"}},
        {"attributes": {"addresses": "Place B", "building_stage": "לא ידוע"}},
    ]
    assert risk_assessment(input_data) == []
