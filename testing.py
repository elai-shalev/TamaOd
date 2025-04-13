import json
import requests

def fetch_data(coordinate, radius: int):
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
      "outFields": "*",
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
      print("Status Code:", response.status_code)
      print("Response Body:", response.text)  # This will show the actual content!      return response
    except requests.RequestException as e:
      return {"error": str(e)}
    

fetch_data((32.062745, 34.770447), 30)