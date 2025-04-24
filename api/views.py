from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from api.services import handle_address

@csrf_exempt
def analyze_address(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            street = data.get("street")
            house_number = data.get("houseNumber")
            radius = data.get("radius")

            if not street:
                return JsonResponse({"error": "Missing 'street' field"}, status=400)
            if not house_number:
                return JsonResponse({"error": "Missing 'house number' field"}, status=400)
            response_data = handle_address(street, house_number, radius)
            return JsonResponse(response_data, safe=False)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
    return JsonResponse({"error": "Only POST requests allowed"}, status=405)


@csrf_exempt
def get_streets(request):
    with open('api/data/streets.json', encoding='utf-8') as f:
        street_data = json.load(f)
    street_names = street_data.get("t_rechov_values", [])
    return JsonResponse({"streets": street_names})
