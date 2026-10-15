import React from 'react';
import { Flame, Calendar, Clock, Thermometer, TrendingUp, Award, Layers } from 'lucide-react';

export default function SummaryCards({ summary, trends, hazardType, onOpenDetails }) {
  if (!summary) return null;

  const unit = hazardType === 'heatwave' ? '°C' : (hazardType === 'extreme_precipitation' ? 'mm' : 'days');
  const reg = trends?.event_frequency_regression;
  const mk = trends?.event_frequency_mann_kendall;

  const cards = [
    {
      id: 'events',
      title: 'Total Events Detected',
      value: summary.total_events,
      unitLabel: 'events',
      subtext: `Avg ${summary.annual_average_events} events/year`,
      icon: Flame,
      colorClass: 'accent-orange'
    },
    {
      id: 'days',
      title: 'Total Hazard Days',
      value: summary.total_days,
      unitLabel: 'days',
      subtext: `Longest single spell: ${summary.max_event_duration} days`,
      icon: Calendar,
      colorClass: 'accent-cyan'
    },
    {
      id: 'duration',
      title: 'Average Event Duration',
      value: summary.avg_duration_days,
      unitLabel: 'days',
      subtext: `Peak active year: ${summary.most_active_year}`,
      icon: Clock,
      colorClass: 'accent-amber'
    },
    {
      id: 'threshold',
      title: 'Percentile Threshold',
      value: `${summary.percentile_threshold_value}`,
      unitLabel: unit,
      subtext: `95th percentile climatological baseline`,
      icon: Thermometer,
      colorClass: 'accent-rose'
    },
    {
      id: 'trend',
      title: "Sen's Slope & Trend",
      value: `${mk?.sens_slope ? (mk.sens_slope > 0 ? '+' : '') + mk.sens_slope.toFixed(3) : '0'}/yr`,
      unitLabel: 'rate',
      subtext: `Tau: ${mk?.tau?.toFixed(2) || '0'}, p = ${mk?.p_value?.toFixed(3) || '0'}`,
      icon: TrendingUp,
      colorClass: 'accent-purple',
      clickable: true
    }
  ];

  return (
    <div className="summary-cards-grid">
      {cards.map((card) => {
        const IconComponent = card.icon;
        return (
          <div 
            key={card.id} 
            className={`kpi-card glass-panel ${card.clickable ? 'clickable' : ''}`}
            onClick={card.clickable ? onOpenDetails : undefined}
            title={card.clickable ? "Click to view full statistical test breakdown" : undefined}
          >
            <div className="kpi-card-header">
              <span className="kpi-card-title">{card.title}</span>
              <div className={`kpi-icon-wrap ${card.colorClass}`}>
                <IconComponent size={18} />
              </div>
            </div>

            <div className="kpi-value-row">
              <span className="kpi-value">{card.value}</span>
              <span className="kpi-unit">{card.unitLabel}</span>
            </div>

            <div className="kpi-subtext">
              {card.subtext}
              {card.clickable && <span className="kpi-more-hint"> • View Details →</span>}
            </div>
          </div>
        );
      })}
    </div>
  );
}
