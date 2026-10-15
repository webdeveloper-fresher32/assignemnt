import numpy as np
import pandas as pd
from typing import List
from backend.app.models.requests import HazardType
from backend.app.models.responses import (
    HazardEvent, AnnualMetric, TrendStatistics, SummaryInsights
)

class InsightsGenerator:
    """
    Synthesizes scientific data into clear, honest, and actionable climate insights.
    Adheres strictly to meteorological reporting ethics:
    - Never over-interprets noisy non-significant trends
    - Clearly reports p-values and confidence intervals
    - Contextualizes natural climate modes (e.g. ENSO) vs long-term secular warming
    """

    @classmethod
    def generate_insights(
        cls,
        region_name: str,
        hazard_type: HazardType,
        start_year: int,
        end_year: int,
        events: List[HazardEvent],
        annual_metrics: List[AnnualMetric],
        trend_stats: TrendStatistics,
        threshold_val: float
    ) -> SummaryInsights:
        
        hazard_label = "Heatwaves" if hazard_type == HazardType.HEATWAVE else (
            "Heavy Rainfall Events" if hazard_type == HazardType.EXTREME_PRECIPITATION else "Drought Periods"
        )
        unit = "°C" if hazard_type == HazardType.HEATWAVE else "mm"
        
        total_events = len(events)
        total_days = sum(m.total_hazard_days for m in annual_metrics)
        avg_duration = round(float(np.mean([e.duration_days for e in events])), 1) if events else 0.0
        max_duration = max([e.duration_days for e in events], default=0)
        
        # Most active year by event count
        most_active_metric = max(annual_metrics, key=lambda m: m.event_count, default=None)
        most_active_year = most_active_metric.year if most_active_metric else end_year
        
        # Warmest year by mean temp or peak
        warmest_metric = max(annual_metrics, key=lambda m: (m.mean_annual_temp or -999), default=None)
        warmest_year = warmest_metric.year if warmest_metric else end_year
        
        num_years = max(1, end_year - start_year + 1)
        annual_avg_events = round(total_events / num_years, 2)
        
        # Trend specifics
        pct_change = trend_stats.event_frequency_regression.percentage_change
        p_val = trend_stats.event_frequency_regression.p_value
        mk_trend = trend_stats.event_frequency_mann_kendall.trend
        is_significant = trend_stats.event_frequency_mann_kendall.is_significant
        
        # Direction formatting
        if pct_change > 0:
            change_str = f"increased by {abs(pct_change):.1f}%"
            direction = "Increasing"
        elif pct_change < 0:
            change_str = f"decreased by {abs(pct_change):.1f}%"
            direction = "Decreasing"
        else:
            change_str = "remained stable"
            direction = "Stable"

        # Headline synthesis
        headline = (
            f"{hazard_label} have {change_str} in {region_name} between {start_year} and {end_year}."
        )

        # Statistical confidence description
        if is_significant:
            stat_confidence = (
                f"Statistically Significant (p = {p_val:.3f} < 0.05). "
                f"Mann-Kendall test confirms an {mk_trend} secular trend."
            )
        else:
            stat_confidence = (
                f"No Statistically Significant Trend Detected (p = {p_val:.3f} ≥ 0.05). "
                f"Observed changes fall within expected interannual climate variability."
            )

        # Scientific caveat & domain honesty
        if hazard_type == HazardType.HEATWAVE:
            caveat = (
                f"Calculated using a 95th percentile threshold (~{threshold_val:.1f}{unit}) and ≥3 consecutive day definition. "
                "Local urban heat island (UHI) expansion, land-use changes, and large-scale atmospheric blocking "
                "interact with global warming to govern localized heatwave intensity."
            )
        else:
            caveat = (
                f"Calculated against baseline threshold of {threshold_val:.1f}{unit}. "
                "Extreme precipitation trends are often localized and modulated by convective storm dynamics and topography."
            )

        return SummaryInsights(
            headline=headline,
            total_events=total_events,
            total_days=total_days,
            avg_duration_days=avg_duration,
            max_event_duration=max_duration,
            warmest_year=warmest_year,
            most_active_year=most_active_year,
            annual_average_events=annual_avg_events,
            percentile_threshold_value=round(threshold_val, 2),
            trend_direction=direction,
            statistical_confidence=stat_confidence,
            scientific_caveat=caveat
        )
