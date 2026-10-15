from pydantic import BaseModel, Field, model_validator
from enum import Enum
from typing import Optional

class HazardType(str, Enum):
    HEATWAVE = "heatwave"
    EXTREME_PRECIPITATION = "extreme_precipitation"
    DROUGHT = "drought"

class AnalysisRequest(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude between -90 and 90 degrees")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Longitude between -180 and 180 degrees")
    region_name: Optional[str] = Field("Selected Region", max_length=150, description="Human-readable location or city name")
    hazard_type: HazardType = Field(HazardType.HEATWAVE, description="Climate hazard type to analyze")
    start_year: int = Field(1990, ge=1950, le=2025, description="Start year of the study period (e.g. 1990)")
    end_year: int = Field(2023, ge=1950, le=2025, description="End year of the study period (e.g. 2023)")
    
    # Domain-specific parameters
    threshold_percentile: float = Field(95.0, ge=75.0, le=99.9, description="Percentile threshold for hazard definition (e.g. 95th percentile)")
    min_consecutive_days: int = Field(3, ge=1, le=30, description="Minimum consecutive days required to count as an event (e.g. 3)")
    
    # Climatology baseline definition
    baseline_start_year: Optional[int] = Field(None, ge=1950, le=2025, description="Climatological baseline start year (default: entire period or 1981)")
    baseline_end_year: Optional[int] = Field(None, ge=1950, le=2025, description="Climatological baseline end year (default: entire period or 2010)")
    use_doy_window: bool = Field(True, description="Use day-of-year rolling window (ETCCDI standard) for seasonal threshold")
    
    # Cache control
    force_refresh: bool = Field(False, description="Bypass cache and force fresh data fetch and calculation")

    @model_validator(mode="after")
    def validate_year_range(self):
        if self.start_year > self.end_year:
            raise ValueError(f"Start year ({self.start_year}) cannot be greater than end year ({self.end_year})")
        if self.end_year - self.start_year < 2:
            raise ValueError("Time range must span at least 3 years to compute meaningful statistical trends.")
        if self.baseline_start_year and self.baseline_end_year:
            if self.baseline_start_year > self.baseline_end_year:
                raise ValueError("Baseline start year cannot be greater than baseline end year.")
        return self

class GeocodeQuery(BaseModel):
    query: str = Field(..., min_length=2, max_length=100, description="City, state, or location name to search")
