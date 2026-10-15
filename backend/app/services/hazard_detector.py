import numpy as np
import pandas as pd
from typing import List, Tuple, Dict, Any, Optional
from backend.app.models.requests import HazardType
from backend.app.models.responses import HazardEvent, AnnualMetric

class HazardDetector:
    """
    Climate Hazard Detection Engine.
    Implements ETCCDI (Expert Team on Climate Change Detection and Indices) standards
    for Heatwaves, Extreme Precipitation, and Droughts.
    """

    @classmethod
    def detect_hazards(
        cls,
        df: pd.DataFrame,
        hazard_type: HazardType = HazardType.HEATWAVE,
        percentile: float = 95.0,
        min_consecutive_days: int = 3,
        baseline_start_year: Optional[int] = None,
        baseline_end_year: Optional[int] = None,
        use_doy_window: bool = True
    ) -> Tuple[List[HazardEvent], List[AnnualMetric], float, pd.DataFrame]:
        """
        Detects events and computes annual aggregations.
        Returns:
            events: List of detected individual hazard events
            annual_metrics: Annual aggregation metrics
            threshold_scalar: Global or representative threshold value
            df_with_flags: Dataframe with boolean hazard indicator and threshold columns
        """
        work_df = df.copy()
        
        # 1. Define baseline slice for climatology
        if baseline_start_year and baseline_end_year:
            baseline_mask = (work_df["year"] >= baseline_start_year) & (work_df["year"] <= baseline_end_year)
            baseline_df = work_df[baseline_mask]
            if len(baseline_df) < 365:
                # If baseline slice is too small, fallback to entire series
                baseline_df = work_df
        else:
            baseline_df = work_df

        if hazard_type == HazardType.HEATWAVE:
            return cls._detect_heatwaves(
                work_df, baseline_df, percentile, min_consecutive_days, use_doy_window
            )
        elif hazard_type == HazardType.EXTREME_PRECIPITATION:
            return cls._detect_extreme_precipitation(
                work_df, baseline_df, percentile, min_consecutive_days
            )
        elif hazard_type == HazardType.DROUGHT:
            return cls._detect_droughts(
                work_df, min_consecutive_days=max(14, min_consecutive_days)
            )
        else:
            return cls._detect_heatwaves(
                work_df, baseline_df, percentile, min_consecutive_days, use_doy_window
            )

    @classmethod
    def _detect_heatwaves(
        cls,
        df: pd.DataFrame,
        baseline_df: pd.DataFrame,
        percentile: float,
        min_consecutive_days: int,
        use_doy_window: bool
    ) -> Tuple[List[HazardEvent], List[AnnualMetric], float, pd.DataFrame]:
        
        # Calculate threshold
        overall_threshold = float(np.percentile(baseline_df["t_max_imputed"].dropna(), percentile))
        
        if use_doy_window:
            # ETCCDI TX95p standard: 15-day centered moving window for each calendar day of year
            doy_thresholds = {}
            for doy in range(1, 367):
                # 15-day window centered on DOY (+- 7 days with wrap-around)
                doy_min = (doy - 7)
                doy_max = (doy + 7)
                if doy_min < 1:
                    mask = (baseline_df["day_of_year"] >= (365 + doy_min)) | (baseline_df["day_of_year"] <= doy_max)
                elif doy_max > 365:
                    mask = (baseline_df["day_of_year"] >= doy_min) | (baseline_df["day_of_year"] <= (doy_max - 365))
                else:
                    mask = (baseline_df["day_of_year"] >= doy_min) & (baseline_df["day_of_year"] <= doy_max)
                
                sub = baseline_df.loc[mask, "t_max_imputed"].dropna()
                if len(sub) > 0:
                    doy_thresholds[doy] = float(np.percentile(sub, percentile))
                else:
                    doy_thresholds[doy] = overall_threshold
                    
            df["threshold"] = df["day_of_year"].map(doy_thresholds).fillna(overall_threshold)
        else:
            df["threshold"] = overall_threshold

        # Exceedance condition: t_max >= threshold
        df["is_exceedance"] = df["t_max_imputed"] >= df["threshold"]
        
        # Consecutive run identification
        events, df["is_hazard"] = cls._find_consecutive_events(
            df=df,
            condition_col="is_exceedance",
            value_col="t_max_imputed",
            threshold_col="threshold",
            min_days=min_consecutive_days
        )
        
        # Annual aggregation
        annual_metrics = cls._aggregate_annual(df, events, value_col="t_max_imputed")
        
        return events, annual_metrics, overall_threshold, df

    @classmethod
    def _detect_extreme_precipitation(
        cls,
        df: pd.DataFrame,
        baseline_df: pd.DataFrame,
        percentile: float,
        min_consecutive_days: int
    ) -> Tuple[List[HazardEvent], List[AnnualMetric], float, pd.DataFrame]:
        
        # Filter wet days (> 1.0 mm) for percentile calculation (WMO standard R95p)
        wet_days = baseline_df.loc[baseline_df["precip_imputed"] >= 1.0, "precip_imputed"].dropna()
        if len(wet_days) > 10:
            threshold = float(np.percentile(wet_days, percentile))
        else:
            threshold = 50.0  # standard 50mm extreme rain threshold fallback
            
        df["threshold"] = threshold
        df["is_exceedance"] = df["precip_imputed"] >= threshold
        
        events, df["is_hazard"] = cls._find_consecutive_events(
            df=df,
            condition_col="is_exceedance",
            value_col="precip_imputed",
            threshold_col="threshold",
            min_days=max(1, min_consecutive_days)
        )
        
        annual_metrics = cls._aggregate_annual(df, events, value_col="precip_imputed")
        return events, annual_metrics, threshold, df

    @classmethod
    def _detect_droughts(
        cls,
        df: pd.DataFrame,
        min_consecutive_days: int = 14
    ) -> Tuple[List[HazardEvent], List[AnnualMetric], float, pd.DataFrame]:
        # Consecutive dry days (precip < 1.0 mm)
        df["threshold"] = 1.0
        df["is_exceedance"] = df["precip_imputed"] < 1.0
        
        events, df["is_hazard"] = cls._find_consecutive_events(
            df=df,
            condition_col="is_exceedance",
            value_col="precip_imputed",
            threshold_col="threshold",
            min_days=min_consecutive_days
        )
        
        annual_metrics = cls._aggregate_annual(df, events, value_col="precip_imputed")
        return events, annual_metrics, 1.0, df

    @staticmethod
    def _find_consecutive_events(
        df: pd.DataFrame,
        condition_col: str,
        value_col: str,
        threshold_col: str,
        min_days: int
    ) -> Tuple[List[HazardEvent], pd.Series]:
        """
        Run-length encoding to identify contiguous runs >= min_days.
        """
        is_cond = df[condition_col].astype(bool).values
        n = len(is_cond)
        
        hazard_mask = np.zeros(n, dtype=bool)
        events: List[HazardEvent] = []
        event_id = 1
        
        i = 0
        while i < n:
            if is_cond[i]:
                start_idx = i
                while i < n and is_cond[i]:
                    i += 1
                end_idx = i - 1
                duration = end_idx - start_idx + 1
                
                if duration >= min_days:
                    hazard_mask[start_idx:end_idx + 1] = True
                    event_slice = df.iloc[start_idx:end_idx + 1]
                    
                    values = event_slice[value_col].values
                    thresh = event_slice[threshold_col].values
                    excess = np.maximum(0, values - thresh).sum()
                    
                    event = HazardEvent(
                        id=event_id,
                        start_date=event_slice["date"].iloc[0].strftime("%Y-%m-%d"),
                        end_date=event_slice["date"].iloc[-1].strftime("%Y-%m-%d"),
                        duration_days=int(duration),
                        peak_value=round(float(np.max(values)), 2),
                        mean_value=round(float(np.mean(values)), 2),
                        cumulative_excess=round(float(excess), 2),
                        year=int(event_slice["year"].iloc[0])
                    )
                    events.append(event)
                    event_id += 1
            else:
                i += 1
                
        return events, pd.Series(hazard_mask, index=df.index)

    @staticmethod
    def _aggregate_annual(
        df: pd.DataFrame,
        events: List[HazardEvent],
        value_col: str
    ) -> List[AnnualMetric]:
        """
        Aggregates yearly event counts, hazard days, intensity, and temperature.
        """
        years = sorted(df["year"].unique())
        events_by_year: Dict[int, List[HazardEvent]] = {y: [] for y in years}
        for ev in events:
            if ev.year in events_by_year:
                events_by_year[ev.year].append(ev)
                
        annual_metrics: List[AnnualMetric] = []
        
        for y in years:
            sub = df[df["year"] == y]
            y_events = events_by_year[y]
            
            event_count = len(y_events)
            total_days = int(sub["is_hazard"].sum())
            longest = max([e.duration_days for e in y_events], default=0)
            max_peak = max([e.peak_value for e in y_events], default=None)
            cum_intensity = round(sum([e.cumulative_excess for e in y_events]), 2)
            mean_temp = round(float(sub[value_col].mean()), 2) if len(sub) > 0 else None
            
            metric = AnnualMetric(
                year=int(y),
                event_count=event_count,
                total_hazard_days=total_days,
                longest_event_days=longest,
                max_peak_value=max_peak,
                cumulative_intensity=cum_intensity,
                mean_annual_temp=mean_temp
            )
            annual_metrics.append(metric)
            
        return annual_metrics
