import React, { useState } from 'react';
import { 
  Flame, CloudRain, SunMedium, Sliders, Calendar, 
  RotateCcw, Sparkles, ChevronDown, ChevronUp, RefreshCw
} from 'lucide-react';

export default function HazardControls({
  hazardType,
  setHazardType,
  startYear,
  setStartYear,
  endYear,
  setEndYear,
  thresholdPercentile,
  setThresholdPercentile,
  minConsecutiveDays,
  setMinConsecutiveDays,
  useDoyWindow,
  setUseDoyWindow,
  isLoading,
  onAnalyze,
  onReset
}) {
  const [showAdvanced, setShowAdvanced] = useState(false);

  const handlePresetYears = (s, e) => {
    setStartYear(s);
    setEndYear(e);
  };

  return (
    <div className="hazard-controls glass-panel">
      {/* 1. Hazard Type Selector */}
      <div className="control-section">
        <label className="section-label">
          <Flame size={16} className="text-orange" />
          <span>Climate Hazard Type</span>
        </label>
        <div className="hazard-tabs">
          <button
            type="button"
            className={`hazard-tab ${hazardType === 'heatwave' ? 'active heatwave' : ''}`}
            onClick={() => setHazardType('heatwave')}
          >
            <Flame size={18} />
            <div className="tab-text">
              <span className="tab-title">Heatwave</span>
              <span className="tab-badge">Default</span>
            </div>
          </button>

          <button
            type="button"
            className={`hazard-tab ${hazardType === 'extreme_precipitation' ? 'active precipitation' : ''}`}
            onClick={() => setHazardType('extreme_precipitation')}
          >
            <CloudRain size={18} />
            <div className="tab-text">
              <span className="tab-title">Extreme Rainfall</span>
              <span className="tab-badge">Bonus</span>
            </div>
          </button>

          <button
            type="button"
            className={`hazard-tab ${hazardType === 'drought' ? 'active drought' : ''}`}
            onClick={() => setHazardType('drought')}
          >
            <SunMedium size={18} />
            <div className="tab-text">
              <span className="tab-title">Drought</span>
              <span className="tab-badge">Bonus</span>
            </div>
          </button>
        </div>
      </div>

      {/* 2. Time Range Selection */}
      <div className="control-section">
        <div className="section-label-row">
          <label className="section-label">
            <Calendar size={16} className="text-orange" />
            <span>Time Span: {startYear} – {endYear} ({endYear - startYear + 1} Years)</span>
          </label>
          <div className="year-presets">
            <button 
              type="button" 
              className={`year-preset-btn ${startYear === 1990 && endYear === 2023 ? 'active' : ''}`}
              onClick={() => handlePresetYears(1990, 2023)}
            >
              1990–2023
            </button>
            <button 
              type="button" 
              className={`year-preset-btn ${startYear === 1980 && endYear === 2023 ? 'active' : ''}`}
              onClick={() => handlePresetYears(1980, 2023)}
            >
              1980–2023
            </button>
            <button 
              type="button" 
              className={`year-preset-btn ${startYear === 1950 && endYear === 2023 ? 'active' : ''}`}
              onClick={() => handlePresetYears(1950, 2023)}
            >
              Full (1950+)
            </button>
          </div>
        </div>

        <div className="range-inputs-row">
          <div className="range-col">
            <span className="range-col-label">Start Year: {startYear}</span>
            <input
              type="range"
              min="1950"
              max={endYear - 3}
              value={startYear}
              onChange={(e) => setStartYear(parseInt(e.target.value))}
              className="slider-input"
            />
          </div>
          <div className="range-col">
            <span className="range-col-label">End Year: {endYear}</span>
            <input
              type="range"
              min={startYear + 3}
              max="2024"
              value={endYear}
              onChange={(e) => setEndYear(parseInt(e.target.value))}
              className="slider-input"
            />
          </div>
        </div>
      </div>

      {/* 3. Advanced Parameters Toggle */}
      <div className="advanced-toggle-row">
        <button
          type="button"
          className="advanced-btn"
          onClick={() => setShowAdvanced(!showAdvanced)}
        >
          <Sliders size={15} />
          <span>Domain Methodology Parameters</span>
          {showAdvanced ? <ChevronUp size={15} /> : <ChevronDown size={15} />}
        </button>
      </div>

      {showAdvanced && (
        <div className="advanced-panel animate-fade-in">
          <div className="param-grid">
            <div className="param-item">
              <label>
                Percentile Threshold: <strong>{thresholdPercentile}th</strong>
              </label>
              <select
                value={thresholdPercentile}
                onChange={(e) => setThresholdPercentile(parseFloat(e.target.value))}
              >
                <option value="90">90th Percentile (Moderate)</option>
                <option value="95">95th Percentile (WMO Standard)</option>
                <option value="97.5">97.5th Percentile (Severe)</option>
                <option value="99">99th Percentile (Extreme)</option>
              </select>
              <span className="param-hint">Base temperature threshold for exceedance</span>
            </div>

            <div className="param-item">
              <label>
                Min Consecutive Days: <strong>{minConsecutiveDays} Days</strong>
              </label>
              <select
                value={minConsecutiveDays}
                onChange={(e) => setMinConsecutiveDays(parseInt(e.target.value))}
              >
                <option value="2">2+ Days (Short Spell)</option>
                <option value="3">3+ Days (Standard Heatwave)</option>
                <option value="4">4+ Days (Prolonged Event)</option>
                <option value="5">5+ Days (Severe Prolonged)</option>
              </select>
              <span className="param-hint">Run-length encoding minimum persistence</span>
            </div>

            <div className="param-item checkbox-item">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={useDoyWindow}
                  onChange={(e) => setUseDoyWindow(e.target.checked)}
                />
                <span>ETCCDI Day-of-Year 15-day Rolling Window</span>
              </label>
              <span className="param-hint">Adjusts threshold for seasonal variation across calendar days</span>
            </div>
          </div>
        </div>
      )}

      {/* 4. Action Buttons */}
      <div className="actions-row">
        <button
          type="button"
          className="btn-primary"
          onClick={onAnalyze}
          disabled={isLoading}
        >
          {isLoading ? (
            <>
              <RefreshCw size={18} className="animate-spin" />
              <span>Analyzing ERA5 Climate Series...</span>
            </>
          ) : (
            <>
              <Sparkles size={18} />
              <span>Analyze Climate Trends</span>
            </>
          )}
        </button>

        <button
          type="button"
          className="btn-secondary"
          onClick={onReset}
          disabled={isLoading}
          title="Reset to defaults"
        >
          <RotateCcw size={16} />
          <span>Reset</span>
        </button>
      </div>
    </div>
  );
}
