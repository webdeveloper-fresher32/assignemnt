import React, { useState } from 'react';
import { TrendingUp, TrendingDown, Minus, Info, Sparkles, CheckCircle2, AlertTriangle } from 'lucide-react';

export default function InsightBanner({ summary, trends, regionName }) {
  const [showCaveat, setShowCaveat] = useState(false);

  if (!summary) return null;

  const isIncreasing = summary.trend_direction === 'Increasing';
  const isDecreasing = summary.trend_direction === 'Decreasing';
  const isSig = trends?.event_frequency_mann_kendall?.is_significant;

  return (
    <div className="insight-banner glass-panel">
      <div className="banner-content">
        <div className="banner-header">
          <div className="banner-tag">
            <Sparkles size={14} className="text-orange" />
            <span>EXECUTIVE CLIMATE SUMMARY</span>
          </div>

          <div className="banner-badges">
            <div className={`trend-pill ${isIncreasing ? 'increasing' : isDecreasing ? 'decreasing' : 'stable'}`}>
              {isIncreasing ? <TrendingUp size={14} /> : isDecreasing ? <TrendingDown size={14} /> : <Minus size={14} />}
              <span>{summary.trend_direction} Trend</span>
            </div>

            <div className={`sig-pill ${isSig ? 'significant' : 'insignificant'}`}>
              {isSig ? <CheckCircle2 size={13} /> : <AlertTriangle size={13} />}
              <span>{isSig ? 'p < 0.05 Significant' : 'p ≥ 0.05 Not Significant'}</span>
            </div>
          </div>
        </div>

        {/* Main headline */}
        <h2 className="headline-text">
          {summary.headline}
        </h2>

        {/* Sub-insight with Mann-Kendall statistics */}
        <div className="sub-headline">
          <p className="confidence-text">
            <strong>Statistical Verification:</strong> {summary.statistical_confidence}
          </p>
        </div>

        {/* Scientific Context Toggle */}
        <div className="caveat-section">
          <button 
            type="button" 
            className="caveat-toggle-btn"
            onClick={() => setShowCaveat(!showCaveat)}
          >
            <Info size={14} />
            <span>{showCaveat ? 'Hide Methodology & Caveats' : 'Methodology & Critical Thinking Disclosure'}</span>
          </button>

          {showCaveat && (
            <div className="caveat-box animate-fade-in">
              <p>
                <strong>Scientific Methodology:</strong> {summary.scientific_caveat}
              </p>
              <p className="caveat-sub">
                <em>Note on Interannual Climate Modes:</em> Decadal shifts like El Niño-Southern Oscillation (ENSO), 
                Pacific Decadal Oscillation (PDO), and local urban heat island (UHI) growth affect local meteorological 
                stations. Long baseline periods (≥30 years) help distinguish anthropogenic secular warming from cyclic climate variability.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
