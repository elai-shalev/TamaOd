import requests
import json
from django.http import JsonResponse
from urllib.parse import quote_plus, quote
from django.apps import apps

from api.services.base import BaseAPIService

def get_api_services() -> dict:
    """Fetches the appropriate API services instance."""
    api_config = apps.get_app_config("api")
    return {
        "nominative_service": api_config.nominative_service,
        "gisn_service": api_config.gisn_service
    }

api_services = get_api_services()

# This function takes a string value "address", calls the GIS api with a geographic query
# and returns a JSON of relevant information
# For now, this function returns a static JSON
def handle_address(street, house_number, radius):
    coordinates_list = api_services["nominative_service"].fetch_data(street, house_number)
    coordinate_json = json.loads(coordinates_list)
    places = api_services["gisn_service"].fetch_data(coordinate_json["0"], radius)
    return places

# This function will recieve a list of addresses in the queried radius
# And will return a report of the 'dangerous' places   
def analyze_places(data):
   # example for data
  data = json.loads(data)
  print(data)
  dangerous_addresses = []
  dangerous_stage = ["בבניה"]

  # Iterate over each item in the list
  for item in data:
      attributes = item["attributes"]
      
      # Check if address is dangerous
      if attributes.get("building_stage") in dangerous_stage:
          dangerous_addresses.append(attributes)
  
  return dangerous_addresses
