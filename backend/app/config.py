import os
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "Climate Hazard Trend Analyzer"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*"
    ]
    
    # Rate Limiting
    RATE_LIMIT_DEFAULT: str = "60/minute"
    RATE_LIMIT_ANALYZE: str = "20/minute"
    
    # Cache settings
    CACHE_DIR: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".data")
    CACHE_DB_FILE: str = "nosql_cache.json"
    CACHE_TTL_DAYS: int = 14  # Historical data doesn't change
    
    # MongoDB (optional, if provided)
    MONGODB_URI: str = os.getenv("MONGODB_URI", "")
    MONGODB_DB_NAME: str = "climate_analyzer"
    
    # Open-Meteo external API
    OPEN_METEO_ARCHIVE_URL: str = "https://archive-api.open-meteo.com/v1/archive"
    OPEN_METEO_GEOCODING_URL: str = "https://geocoding-api.open-meteo.com/v1/search"
    EXTERNAL_API_TIMEOUT_SECONDS: float = 20.0
    EXTERNAL_API_MAX_RETRIES: int = 3
    
    # Climatology defaults
    DEFAULT_BASELINE_START_YEAR: int = 1981
    DEFAULT_BASELINE_END_YEAR: int = 2010

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore"
    }

settings = Settings()
