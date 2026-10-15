import React from 'react';
import { Line } from 'react-chartjs-2';
import './chartSetup';
import { defaultChartOptions } from './chartSetup';
import { Clock, Info, ShieldAlert } from 'lucide-react';

export default function DailyTimelineChart({ dailyTimeline, hazardType }) {
  if (!dailyTimeline || dailyTimeline.length === 0) return null;

  const dates = dailyTimeline.map((d) => d.date);
  const values = dailyTimeline.map((d) => d.value);
  const thresholds = dailyTimeline.map((d) => d.threshold);

  const unit = hazardType === 'heatwave' ? '°C' : 'mm';

  // Point styling: make hazard exceedance points glow red/orange
  const pointBgColors = dailyTimeline.map((d) => (d.is_hazard ? '#ef4444' : 'transparent'));
  const pointBorderColors = dailyTimeline.map((d) => (d.is_hazard ? '#ffffff' : 'transparent'));
  const pointRadii = dailyTimeline.map((d) => (d.is_hazard ? 3.5 : 0));

  const chartData = {
    labels: dates,
    datasets: [
      {
        label: `Recorded Max Temperature (${unit})`,
        data: values,
        borderColor: '#38bdf8',
        backgroundColor: 'rgba(56, 189, 248, 0.08)',
        borderWidth: 1.5,
        tension: 0.15,
        pointBackgroundColor: pointBgColors,
        pointBorderColor: pointBorderColors,
        pointRadius: pointRadii,
        pointHoverRadius: 6,
      },
      {
        label: `95th Percentile Threshold (${unit})`,
        data: thresholds,
        borderColor: '#ef4444',
        borderWidth: 1.8,
        borderDash: [4, 4],
        pointRadius: 0,
        fill: false,
      },
    ],
  };

  const timelineOptions = {
    ...defaultChartOptions,
    scales: {
      ...defaultChartOptions.scales,
      x: {
        ...defaultChartOptions.scales.x,
        ticks: {
          ...defaultChartOptions.scales.x.ticks,
          maxTicksLimit: 12,
        },
      },
      y: {
        ...defaultChartOptions.scales.y,
        title: {
          display: true,
          text: `Daily Value (${unit})`,
          color: '#94a3b8',
          font: { size: 10 },
        },
      },
    },
  };

  return (
    <div className="chart-card glass-panel timeline-card">
      <div className="chart-card-header">
        <div className="chart-title-wrap">
          <Clock size={18} className="text-orange" />
          <h3 className="chart-title">Daily Meteorological Timeline & Threshold Exceedance</h3>
        </div>
        <div className="chart-legend-indicator">
          <span className="indicator-dot red"></span>
          <span>Red markers = Active Heatwave Days</span>
        </div>
      </div>

      <div className="chart-canvas-container timeline-canvas">
        <Line data={chartData} options={timelineOptions} />
      </div>

      <div className="chart-footnote">
        <Info size={12} />
        <span>
          Visualizes actual daily values against the seasonal 95th percentile threshold for recent years. 
          Consecutive sequences above the red dashed line constitute detected heatwave events.
        </span>
      </div>
    </div>
  );
}
