import pytest
import numpy as np
import pandas as pd
from backend.app.models.requests import HazardType
from backend.app.services.hazard_detector import HazardDetector

def create_synthetic_temperature_series(num_years=5, base_temp=30.0, heatwave_in_year=2):
    """Creates a predictable daily synthetic time-series with an injected heatwave."""
    dates = pd.date_range("2010-01-01", periods=num_years * 365, freq="D")
    np.random.seed(42)
    # Seasonal cycle + random noise
    doy = dates.dayofyear.values
    t_max = base_temp + 10.0 * np.sin(2 * np.pi * doy / 365.0) + np.random.normal(0, 1.5, len(dates))
    
    df = pd.DataFrame({
        "date": dates,
        "t_max_imputed": t_max,
        "precip_imputed": np.zeros(len(dates)),
        "year": dates.year,
        "day_of_year": doy,
        "month": dates.month
    })
    
    # Inject a distinct 5-day extreme heatwave in the target year
    hw_start = pd.Timestamp(f"{2010 + heatwave_in_year}-06-10")
    hw_mask = (df["date"] >= hw_start) & (df["date"] < hw_start + pd.Timedelta(days=5))
    df.loc[hw_mask, "t_max_imputed"] = 48.0  # Well above the 95th percentile
    
    return df

def test_heatwave_detection_identifies_injected_event():
    df = create_synthetic_temperature_series(num_years=4, heatwave_in_year=2)
    events, annual, threshold, df_flags = HazardDetector.detect_hazards(
        df=df,
        hazard_type=HazardType.HEATWAVE,
        percentile=95.0,
        min_consecutive_days=3,
        use_doy_window=False
    )
    
    assert len(events) >= 1
    # Check that the injected 5-day event was caught
    target_events = [e for e in events if e.year == 2012 and e.duration_days >= 5]
    assert len(target_events) >= 1
    assert target_events[0].peak_value == 48.0
    assert target_events[0].cumulative_excess > 0

def test_min_consecutive_days_filter():
    """Events shorter than min_consecutive_days should not be classified as heatwaves."""
    df = create_synthetic_temperature_series(num_years=2)
    # Inject a 2-day spike
    df.loc[10:11, "t_max_imputed"] = 55.0
    
    events, _, _, _ = HazardDetector.detect_hazards(
        df=df,
        hazard_type=HazardType.HEATWAVE,
        percentile=95.0,
        min_consecutive_days=4, # requires 4 days
        use_doy_window=False
    )
    
    # None of the events should have duration < 4
    for ev in events:
        assert ev.duration_days >= 4
