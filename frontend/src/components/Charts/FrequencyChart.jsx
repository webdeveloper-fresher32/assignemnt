import React from 'react';
import { Bar } from 'react-chartjs-2';
import './chartSetup';
import { defaultChartOptions } from './chartSetup';
import { BarChart3, TrendingUp, Info } from 'lucide-react';

export default function FrequencyChart({ annualData, regression, mannKendall, hazardType }) {
  if (!annualData || annualData.length === 0) return null;

  const years = annualData.map((d) => d.year);
  const counts = annualData.map((d) => d.event_count);
  const rolling3yr = annualData.map((d) => d.rolling_3yr_count);
  const trendLine = annualData.map((d) => d.trend_line_count);

  const hazardLabel = hazardType === 'heatwave' ? 'Heatwaves' : (hazardType === 'extreme_precipitation' ? 'Rain Events' : 'Droughts');

  const chartData = {
    labels: years,
    datasets: [
      {
        type: 'bar',
        label: `Annual ${hazardLabel} Count`,
        data: counts,
        backgroundColor: 'rgba(249, 115, 22, 0.45)',
        borderColor: '#f97316',
        borderWidth: 1.5,
        borderRadius: 4,
        order: 3,
      },
      {
        type: 'line',
        label: '3-Year Rolling Moving Avg',
        data: rolling3yr,
        borderColor: '#38bdf8',
        backgroundColor: 'transparent',
        borderWidth: 2.5,
        tension: 0.35,
        pointRadius: 0,
        order: 2,
      },
      {
        type: 'line',
        label: `Linear Trend (${regression?.slope ? (regression.slope > 0 ? '+' : '') + regression.slope.toFixed(3) : ''}/yr)`,
        data: trendLine,
        borderColor: '#ec4899',
        borderWidth: 2,
        borderDash: [5, 5],
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
          <BarChart3 size={18} className="text-orange" />
          <h3 className="chart-title">Hazard Frequency Trend (Annual Events)</h3>
        </div>
        <div className="chart-stat-chip">
          <TrendingUp size={14} />
          <span>Slope: {regression?.slope ? (regression.slope > 0 ? '+' : '') + regression.slope.toFixed(4) : '0'}/yr</span>
          <span className="chip-p">R² = {regression?.r_squared || '0'}</span>
        </div>
      </div>

      <div className="chart-canvas-container">
        <Bar data={chartData} options={defaultChartOptions} />
      </div>

      <div className="chart-footnote">
        <Info size={12} />
        <span>
          Shows raw event counts per year, smoothed 3-year moving average, and OLS regression line (p = {regression?.p_value?.toFixed(4)}).
        </span>
      </div>
    </div>
  );
}
