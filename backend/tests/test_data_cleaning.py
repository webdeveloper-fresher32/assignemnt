import pytest
import numpy as np
from backend.app.services.data_cleaner import DataCleaner

def test_data_cleaning_with_gaps_and_outliers():
    # Raw API response with missing date and a severe physical outlier
    raw_api_data = {
        "daily_units": {"temperature_2m_max": "°C", "precipitation_sum": "mm"},
        "daily": {
            "time": ["2020-01-01", "2020-01-02", "2020-01-04", "2020-01-05", "2020-01-06"],  # Missing 2020-01-03
            "temperature_2m_max": [25.0, 26.0, 28.0, 99.0, 29.0],  # 99.0 is an impossible outlier
            "temperature_2m_min": [15.0, 16.0, 17.0, 18.0, 18.0],
            "precipitation_sum": [0.0, 5.0, 0.0, -2.0, 10.0]  # negative precip
        }
    }
    
    cleaned_df, report = DataCleaner.clean_daily_weather(raw_api_data)
    
    # Check that 2020-01-03 was reindexed into the series (total 6 days)
    assert len(cleaned_df) == 6
    assert report.total_days == 6
    assert report.missing_days >= 1
    assert report.outliers_detected >= 1
    
    # Check that 99.0 was replaced and interpolated without exploding
    max_val = cleaned_df["t_max_imputed"].max()
    assert max_val < 65.0  # within realistic bounds
    
    # Check precipitation was clipped at 0
    assert (cleaned_df["precip"] >= 0).all()
