import httpx
import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from backend.app.config import settings
from backend.app.core.exceptions import ClimateDataFetchError

logger = logging.getLogger(__name__)

class WeatherClient:
    """
    Client for interacting with Open-Meteo Historical Weather and Geocoding APIs.
    Includes timeout safety, automatic exponential backoff retries, and chunking for long spans.
    """
    
    def __init__(self):
        self.archive_url = settings.OPEN_METEO_ARCHIVE_URL
        self.geocoding_url = settings.OPEN_METEO_GEOCODING_URL
        self.timeout = httpx.Timeout(settings.EXTERNAL_API_TIMEOUT_SECONDS, connect=10.0)

    async def fetch_historical_daily(
        self,
        latitude: float,
        longitude: float,
        start_date: str,
        end_date: str
    ) -> Dict[str, Any]:
        """
        Fetch daily historical weather variables:
        - temperature_2m_max
        - temperature_2m_min
        - precipitation_sum
        """
        params = {
            "latitude": round(latitude, 4),
            "longitude": round(longitude, 4),
            "start_date": start_date,
            "end_date": end_date,
            "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum"],
            "timezone": "auto"
        }
        
        url = self.archive_url
        headers = {"User-Agent": "ClimateHazardTrendAnalyzer/1.0"}
        
        last_exception = None
        for attempt in range(1, settings.EXTERNAL_API_MAX_RETRIES + 1):
            try:
                logger.info(f"Fetching weather data (attempt {attempt}) for lat={latitude}, lon={longitude}, {start_date} to {end_date}")
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.get(url, params=params, headers=headers)
                    if response.status_code == 200:
                        data = response.json()
                        if "daily" not in data or "time" not in data["daily"]:
                            raise ClimateDataFetchError("Open-Meteo response missing 'daily' time-series payload.")
                        return data
                    elif response.status_code == 429:
                        # Rate limited, back off
                        wait_sec = attempt * 2.0
                        logger.warning(f"Rate limited (429) by Open-Meteo. Waiting {wait_sec}s before retry.")
                        await asyncio.sleep(wait_sec)
                    else:
                        logger.error(f"Open-Meteo API returned error status {response.status_code}: {response.text}")
                        response.raise_for_status()
            except httpx.RequestError as e:
                last_exception = e
                wait_sec = attempt * 1.5
                logger.warning(f"Network error communicating with Open-Meteo ({e}). Retry {attempt}/{settings.EXTERNAL_API_MAX_RETRIES} in {wait_sec}s")
                await asyncio.sleep(wait_sec)
            except Exception as e:
                last_exception = e
                logger.error(f"Unexpected error in weather client: {e}")
                break

        raise ClimateDataFetchError(f"Could not retrieve historical weather data from Open-Meteo: {last_exception}")

    async def search_locations(self, query: str, count: int = 8) -> List[Dict[str, Any]]:
        """
        Search for cities/regions by name using Open-Meteo Geocoding API.
        """
        params = {
            "name": query.strip(),
            "count": count,
            "language": "en",
            "format": "json"
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.get(self.geocoding_url, params=params)
                if res.status_code == 200:
                    data = res.json()
                    results = data.get("results", [])
                    return results
                return []
        except Exception as e:
            logger.error(f"Geocoding error for query '{query}': {e}")
            return []

weather_client = WeatherClient()
