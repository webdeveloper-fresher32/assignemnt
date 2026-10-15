import numpy as np
from scipy import stats
from typing import List, Tuple
from backend.app.models.responses import (
    AnnualMetric, TrendStatistics, RegressionStats, MannKendallStats
)

class TrendAnalyzer:
    """
    Scientific Trend Detection Engine.
    Implements:
    - 3-year and 5-year Rolling Moving Averages
    - Ordinary Least Squares (OLS) Linear Regression with p-values
    - Mann-Kendall Non-Parametric Trend Test
    - Sen's Slope Estimator (Theil-Sen robust estimator)
    """

    @classmethod
    def analyze_trends(cls, annual_metrics: List[AnnualMetric]) -> Tuple[TrendStatistics, List[AnnualMetric]]:
        if not annual_metrics or len(annual_metrics) < 3:
            raise ValueError("At least 3 years of data required for trend calculation.")

        years = np.array([m.year for m in annual_metrics], dtype=float)
        event_counts = np.array([m.event_count for m in annual_metrics], dtype=float)
        hazard_days = np.array([m.total_hazard_days for m in annual_metrics], dtype=float)
        
        # 1. Rolling Moving Averages
        cls._compute_rolling_averages(annual_metrics, event_counts, hazard_days)
        
        # 2. Linear Regression for Event Frequency
        reg_count, fitted_count = cls._linear_regression(years, event_counts)
        # Linear Regression for Hazard Days
        reg_days, fitted_days = cls._linear_regression(years, hazard_days)
        
        # Populate fitted trend line values in annual metrics
        for i, m in enumerate(annual_metrics):
            m.trend_line_count = round(float(fitted_count[i]), 3)
            m.trend_line_days = round(float(fitted_days[i]), 3)

        # 3. Mann-Kendall Test for Event Frequency
        mk_count = cls._mann_kendall_test(event_counts)
        # Mann-Kendall Test for Hazard Days
        mk_days = cls._mann_kendall_test(hazard_days)

        trend_stats = TrendStatistics(
            event_frequency_regression=reg_count,
            hazard_days_regression=reg_days,
            event_frequency_mann_kendall=mk_count,
            hazard_days_mann_kendall=mk_days
        )

        return trend_stats, annual_metrics

    @classmethod
    def _compute_rolling_averages(cls, metrics: List[AnnualMetric], counts: np.ndarray, days: np.ndarray):
        n = len(metrics)
        for i in range(n):
            # 3-year window centered/backward
            w3_start = max(0, i - 2)
            metrics[i].rolling_3yr_count = round(float(np.mean(counts[w3_start:i+1])), 2)
            metrics[i].rolling_3yr_days = round(float(np.mean(days[w3_start:i+1])), 2)

            # 5-year window
            w5_start = max(0, i - 4)
            metrics[i].rolling_5yr_count = round(float(np.mean(counts[w5_start:i+1])), 2)
            metrics[i].rolling_5yr_days = round(float(np.mean(days[w5_start:i+1])), 2)

    @classmethod
    def _linear_regression(cls, x: np.ndarray, y: np.ndarray) -> Tuple[RegressionStats, np.ndarray]:
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        fitted = intercept + slope * x

        # Honest percentage change calculation
        # Use early vs recent 5-year means to avoid division-by-zero on zero-event initial years
        n = len(y)
        early_window = y[:min(5, n)]
        recent_window = y[-min(5, n):]
        early_mean = np.mean(early_window)
        recent_mean = np.mean(recent_window)
        
        if early_mean > 0:
            pct_change = ((recent_mean - early_mean) / early_mean) * 100.0
        else:
            # Fallback to linear fitted values or absolute delta
            fitted_start = max(0.05, fitted[0])
            pct_change = ((fitted[-1] - fitted_start) / fitted_start) * 100.0

        stats_obj = RegressionStats(
            slope=round(float(slope), 4),
            intercept=round(float(intercept), 4),
            r_squared=round(float(r_value ** 2), 4),
            p_value=round(float(p_value), 5),
            std_err=round(float(std_err), 4),
            percentage_change=round(float(pct_change), 1)
        )
        return stats_obj, fitted

    @classmethod
    def _mann_kendall_test(cls, data: np.ndarray) -> MannKendallStats:
        """
        Mann-Kendall Non-Parametric Trend Test with tie handling & Sen's Slope.
        """
        n = len(data)
        if n < 3:
            return MannKendallStats(
                trend="no trend",
                p_value=1.0,
                z_score=0.0,
                tau=0.0,
                sens_slope=0.0,
                is_significant=False
            )

        # 1. Calculate S statistic
        s = 0
        slopes = []
        for k in range(n - 1):
            for j in range(k + 1, n):
                diff = data[j] - data[k]
                s += int(np.sign(diff))
                slopes.append(diff / (j - k))

        # 2. Sen's Slope (median of pairwise slopes)
        sens_slope = float(np.median(slopes)) if slopes else 0.0

        # 3. Variance of S with tie correction
        unique_vals, counts = np.unique(data, return_counts=True)
        tie_term = sum(t * (t - 1) * (2 * t + 5) for t in counts if t > 1)
        var_s = (n * (n - 1) * (2 * n + 5) - tie_term) / 18.0

        # 4. Standardized Test Statistic Z
        if var_s > 0:
            if s > 0:
                z = (s - 1) / np.sqrt(var_s)
            elif s < 0:
                z = (s + 1) / np.sqrt(var_s)
            else:
                z = 0.0
            # Two-tailed p-value
            p_value = 2.0 * (1.0 - stats.norm.cdf(abs(z)))
        else:
            z = 0.0
            p_value = 1.0

        # 5. Kendall's Tau rank correlation
        tau = s / (0.5 * n * (n - 1)) if n > 1 else 0.0

        # 6. Trend classification
        is_sig = p_value < 0.05
        if is_sig and s > 0:
            trend = "increasing"
        elif is_sig and s < 0:
            trend = "decreasing"
        else:
            trend = "no trend"

        return MannKendallStats(
            trend=trend,
            p_value=round(float(p_value), 5),
            z_score=round(float(z), 3),
            tau=round(float(tau), 4),
            sens_slope=round(float(sens_slope), 4),
            is_significant=is_sig
        )
