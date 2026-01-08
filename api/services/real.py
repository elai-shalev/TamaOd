import json
import os
import httpx
from api.services.base import (
    BaseNominativeQuery,
    BaseGISNQuery,
    DataRetrievalError,
)
from httpx import HTTPStatusError, RequestError


class RealNominativeQuery(BaseNominativeQuery):

    def fetch_data(
        self, street: str, house_number: int
    ) -> tuple[float, float]:
        query_string = " ".join([street, str(house_number), "תל", "אביב"])
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            "q": query_string,
            "format": "json",
        }

        # Nominatim requires a User-Agent header (usage policy)
        # Set defaults if not provided
        user_agent = os.getenv(
            'USER_AGENT',
            'TamaOd/1.0 (https://github.com/elai-shalev/tamaod)'
        )
        referer = os.getenv('REFERRER', 'https://tamaod.local')

        # Build headers dict, only including non-None values
        headers = {}
        if user_agent:
            headers["User-Agent"] = user_agent
        if referer:
            headers["Referer"] = referer

        try:
            response = httpx.get(
                url,
                params=params,
                headers=headers,
                timeout=5,
            )
            response.raise_for_status()
            data = response.json()
        except HTTPStatusError as e:
            raise DataRetrievalError(
                (
                    f"Nominatim API error: {e.response.status_code} "
                    f"{e.response.reason_phrase}"
                ),
                status_code=e.response.status_code,
            ) from e
        except RequestError as e:
            raise DataRetrievalError(
                "Nominatim request failed",
                status_code=500,
            ) from e
        except (ValueError, TypeError) as e:
            raise DataRetrievalError(
                "Invalid JSON response from Nominatim",
                status_code=500,
            ) from e

        if not data:
            raise DataRetrievalError(
                "could not locate address",
                status_code=500,
            )

        # collect all places
        places = {
            i: (place.get('lon'), place.get('lat'))
            for i, place in enumerate(data)
            if place.get('lat') and place.get('lon')
        }

        if not places:
            raise DataRetrievalError(
                "No valid lat/lon found in Nominatim results",
                status_code=500,
            )

        # Get first available coordinates and convert to float
        lon, lat = next(iter(places.values()))
        return (float(lon), float(lat))


class RealGISNQuery(BaseGISNQuery):
    """Real API implementation."""

    def fetch_data(
        self, coordinate, radius: int
    ):

        url = (
            "https://gisn.tel-aviv.gov.il/arcgis/rest/services/WM/IView2WM/MapServer/772/query"
        )

        geometry = {
            "x": float(coordinate[0]),
            "y": float(coordinate[1]),
        }

        out_fields = ",".join(["addresses", "building_stage", "sw_tama_38"])

        # Note: inSR and outSR use EPSG:4326 (WGS84), the standard projection
        # used by OpenStreetMap.
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
            "returnGeometry": "true",
            "returnTrueCurves": "false",
            "maxAllowableOffset": "",
            "geometryPrecision": "",
            "outSR": "4326",
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
                raise Exception(
                    f"GISN API error: {response.status_code} {response.text}"
                )

            data = response.json()
            return data.get("features", [])

        except httpx.RequestError as e:
            raise Exception(
                f"GISN API request failed: {e!s}"
            ) from e
        except (ValueError, TypeError) as e:
            raise Exception(
                f"Invalid JSON response from GISN API: {e!s}"
            ) from e
