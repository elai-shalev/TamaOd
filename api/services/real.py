import requests
import json
from django.http import JsonResponse
from api.services.base import BaseNominativeQuery, BaseGISNQuery

class RealNominativeQuery(BaseNominativeQuery):
    
    def fetch_data(self, street: str, house_number: int):
      query_string = " ".join([street, str(house_number), "תל", "אביב"])
      url = "https://nominatim.openstreetmap.org/search?"
      params = {
        "q": query_string,
        "format": "json"
      }

      headers = {
        "User-Agent": "TamaApp/1.0 (eshalev@redhat.com)",  # Identify your app + contact info
        "Referer": "https://github.com/elai-shalev/TamaOd"  # Optional but helps with credibility
      }

      try: 
        response = requests.get(url, params=params, headers=headers, timeout=5)
        
        response.raise_for_status()
        data = response.json()

       #[{'place_id': 195444241, 'licence': 'Data © OpenStreetMap contributors, ODbL 1.0. http://osm.org/copyright', 'osm_type': 'way', 'osm_id': 149384937, 'lat': '32.0834474', 'lon': '34.7816799', 'class': 'amenity', 'type': 'restaurant', 'place_rank': 30, 'importance': 7.500038147550191e-05, 'addresstype': 'amenity', 'name': 'אמורה מיו', 'display_name': 'אמורה מיו, 100, אבן גבירול, הצפון החדש - החלק הדרומי, הצפון החדש, תל־אביב–יפו, נפת תל אביב, מחוז תל אביב, 6296802, ישראל', 'boundingbox': ['32.0833959', '32.0835422', '34.7815499', '34.7818089']}, {'place_id': 195886935, 'licence': 'Data © OpenStreetMap contributors, ODbL 1.0. http://osm.org/copyright', 'osm_type': 'node', 'osm_id': 2078972513, 'lat': '32.0834730', 'lon': '34.7815920', 'class': 'place', 'type': 'house', 'place_rank': 30, 'importance': 7.500038147550191e-05, 'addresstype': 'place', 'name': '', 'display_name': '100, אבן גבירול, הצפון החדש - החלק הדרומי, הצפון החדש, תל־אביב–יפו, נפת תל אביב, מחוז תל אביב, 6296802, ישראל', 'boundingbox': ['32.0834230', '32.0835230', '34.7815420', '34.7816420']}]

            
        places = {}
        for i, place in enumerate(data):
            lat = place.get('lat')
            lon = place.get('lon')
            places[i] = (lon, lat)

        if len(places) == 0:
            return JsonResponse({"error": "could not locate address"}, status=500)
        return places[0]
      
      except requests.RequestException as e:
        return JsonResponse({"error": "AAA"+str(e)}, status=500, safe=False)

class RealGISNQuery(BaseGISNQuery):
    """Real API implementation."""
    
    def fetch_data(self, coordinate, radius: int):

        url = "https://gisn.tel-aviv.gov.il/arcgis/rest/services/WM/IView2WM/MapServer/772/query?"
        
        geometry = {
        "x": float(coordinate[0]),
        "y": float(coordinate[1]),
        }

        out_fields = ",".join(["addresses", "building_stage","sw_tama_38"])

        params = {
          "where": "1=1",
          "text": "",
          "objectIds": "",
          "time": "",
          "timeRelation": "esriTimeRelationOverlaps",
          "geometry": json.dumps(geometry),
          "geometryType": "esriGeometryPoint",
           "inSR": "4326",
          "spatialRel": "esriSpatialRelIntersects",
          "distance": str(radius),
          "units": "esriSRUnit_Meter",
          "relationParam": "",
          "outFields": out_fields,
          "returnGeometry": "false",
          "returnTrueCurves": "false",
          "maxAllowableOffset": "",
          "geometryPrecision": "",
          "outSR": "",
          "havingClause": "",
          "returnIdsOnly": "false",
          "returnCountOnly": "false",
          "orderByFields": "",
          "groupByFieldsForStatistics": "",
          "outStatistics": "",
          "returnZ": "false",
          "returnM": "false",
          "gdbVersion": "",
          "historicMoment": "",
          "returnDistinctValues": "false",
          "resultOffset": "",
          "resultRecordCount": "",
          "returnExtentOnly": "false",
          "sqlFormat": "none",
          "datumTransformation": "",
          "parameterValues": "",
          "rangeValues": "",
          "quantizationParameters": "",
          "featureEncoding": "esriDefault",
          "f": "pjson",
          }

        # Define headers
        headers = {
              "Accept": "application/json",
              "Accept-Language": "en-US,en;q=0.9",
        }

        try: 
          response = requests.get(url, params=params, headers=headers)
          data = response.json()
          features = data.get("features", [])
          return features
        except requests.RequestException as e:
          return JsonResponse({"error": str(e)}, status=500, safe=False)