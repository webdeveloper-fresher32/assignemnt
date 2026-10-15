import React from 'react';
import { Line } from 'react-chartjs-2';
import './chartSetup';
import { defaultChartOptions } from './chartSetup';
import { Flame, Thermometer, Info } from 'lucide-react';

export default function IntensityChart({ annualData, hazardType }) {
  if (!annualData || annualData.length === 0) return null;

  const years = annualData.map((d) => d.year);
  const intensities = annualData.map((d) => d.cumulative_intensity);
  const meanTemps = annualData.map((d) => d.mean_annual_temp);

  const unit = hazardType === 'heatwave' ? '°C-days' : 'mm';

  const chartData = {
    labels: years,
    datasets: [
      {
        type: 'line',
        label: `Cumulative Hazard Intensity (${unit})`,
        data: intensities,
        borderColor: '#f97316',
        backgroundColor: 'rgba(249, 115, 22, 0.15)',
        borderWidth: 2.5,
        fill: true,
        tension: 0.3,
        pointRadius: 3,
        pointHoverRadius: 6,
        yAxisID: 'y',
      },
      {
        type: 'line',
        label: 'Annual Mean Temp (°C)',
        data: meanTemps,
        borderColor: '#a78bfa',
        backgroundColor: 'transparent',
        borderWidth: 2,
        borderDash: [3, 3],
        pointRadius: 2,
        tension: 0.2,
        yAxisID: 'y1',
      },
    ],
  };

  const dualAxisOptions = {
    ...defaultChartOptions,
    scales: {
      ...defaultChartOptions.scales,
      y: {
        ...defaultChartOptions.scales.y,
        position: 'left',
        title: {
          display: true,
          text: `Cumulative Excess (${unit})`,
          color: '#94a3b8',
          font: { size: 10 },
        },
      },
      y1: {
        position: 'right',
        grid: {
          drawOnChartArea: false,
        },
        ticks: {
          color: '#a78bfa',
          font: { size: 10 },
        },
        title: {
          display: true,
          text: 'Mean Temp (°C)',
          color: '#a78bfa',
          font: { size: 10 },
        },
      },
    },
  };

  return (
    <div className="chart-card glass-panel">
      <div className="chart-card-header">
        <div className="chart-title-wrap">
          <Flame size={18} className="text-orange" />
          <h3 className="chart-title">Thermal Severity & Background Climate</h3>
        </div>
      </div>

      <div className="chart-canvas-container">
        <Line data={chartData} options={dualAxisOptions} />
      </div>

      <div className="chart-footnote">
        <Info size={12} />
        <span>
          Cumulative excess intensity integrates both duration and magnitude of temperature above the threshold.
        </span>
      </div>
    </div>
  );
}
