from typing import Any
import httpx

MAPBOX_GEOCODING_URL = "https://api.mapbox.com/geocoding/v5/mapbox.places"


async def search_places_in_india(
    query: str,
    limit: int = 5,
    access_token: str = ""
) -> list[dict[str, Any]]:
    """
    Searches Mapbox for places in India and returns simplified place dictionaries.
    """
    params = {
        "access_token": access_token,
        "country": "in",
        "types": "poi,place",
        "limit": limit
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{MAPBOX_GEOCODING_URL}/{query}.json",
            params=params
        )

        if response.status_code != 200:
            return []

        data = response.json()
        results = []

        for feature in data.get("features", []):
            results.append({
                "mapbox_id": feature.get("id"),
                "name": feature.get("text")
            })

        return results