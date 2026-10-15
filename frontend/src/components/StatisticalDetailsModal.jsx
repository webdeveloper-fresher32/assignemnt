import React from 'react';
import { X, CheckCircle2, AlertTriangle, Calculator, Database, ShieldCheck, HelpCircle } from 'lucide-react';

export default function StatisticalDetailsModal({ isOpen, onClose, trends, dataQuality, summary, queryParams }) {
  if (!isOpen) return null;

  const reg = trends?.event_frequency_regression;
  const regDays = trends?.hazard_days_regression;
  const mk = trends?.event_frequency_mann_kendall;
  const mkDays = trends?.hazard_days_mann_kendall;

  return (
    <div className="modal-backdrop animate-fade-in" onClick={onClose}>
      <div className="modal-card glass-panel" onClick={(e) => e.stopPropagation()}>
        {/* Modal Header */}
        <div className="modal-header">
          <div className="modal-title-wrap">
            <Calculator className="text-orange" size={20} />
            <div>
              <h3 className="modal-title">Scientific & Statistical Methodology</h3>
              <p className="modal-subtitle">
                Linear Regression (OLS) vs Non-Parametric Mann-Kendall Trend Analysis
              </p>
            </div>
          </div>
          <button className="modal-close-btn" onClick={onClose} aria-label="Close modal">
            <X size={18} />
          </button>
        </div>

        {/* Modal Body */}
        <div className="modal-body">
          {/* Section 1: Comparison Matrix */}
          <div className="modal-section">
            <h4 className="section-heading">1. Statistical Trend Comparison</h4>
            <div className="stats-comparison-table-wrap">
              <table className="stats-table">
                <thead>
                  <tr>
                    <th>Metric</th>
                    <th>Ordinary Least Squares (OLS)</th>
                    <th>Mann-Kendall & Sen's Slope</th>
                    <th>Domain Meaning</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td><strong>Event Frequency Rate</strong></td>
                    <td>{reg?.slope ? (reg.slope > 0 ? '+' : '') + reg.slope.toFixed(4) : '0'} events/yr</td>
                    <td>{mk?.sens_slope ? (mk.sens_slope > 0 ? '+' : '') + mk.sens_slope.toFixed(4) : '0'} events/yr</td>
                    <td>Rate of change in annual heatwave occurrences</td>
                  </tr>
                  <tr>
                    <td><strong>Hazard Days Rate</strong></td>
                    <td>{regDays?.slope ? (regDays.slope > 0 ? '+' : '') + regDays.slope.toFixed(3) : '0'} days/yr</td>
                    <td>{mkDays?.sens_slope ? (mkDays.sens_slope > 0 ? '+' : '') + mkDays.sens_slope.toFixed(3) : '0'} days/yr</td>
                    <td>Rate of change in total annual hazard exposure days</td>
                  </tr>
                  <tr>
                    <td><strong>Test Statistic</strong></td>
                    <td>R² = {reg?.r_squared || '0'}</td>
                    <td>Z = {mk?.z_score || '0'}, Tau = {mk?.tau || '0'}</td>
                    <td>Goodness-of-fit vs Rank correlation coefficient</td>
                  </tr>
                  <tr>
                    <td><strong>p-value (Significance)</strong></td>
                    <td>
                      <span className={`p-pill ${reg?.p_value < 0.05 ? 'sig' : 'insig'}`}>
                        p = {reg?.p_value?.toFixed(4) || '1.0'}
                      </span>
                    </td>
                    <td>
                      <span className={`p-pill ${mk?.p_value < 0.05 ? 'sig' : 'insig'}`}>
                        p = {mk?.p_value?.toFixed(4) || '1.0'}
                      </span>
                    </td>
                    <td>
                      {mk?.is_significant 
                        ? 'Statistically significant (reject null hypothesis at 95% confidence)' 
                        : 'Fail to reject null hypothesis (no monotonic secular trend)'}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          {/* Section 2: Mathematical Formulation */}
          <div className="modal-section">
            <h4 className="section-heading">2. Formulae & Domain Standards</h4>
            <div className="math-cards-grid">
              <div className="math-card">
                <h5>Mann-Kendall S-Score & Variance</h5>
                <code>S = ∑ ∑ sgn(x_j - x_k)</code>
                <p>
                  Non-parametric test resistant to non-normal distributions and outlier spikes in discrete event counts.
                </p>
              </div>

              <div className="math-card">
                <h5>Sen's Robust Slope Estimator</h5>
                <code>Q_med = Median((x_j - x_k) / (j - k))</code>
                <p>
                  Theil-Sen estimator calculates the median slope over all pairwise combinations, immune to outlier years.
                </p>
              </div>

              <div className="math-card">
                <h5>ETCCDI TX95p Definition</h5>
                <code>T_threshold(DOY) = 95th Percentile(DOY ± 7 days)</code>
                <p>
                  Climatological calendar-day standard from WMO ETCCDI ensuring seasonal consistency.
                </p>
              </div>
            </div>
          </div>

          {/* Section 3: Data Quality & Provenance */}
          {dataQuality && (
            <div className="modal-section">
              <h4 className="section-heading">3. Data Quality & Cleaning Audit</h4>
              <div className="quality-audit-grid">
                <div className="quality-item">
                  <span className="q-label">Data Source</span>
                  <span className="q-val">{dataQuality.data_source}</span>
                </div>
                <div className="quality-item">
                  <span className="q-label">Valid Daily Records</span>
                  <span className="q-val">{dataQuality.valid_days} / {dataQuality.total_days} days</span>
                </div>
                <div className="quality-item">
                  <span className="q-label">Missing Records Imputed</span>
                  <span className="q-val">{dataQuality.missing_days} days ({dataQuality.missing_percentage}%)</span>
                </div>
                <div className="quality-item">
                  <span className="q-label">Sensor Outliers Scrubbed</span>
                  <span className="q-val">{dataQuality.outliers_detected} records</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="modal-footer">
          <button className="btn-primary" onClick={onClose}>
            Close Methodology
          </button>
        </div>
      </div>
    </div>
  );
}
