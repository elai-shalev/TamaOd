nominative_service = None
gisn_service = None

def set_services(nominative, gisn):
    global nominative_service, gisn_service
    nominative_service = nominative
    gisn_service = gisn

def get_nominative_service():
    return nominative_service

def get_gisn_service():
    return gisn_service
