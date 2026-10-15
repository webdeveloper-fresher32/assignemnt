import numpy as np
import pandas as pd
import logging
from typing import Tuple, Dict, Any
from backend.app.models.responses import DataQualityReport

logger = logging.getLogger(__name__)

class DataCleaner:
    """
    Cleans raw meteorological time-series:
    - Verifies continuous daily date sequence (no hidden gaps)
    - Interpolates small missing data gaps (<= 3 days) using linear interpolation
    - Flags and handles physical and statistical outliers
    - Audits units and missingness
    """

    # Physical meteorological bounds
    MIN_REALISTIC_TEMP_C = -70.0
    MAX_REALISTIC_TEMP_C = 65.0
    MIN_REALISTIC_PRECIP_MM = 0.0
    MAX_REALISTIC_PRECIP_MM = 1200.0

    @classmethod
    def clean_daily_weather(cls, raw_api_data: Dict[str, Any]) -> Tuple[pd.DataFrame, DataQualityReport]:
        daily = raw_api_data.get("daily", {})
        daily_units = raw_api_data.get("daily_units", {})
        
        times = daily.get("time", [])
        t_max = daily.get("temperature_2m_max", [])
        t_min = daily.get("temperature_2m_min", [])
        precip = daily.get("precipitation_sum", [])
        
        if not times or not t_max:
            raise ValueError("No daily weather records received.")
            
        df = pd.DataFrame({
            "date": pd.to_datetime(times),
            "t_max": pd.to_numeric(t_max, errors="coerce"),
            "t_min": pd.to_numeric(t_min, errors="coerce") if t_min else np.nan,
            "precip": pd.to_numeric(precip, errors="coerce") if precip else 0.0
        })
        
        df = df.sort_values("date").drop_duplicates(subset=["date"]).reset_index(drop=True)
        
        # Ensure complete date index (identify any missing calendar days)
        full_idx = pd.date_range(start=df["date"].min(), end=df["date"].max(), freq="D")
        original_len = len(df)
        df = df.set_index("date").reindex(full_idx)
        df.index.name = "date"
        
        total_days = len(df)
        missing_count_initial = int(df["t_max"].isna().sum())
        
        # Outlier Detection
        outlier_count = 0
        # 1. Physical range check
        phys_outliers = (df["t_max"] < cls.MIN_REALISTIC_TEMP_C) | (df["t_max"] > cls.MAX_REALISTIC_TEMP_C)
        outlier_count += int(phys_outliers.sum())
        df.loc[phys_outliers, "t_max"] = np.nan
        
        # 2. Statistical rolling outlier check (4 standard deviations from 31-day centered rolling mean)
        rolling_mean = df["t_max"].rolling(window=31, center=True, min_periods=7).mean()
        rolling_std = df["t_max"].rolling(window=31, center=True, min_periods=7).std()
        stat_outliers = (df["t_max"] - rolling_mean).abs() > (4.0 * rolling_std.fillna(rolling_std.mean()))
        outlier_count += int(stat_outliers.sum())
        df.loc[stat_outliers, "t_max"] = np.nan
        
        # Handle precipitation negatives and missing values
        df["precip"] = df["precip"].fillna(0.0).clip(lower=0.0)
        df["precip_imputed"] = df["precip"]
        
        # Imputation: Linear interpolation for small missing gaps (up to 3 consecutive days)
        df["t_max_imputed"] = df["t_max"].interpolate(method="linear", limit=3)
        # For any remaining NaNs at the edges, forward-fill / backward-fill
        df["t_max_imputed"] = df["t_max_imputed"].ffill().bfill()
        
        valid_days = int(df["t_max_imputed"].notna().sum())
        missing_percentage = round((missing_count_initial / total_days) * 100, 2) if total_days > 0 else 0.0
        
        report = DataQualityReport(
            total_days=total_days,
            valid_days=valid_days,
            missing_days=missing_count_initial,
            missing_percentage=missing_percentage,
            outliers_detected=outlier_count,
            units={
                "temperature": daily_units.get("temperature_2m_max", "°C"),
                "precipitation": daily_units.get("precipitation_sum", "mm")
            },
            data_source="Open-Meteo Historical Weather (ERA5 / ERA5-Land Reanalysis)",
            imputation_applied=missing_count_initial > 0 or outlier_count > 0
        )
        
        df = df.reset_index()
        df["year"] = df["date"].dt.year
        df["day_of_year"] = df["date"].dt.dayofyear
        df["month"] = df["date"].dt.month
        
        return df, report
