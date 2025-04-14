import requests
import json
from django.http import JsonResponse
from api.services.base import BaseNominativeQuery, BaseGISNQuery

class RealNominativeQuery(BaseNominativeQuery):
    
    def fetch_data(self, street: str, house_number: int):
      query_string = " ".join([street, house_number, "תל", "אביב"])
      url = "https://nominatim.openstreetmap.org/search?"
      params = {
        "q": query_string,
        "format": "json"
      }

      headers = {
        "User-Agent": "TamaApp/1.0 (eshalev@redhat.com)",  # Identify your app + contact info
        "Referer": "https://github.com/ElaiShalevRH/TamaOd"  # Optional but helps with credibility
      }

      try: 
        response = requests.get(url, params=params, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()
            
        places = {}
        i=0
        for place in data:
          places[i] = (place.get('lat'),place.get('lon'))
          i += 1
    
        if len(places) == 0:
          return JsonResponse({"error": "could not locate address"}, status=500) 
        return json.dumps(places)
      
      except requests.RequestException as e:
        return JsonResponse({"error": "AAA"+str(e)}, status=500, safe=False)

class RealGISNQuery(BaseGISNQuery):
    """Real API implementation."""
    
    def fetch_data(self, coordinate, radius: int):
        print("HEYYYYY")

        url = "https://gisn.tel-aviv.gov.il/arcgis/rest/services/WM/IView2WM/MapServer/772/query?"
        
        geometry = {
        "x": float(coordinate[1]),
        "y": float(coordinate[0]),
        }
        print(geometry)

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