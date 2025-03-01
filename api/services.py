
# This function takes a string value "address", calls the GIS api with a geografic query
# and returns a JSON of relevant information 
# for now, this function return a static json 
def handel_address(street, house_number, radius):
 
  # Steps:
  # 1. Get coordinates of the address
  # 2. Query gisn.tel aviv for all the data in the radius of the coordinate
  # 3  Analyze the returned information
  # 4. Vizualize

  return {"street": street, "tama":"yes", "security": 0.9} # + get_coordinate(street, house_number) # returns a dictionary, views.py will take care of JSONResponse

def get_coordinate(street, house_number):
  # This function will contact Nominatim API to return thecoordinate point
  # of the street name, house number and Tel aviv as a default city
  return {"x":34.7818,"y":32.0853} 

