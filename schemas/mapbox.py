from pydantic import BaseModel


class PlaceSearchResponse(BaseModel):
    mapbox_id: str
    name: str