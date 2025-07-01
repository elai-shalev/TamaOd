import json
import os
from django.http import JsonResponse
import httpx
from api.services.base import BaseNominativeQuery, BaseGISNQuery
from httpx import HTTPStatusError, RequestError

class RealNominativeQuery(BaseNominativeQuery):

    def fetch_data(self, street: str, house_number: int):
      query_string = " ".join([street, str(house_number), "תל", "אביב"])
      url = "https://nominatim.openstreetmap.org/search?"
      params = {
        "q": query_string,
        "format": "json"
      }

      headers = {
        "User-Agent": os.getenv('USER_AGENT'),
        "Referer": os.getenv('REFERRER')
      }

      try:
          response = httpx.get(url, params=params, headers=headers, timeout=5)
          response.raise_for_status()
          data = response.json()
      except HTTPStatusError as e:
          return JsonResponse({"error": f"Nominatim API error: {e.response.status_code} {e.response.reason_phrase}"}, status=e.response.status_code)
      except RequestError:
          return JsonResponse({"error": "Nominatim request failed"}, status=500)
      except (ValueError, TypeError):
          return JsonResponse({"error": "Invalid JSON response from Nominatim"}, status=500)

      if not data:
          return JsonResponse({"error": "could not locate address"}, status=500)

      # collect all places
      places = {
          i: (place.get('lon'), place.get('lat'))
          for i, place in enumerate(data)
          if place.get('lat') and place.get('lon')
      }

      if not places:
          return JsonResponse({"error": "No valid lat/lon found in Nominatim results"}, status=500)

      return places[0]


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
            response = httpx.get(url, params=params, headers=headers)

            if response.status_code != 200:
                return JsonResponse(
                    {"error": f"GISN API error: {response.status_code} {response.text}"},
                    status=response.status_code
                )

            data = response.json()
            return data.get("features", [])

        except httpx.RequestError as e:
            return JsonResponse(
                {"error": f"GISN API request failed:  {e!s}"},
                status=503
            )
