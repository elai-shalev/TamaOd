
import requests
import json
from django.http import JsonResponse
from urllib.parse import quote_plus, quote


# This function takes a string value "address", calls the GIS api with a geografic query
# and returns a JSON of relevant information 
# for now, this function return a static json 
def handel_address(street, house_number, radius):

 
  # Steps:
  # 1. Get coordinates of the address
  # 2. Query gisn.tel aviv for all the data in the radius of the coordinate
  # 3  Analyze the returned information
  # 4. Vizualize

  coordinates_list = get_coordinate(street=street, house_number=house_number)
  # {"0": ["32.062745", "34.770447"], "1": ["32.064218", "34.775547"]}
  x = json.loads(coordinates_list)
  get_all_places_in_radius(x["0"], radius)


  return {"street": street, "tama":"yes", "security": 0.9} # + get_coordinate(street, house_number) # returns a dictionary, views.py will take care of JSONResponse

def get_coordinate(street, house_number):
  # This function will contact Nominatim API to return thecoordinate point
  # of the street name, house number and Tel aviv as a default city

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
    
    # remove comments to actually query the API:
      # response = requests.get(url, params=params, headers=headers, timeout=5)
      # response.raise_for_status()
      # data = response.json()
    
    # comment this out if using API
    data = json.loads(get_mock_json())

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

def get_mock_json():
   # So we don't abuse the 3rd party api
   x = '''[{"place_id": "194986840", "licence": "Data © OpenStreetMap contributors, ODbL 1.0. http://osm.org/copyright", "osm_type": "node", "osm_id": 2078982447, "lat": "32.062745", "lon": "34.770447", "class": "place", "type": "house", "place_rank": 30, "importance": 7.500038147550191e-05, "addresstype": "place", "name": "", "display_name": "12, שדרות רוטשילד, לב תל-אביב, תל־אביב–יפו, נפת תל אביב, מחוז תל אביב, 6688218, ישראל", "boundingbox": ["32.0626950", "32.0627950", "34.7703970", "34.7704970"]}, {"place_id": 195264854, "licence": "Data © OpenStreetMap contributors, ODbL 1.0. http://osm.org/copyright", "osm_type": "node", "osm_id": 2078983104, "lat": "32.064218", "lon": "34.775547", "class": "place", "type": "house", "place_rank": 30, "importance": 7.500038147550191e-05, "addresstype": "place", "name": "", "display_name": "12א, שדרות רוטשילד, לב תל-אביב, תל־אביב–יפו, נפת תל אביב, מחוז תל אביב, 6578103, ישראל", "boundingbox": ["32.0641680", "32.0642680", "34.7754970", "34.7755970"]}]'''
   return x
   
def get_all_places_in_radius(coordinate, radius):
  url = "https://gisn.tel-aviv.gov.il/arcgis/rest/services/WM/IView2WM/MapServer/772/query?"

  print(coordinate)
  geometry = {
    "x": float(coordinate[1]),
    "y": float(coordinate[0])
  }

  out_fields = ",".join(["addresses", "building_stage","sw_tama_38"])

  params = {
    "where": "1=1",
    "text": "",
    "objectIds": "",
    "time": "",
    "timeRelation": "esriTimeRelationOverlaps",
    "geometry" : json.dumps(geometry),
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
    # Uncomment to actually Query the GIST API. 
    #response = requests.get(url, params=params, headers=headers)
    # print(response.url)  # Debugging: Check the final URL
    # print(response.json())  # Check the response content

    data = '''[{'attributes': {'addresses': 'שדרות רוטשילד 16', 'building_stage': 'קיים היתר', 'sw_tama_38': 'לא'}}, {'attributes': {'addresses': 'שדרות רוטשילד 16', 'building_stage': 'קיים היתר', 'sw_tama_38': 'לא'}}, {'attributes': {'addresses': 'שדרות רוטשילד 16', 'building_stage': 'קיים היתר', 'sw_tama_38': 'לא'}}, {'attributes': {'addresses': 'שדרות רוטשילד 16', 'building_stage': 'קיים היתר', 'sw_tama_38': 'לא'}}, {'attributes': {'addresses': 'הרצל 5, שדרות רוטשילד 9', 'building_stage': 'בבניה', 'sw_tama_38': 'לא'}}, {'attributes': {'addresses': 'הרצל 7, שדרות רוטשילד 10, שדרות רוטשילד 10א', 'building_stage': 'בתהליך היתר', 'sw_tama_38': 'לא'}}, {'attributes': {'addresses': 'הרצל 7, שדרות רוטשילד 10, שדרות רוטשילד 10א', 'building_stage': 'בתהליך היתר', 'sw_tama_38': 'לא'}}, {'attributes': {'addresses': 'הרצל 7, שדרות רוטשילד 10, שדרות רוטשילד 10א', 'building_stage': 'בתהליך היתר', 'sw_tama_38': 'לא'}}, {'attributes': {'addresses': 'הרצל 7, שדרות רוטשילד 10, שדרות רוטשילד 10א', 'building_stage': 'בתהליך היתר', 'sw_tama_38': 'לא'}}, {'attributes': {'addresses': 'הרצל 7, שדרות רוטשילד 10, שדרות רוטשילד 10א', 'building_stage': 'בתהליך היתר', 'sw_tama_38': 'לא'}}, {'attributes': {'addresses': 'הרצל 7, שדרות רוטשילד 10, שדרות רוטשילד 10א', 'building_stage': 'בתהליך היתר', 'sw_tama_38': 'לא'}}, {'attributes': {'addresses': 'הרצל 7, שדרות רוטשילד 10, שדרות רוטשילד 10א', 'building_stage': 'בתהליך היתר', 'sw_tama_38': 'לא'}}, {'attributes': {'addresses': 'הרצל 7, שדרות רוטשילד 10, שדרות רוטשילד 10א', 'building_stage': 'בתהליך היתר', 'sw_tama_38': 'לא'}}]
'''

    #response.raise_for_status()
    # data = response.json()
    # print(data['features'])
    # return data['features']
    print(data)
    return data
  except requests.RequestException as e:
      return JsonResponse({"error": "AAA"+str(e)}, status=500, safe=False)

