import React, { useState } from 'react';
import { ListFilter, ArrowUpDown, Flame, Search, ChevronRight } from 'lucide-react';

export default function EventsTable({ events, hazardType }) {
  const [sortField, setSortField] = useState('duration_days');
  const [sortAsc, setSortAsc] = useState(false);
  const [searchFilter, setSearchFilter] = useState('');
  const [displayCount, setDisplayCount] = useState(10);

  if (!events || events.length === 0) return null;

  const unit = hazardType === 'heatwave' ? '°C' : 'mm';

  const handleSort = (field) => {
    if (sortField === field) {
      setSortAsc(!sortAsc);
    } else {
      setSortField(field);
      setSortAsc(false);
    }
  };

  const filtered = events.filter((ev) => {
    if (!searchFilter) return true;
    return (
      ev.start_date.includes(searchFilter) ||
      ev.end_date.includes(searchFilter) ||
      ev.year.toString().includes(searchFilter)
    );
  });

  const sorted = [...filtered].sort((a, b) => {
    const aVal = a[sortField];
    const bVal = b[sortField];
    if (aVal < bVal) return sortAsc ? -1 : 1;
    if (aVal > bVal) return sortAsc ? 1 : -1;
    return 0;
  });

  const visibleEvents = sorted.slice(0, displayCount);

  return (
    <div className="events-table-card glass-panel">
      <div className="table-card-header">
        <div className="table-title-wrap">
          <Flame size={18} className="text-orange" />
          <h3 className="table-title">Detected Climate Hazard Events ({events.length} Total)</h3>
        </div>

        <div className="table-actions">
          <div className="table-search-wrap">
            <Search size={14} className="table-search-icon" />
            <input
              type="text"
              placeholder="Filter by year (e.g. 2023)..."
              value={searchFilter}
              onChange={(e) => setSearchFilter(e.target.value)}
              className="table-search-input"
            />
          </div>
        </div>
      </div>

      <div className="table-responsive">
        <table className="events-data-table">
          <thead>
            <tr>
              <th onClick={() => handleSort('id')} className="cursor-pointer">
                <div className="th-content">
                  <span>#</span>
                  <ArrowUpDown size={12} />
                </div>
              </th>
              <th onClick={() => handleSort('start_date')} className="cursor-pointer">
                <div className="th-content">
                  <span>Start Date</span>
                  <ArrowUpDown size={12} />
                </div>
              </th>
              <th onClick={() => handleSort('end_date')} className="cursor-pointer">
                <div className="th-content">
                  <span>End Date</span>
                  <ArrowUpDown size={12} />
                </div>
              </th>
              <th onClick={() => handleSort('duration_days')} className="cursor-pointer">
                <div className="th-content">
                  <span>Duration</span>
                  <ArrowUpDown size={12} />
                </div>
              </th>
              <th onClick={() => handleSort('peak_value')} className="cursor-pointer">
                <div className="th-content">
                  <span>Peak ({unit})</span>
                  <ArrowUpDown size={12} />
                </div>
              </th>
              <th onClick={() => handleSort('cumulative_excess')} className="cursor-pointer">
                <div className="th-content">
                  <span>Cumulative Excess</span>
                  <ArrowUpDown size={12} />
                </div>
              </th>
            </tr>
          </thead>
          <tbody>
            {visibleEvents.map((ev) => (
              <tr key={ev.id}>
                <td><span className="event-id-badge">#{ev.id}</span></td>
                <td><strong>{ev.start_date}</strong></td>
                <td>{ev.end_date}</td>
                <td>
                  <span className={`duration-badge ${ev.duration_days >= 7 ? 'extreme' : ev.duration_days >= 4 ? 'severe' : 'standard'}`}>
                    {ev.duration_days} days
                  </span>
                </td>
                <td>
                  <span className="peak-val">
                    {ev.peak_value}{unit}
                  </span>
                </td>
                <td>
                  <span className="excess-val">
                    +{ev.cumulative_excess}{unit}-days
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {sorted.length > displayCount && (
        <div className="table-footer">
          <button
            type="button"
            className="btn-show-more"
            onClick={() => setDisplayCount((prev) => prev + 15)}
          >
            <span>Show more events ({sorted.length - displayCount} remaining)</span>
            <ChevronRight size={14} />
          </button>
        </div>
      )}
    </div>
  );
}
