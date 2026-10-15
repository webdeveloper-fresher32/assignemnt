import pytest
import numpy as np
from backend.app.models.responses import AnnualMetric
from backend.app.services.trend_analyzer import TrendAnalyzer

def test_mann_kendall_positive_trend():
    # Construct strictly increasing series
    metrics = [
        AnnualMetric(year=2000 + i, event_count=i + 1, total_hazard_days=(i+1)*3, longest_event_days=3, cumulative_intensity=10.0)
        for i in range(10)
    ]
    
    trend_stats, processed_metrics = TrendAnalyzer.analyze_trends(metrics)
    
    mk = trend_stats.event_frequency_mann_kendall
    assert mk.trend == "increasing"
    assert mk.is_significant is True
    assert mk.tau > 0.8
    assert mk.sens_slope > 0.0
    
    # Regression should have positive slope and R2 close to 1
    reg = trend_stats.event_frequency_regression
    assert reg.slope > 0
    assert reg.r_squared > 0.95
    assert reg.percentage_change > 0

def test_mann_kendall_no_trend():
    # Oscillating flat series
    counts = [2, 3, 2, 3, 2, 3, 2, 3, 2, 3]
    metrics = [
        AnnualMetric(year=2000 + i, event_count=counts[i], total_hazard_days=counts[i]*3, longest_event_days=3, cumulative_intensity=5.0)
        for i in range(len(counts))
    ]
    
    trend_stats, _ = TrendAnalyzer.analyze_trends(metrics)
    mk = trend_stats.event_frequency_mann_kendall
    assert mk.trend == "no trend"
    assert mk.is_significant is False
    assert mk.p_value > 0.05
