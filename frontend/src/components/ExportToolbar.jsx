import React, { useState } from 'react';
import { Download, FileText, FileSpreadsheet, RefreshCw, Database, Code, Check } from 'lucide-react';
import { downloadCsv, downloadPdf } from '../services/api';

export default function ExportToolbar({ 
  queryParams, 
  analysisData, 
  cached, 
  executionTime, 
  onForceRefresh, 
  isRefreshing 
}) {
  const [downloadingPdf, setDownloadingPdf] = useState(false);
  const [downloadingCsv, setDownloadingCsv] = useState(false);

  if (!analysisData) return null;

  const handleDownloadCsv = async () => {
    setDownloadingCsv(true);
    try {
      await downloadCsv(queryParams);
    } catch (err) {
      console.error('Failed to download CSV:', err);
      alert('Could not export CSV. Please try again.');
    } finally {
      setDownloadingCsv(false);
    }
  };

  const handleDownloadPdf = async () => {
    setDownloadingPdf(true);
    try {
      await downloadPdf(queryParams);
    } catch (err) {
      console.error('Failed to download PDF:', err);
      alert('Could not export PDF report. Please try again.');
    } finally {
      setDownloadingPdf(false);
    }
  };

  const handleDownloadJson = () => {
    const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(analysisData, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute('href', dataStr);
    downloadAnchor.setAttribute('download', `climate_hazard_${(queryParams.region_name || 'data').replace(/\s+/g, '_').toLowerCase()}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  return (
    <div className="export-toolbar glass-panel">
      <div className="export-toolbar-left">
        <div className="cache-status-indicator">
          <Database size={15} className={cached ? 'text-cyan' : 'text-orange'} />
          <span className="cache-text">
            {cached ? (
              <strong>⚡ NoSQL Document Cache Hit ({executionTime}ms)</strong>
            ) : (
              <strong>🌐 Fresh ERA5 Meteorological Reanalysis ({executionTime}ms)</strong>
            )}
          </span>
        </div>
      </div>

      <div className="export-toolbar-right">
        {/* CSV Export Button */}
        <button
          type="button"
          className="export-btn"
          onClick={handleDownloadCsv}
          disabled={downloadingCsv}
          title="Download Annual Metrics and Detected Events as CSV"
        >
          <FileSpreadsheet size={15} />
          <span>{downloadingCsv ? 'Generating CSV...' : 'Export CSV'}</span>
        </button>

        {/* PDF Export Button (Bonus) */}
        <button
          type="button"
          className="export-btn pdf"
          onClick={handleDownloadPdf}
          disabled={downloadingPdf}
          title="Download Executive Climate Assessment Report as PDF"
        >
          <FileText size={15} />
          <span>{downloadingPdf ? 'Building PDF...' : 'Executive PDF Report'}</span>
        </button>

        {/* JSON Export Button */}
        <button
          type="button"
          className="export-btn"
          onClick={handleDownloadJson}
          title="Download Raw JSON payload"
        >
          <Code size={15} />
          <span>JSON</span>
        </button>

        {/* Force Refresh Button */}
        <button
          type="button"
          className="export-btn refresh"
          onClick={onForceRefresh}
          disabled={isRefreshing}
          title="Bypass cache and force re-fetch from Open-Meteo"
        >
          <RefreshCw size={14} className={isRefreshing ? 'animate-spin' : ''} />
          <span>{isRefreshing ? 'Recomputing...' : 'Bypass Cache'}</span>
        </button>
      </div>
    </div>
  );
}
