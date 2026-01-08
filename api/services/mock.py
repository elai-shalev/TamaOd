import json
from api.services.base import BaseNominativeQuery, BaseGISNQuery


class MockNominativeQuery(BaseNominativeQuery):

    def fetch_data(
        self, street: str, house_number: int
    ) -> tuple[float, float]:
        # Mock data from Nominatim API response
        data = (
            '[{"place_id": "194986840", "licence": "Data © '
            'OpenStreetMap contributors, ODbL 1.0. '
            'http://osm.org/copyright", "osm_type": "node", '
            '"osm_id": 2078982447, "lat": "32.062745", '
            '"lon": "34.770447", "class": "place", "type": "house", '
            '"place_rank": 30, "importance": 7.500038147550191e-05, '
            '"addresstype": "place", "name": "", "display_name": '
            '"12, שדרות רוטשילד, לב תל-אביב, תל־אביב–יפו, '
            'נפת תל אביב, מחוז תל אביב, 6688218, ישראל", '
            '"boundingbox": ["32.0626950", "32.0627950", '
            '"34.7703970", "34.7704970"]}, {"place_id": 195264854, '
            '"licence": "Data © OpenStreetMap contributors, ODbL 1.0. '
            'http://osm.org/copyright", "osm_type": "node", '
            '"osm_id": 2078983104, "lat": "32.064218", '
            '"lon": "34.775547", "class": "place", "type": "house", '
            '"place_rank": 30, "importance": 7.500038147550191e-05, '
            '"addresstype": "place", "name": "", "display_name": '
            '"12א, שדרות רוטשילד, לב תל-אביב, תל־אביב–יפו, '
            'נפת תל אביב, מחוז תל אביב, 6578103, ישראל", '
            '"boundingbox": ["32.0641680", "32.0642680", '
            '"34.7754970", "34.7755970"]}]'
        )
        parsed = json.loads(data)
        lat = float(parsed[0]["lat"])
        lon = float(parsed[0]["lon"])
        return (lon, lat)


class MockGISNQuery(BaseGISNQuery):

    def fetch_data(self, coordinate, radius: int):
        # Mock data from GISN API response
        places_in_radius = (
            '[{"attributes": {"addresses": "שדרות רוטשילד 16", '
            '"building_stage": "קיים היתר", "sw_tama_38": "לא"}}, '
            '{"attributes": {"addresses": "שדרות רוטשילד 16", '
            '"building_stage": "קיים היתר", "sw_tama_38": "לא"}}, '
            '{"attributes": {"addresses": "שדרות רוטשילד 16", '
            '"building_stage": "קיים היתר", "sw_tama_38": "לא"}}, '
            '{"attributes": {"addresses": "שדרות רוטשילד 16", '
            '"building_stage": "קיים היתר", "sw_tama_38": "לא"}}, '
            '{"attributes": {"addresses": "הרצל 5, שדרות רוטשילד 9", '
            '"building_stage": "בבניה", "sw_tama_38": "לא"}}, '
            '{"attributes": {"addresses": "הרצל 7, שדרות רוטשילד 10, '
            'שדרות רוטשילד 10א", "building_stage": "בתהליך היתר", '
            '"sw_tama_38": "לא"}}, {"attributes": {"addresses": '
            '"הרצל 7, שדרות רוטשילד 10, שדרות רוטשילד 10א", '
            '"building_stage": "בתהליך היתר", "sw_tama_38": "לא"}}, '
            '{"attributes": {"addresses": "הרצל 7, שדרות רוטשילד 10, '
            'שדרות רוטשילד 10א", "building_stage": "בתהליך היתר", '
            '"sw_tama_38": "לא"}}, {"attributes": {"addresses": '
            '"הרצל 7, שדרות רוטשילד 10, שדרות רוטשילד 10א", '
            '"building_stage": "בתהליך היתר", "sw_tama_38": "לא"}}, '
            '{"attributes": {"addresses": "הרצל 7, שדרות רוטשילד 10, '
            'שדרות רוטשילד 10א", "building_stage": "בתהליך היתר", '
            '"sw_tama_38": "לא"}}, {"attributes": {"addresses": '
            '"הרצל 7, שדרות רוטשילד 10, שדרות רוטשילד 10א", '
            '"building_stage": "בתהליך היתר", "sw_tama_38": "לא"}}, '
            '{"attributes": {"addresses": "הרצל 7, שדרות רוטשילד 10, '
            'שדרות רוטשילד 10א", "building_stage": "בתהליך היתר", '
            '"sw_tama_38": "לא"}}, {"attributes": {"addresses": '
            '"הרצל 7, שדרות רוטשילד 10, שדרות רוטשילד 10א", '
            '"building_stage": "בתהליך היתר", "sw_tama_38": "לא"}}]'
        )
        return json.loads(places_in_radius)
