from fastapi import APIRouter, Query, HTTPException
from typing import List
from backend.app.models.responses import GeocodedLocation
from backend.app.services.weather_client import weather_client

router = APIRouter()

@router.get("/search", response_model=List[GeocodedLocation])
async def search_locations(
    q: str = Query(..., min_length=2, max_length=100, description="City or region name to search")
):
    """
    Search global locations with coordinates, elevation, and country metadata.
    """
    raw_results = await weather_client.search_locations(q, count=8)
    
    locations = []
    for item in raw_results:
        locations.append(GeocodedLocation(
            id=item.get("id", 0),
            name=item.get("name", ""),
            latitude=item.get("latitude", 0.0),
            longitude=item.get("longitude", 0.0),
            elevation=item.get("elevation"),
            country=item.get("country"),
            country_code=item.get("country_code"),
            admin1=item.get("admin1"),
            timezone=item.get("timezone")
        ))
    return locations
