import React from 'react';
import { Bar } from 'react-chartjs-2';
import './chartSetup';
import { defaultChartOptions } from './chartSetup';
import { CalendarDays, TrendingUp, Info } from 'lucide-react';

export default function DurationChart({ annualData, regression, mannKendall }) {
  if (!annualData || annualData.length === 0) return null;

  const years = annualData.map((d) => d.year);
  const totalDays = annualData.map((d) => d.total_hazard_days);
  const longestSpells = annualData.map((d) => d.longest_event_days);
  const trendDays = annualData.map((d) => d.trend_line_days);

  const chartData = {
    labels: years,
    datasets: [
      {
        type: 'bar',
        label: 'Total Hazard Days',
        data: totalDays,
        backgroundColor: 'rgba(56, 189, 248, 0.4)',
        borderColor: '#0284c7',
        borderWidth: 1.5,
        borderRadius: 4,
        order: 3,
      },
      {
        type: 'line',
        label: 'Longest Single Spell (Days)',
        data: longestSpells,
        borderColor: '#fbbf24',
        backgroundColor: 'rgba(251, 191, 36, 0.1)',
        borderWidth: 2,
        tension: 0.3,
        pointRadius: 2,
        order: 2,
      },
      {
        type: 'line',
        label: `Trend Line (${regression?.slope ? (regression.slope > 0 ? '+' : '') + regression.slope.toFixed(2) : ''} days/yr)`,
        data: trendDays,
        borderColor: '#a855f7',
        borderWidth: 2,
        borderDash: [4, 4],
        pointRadius: 0,
        fill: false,
        order: 1,
      },
    ],
  };

  return (
    <div className="chart-card glass-panel">
      <div className="chart-card-header">
        <div className="chart-title-wrap">
          <CalendarDays size={18} className="text-cyan" />
          <h3 className="chart-title">Hazard Duration & Persistence (Days/Year)</h3>
        </div>
        <div className="chart-stat-chip">
          <TrendingUp size={14} />
          <span>Sen's Slope: {mannKendall?.sens_slope ? (mannKendall.sens_slope > 0 ? '+' : '') + mannKendall.sens_slope.toFixed(3) : '0'} d/yr</span>
        </div>
      </div>

      <div className="chart-canvas-container">
        <Bar data={chartData} options={defaultChartOptions} />
      </div>

      <div className="chart-footnote">
        <Info size={12} />
        <span>
          Measures the total days per year that meet the hazard criteria and tracks the maximum single event duration.
        </span>
      </div>
    </div>
  );
}
