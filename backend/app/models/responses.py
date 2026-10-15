from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class HazardEvent(BaseModel):
    id: int
    start_date: str
    end_date: str
    duration_days: int
    peak_value: float
    mean_value: float
    cumulative_excess: float
    year: int

class AnnualMetric(BaseModel):
    year: int
    event_count: int
    total_hazard_days: int
    longest_event_days: int
    max_peak_value: Optional[float] = None
    cumulative_intensity: float
    mean_annual_temp: Optional[float] = None
    rolling_3yr_count: Optional[float] = None
    rolling_5yr_count: Optional[float] = None
    rolling_3yr_days: Optional[float] = None
    rolling_5yr_days: Optional[float] = None
    trend_line_count: Optional[float] = None
    trend_line_days: Optional[float] = None

class RegressionStats(BaseModel):
    slope: float
    intercept: float
    r_squared: float
    p_value: float
    std_err: float
    percentage_change: float

class MannKendallStats(BaseModel):
    trend: str = Field(..., description="'increasing', 'decreasing', or 'no trend'")
    p_value: float
    z_score: float
    tau: float
    sens_slope: float
    is_significant: bool

class TrendStatistics(BaseModel):
    event_frequency_regression: RegressionStats
    hazard_days_regression: RegressionStats
    event_frequency_mann_kendall: MannKendallStats
    hazard_days_mann_kendall: MannKendallStats

class DataQualityReport(BaseModel):
    total_days: int
    valid_days: int
    missing_days: int
    missing_percentage: float
    outliers_detected: int
    units: Dict[str, str]
    data_source: str
    imputation_applied: bool

class SummaryInsights(BaseModel):
    headline: str
    total_events: int
    total_days: int
    avg_duration_days: float
    max_event_duration: int
    warmest_year: int
    most_active_year: int
    annual_average_events: float
    percentile_threshold_value: float
    trend_direction: str
    statistical_confidence: str
    scientific_caveat: str

class DailySeriesPoint(BaseModel):
    date: str
    value: float
    threshold: float
    is_hazard: bool

class AnalysisResponse(BaseModel):
    query_params: Dict[str, Any]
    summary: SummaryInsights
    trends: TrendStatistics
    annual_data: List[AnnualMetric]
    events: List[HazardEvent]
    daily_timeline: List[DailySeriesPoint]
    data_quality: DataQualityReport
    cached: bool
    cached_at: Optional[str] = None
    execution_time_ms: float

class GeocodedLocation(BaseModel):
    id: int
    name: str
    latitude: float
    longitude: float
    elevation: Optional[float] = None
    country: Optional[str] = None
    country_code: Optional[str] = None
    admin1: Optional[str] = None
    timezone: Optional[str] = None
