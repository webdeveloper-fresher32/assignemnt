import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import RegionSelector from './components/RegionSelector';
import MapPicker from './components/MapPicker';
import HazardControls from './components/HazardControls';
import InsightBanner from './components/InsightBanner';
import SummaryCards from './components/SummaryCards';
import FrequencyChart from './components/Charts/FrequencyChart';
import DurationChart from './components/Charts/DurationChart';
import IntensityChart from './components/Charts/IntensityChart';
import DailyTimelineChart from './components/Charts/DailyTimelineChart';
import EventsTable from './components/EventsTable';
import ExportToolbar from './components/ExportToolbar';
import StatisticalDetailsModal from './components/StatisticalDetailsModal';
import { fetchHazardAnalysis, checkHealth } from './services/api';
import { AlertCircle, RefreshCw, Sparkles } from 'lucide-react';
import './App.css';

export default function App() {
  const [theme, setTheme] = useState('dark');
  const [apiHealth, setApiHealth] = useState(null);

  // Geographic state
  const [latitude, setLatitude] = useState(28.6139);
  const [longitude, setLongitude] = useState(77.2090);
  const [regionName, setRegionName] = useState('New Delhi, India');

  // Hazard parameters
  const [hazardType, setHazardType] = useState('heatwave');
  const [startYear, setStartYear] = useState(1990);
  const [endYear, setEndYear] = useState(2023);
  const [thresholdPercentile, setThresholdPercentile] = useState(95.0);
  const [minConsecutiveDays, setMinConsecutiveDays] = useState(3);
  const [useDoyWindow, setUseDoyWindow] = useState(true);

  // Analysis results & state
  const [analysisData, setAnalysisData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Check API health on mount
  useEffect(() => {
    async function initHealth() {
      try {
        const health = await checkHealth();
        setApiHealth(health);
      } catch (err) {
        console.warn('API Health check could not connect:', err);
      }
    }
    initHealth();
  }, []);

  // Fetch analysis function
  const runAnalysis = async (forceRefresh = false) => {
    if (forceRefresh) {
      setIsRefreshing(true);
    } else {
      setIsLoading(true);
    }
    setError(null);

    const payload = {
      latitude: parseFloat(latitude),
      longitude: parseFloat(longitude),
      region_name: regionName,
      hazard_type: hazardType,
      start_year: parseInt(startYear),
      end_year: parseInt(endYear),
      threshold_percentile: parseFloat(thresholdPercentile),
      min_consecutive_days: parseInt(minConsecutiveDays),
      use_doy_window: useDoyWindow,
      force_refresh: forceRefresh,
    };

    try {
      const data = await fetchHazardAnalysis(payload);
      setAnalysisData(data);
    } catch (err) {
      console.error('Failed to run climate analysis:', err);
      const detail = err.response?.data?.detail;
      setError(
        typeof detail === 'string'
          ? detail
          : 'Unable to analyze climate hazard. Please check network connectivity or try another region.'
      );
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  };

  // Run analysis on initial load
  useEffect(() => {
    runAnalysis();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Reset to defaults
  const handleReset = () => {
    setLatitude(28.6139);
    setLongitude(77.2090);
    setRegionName('New Delhi, India');
    setHazardType('heatwave');
    setStartYear(1990);
    setEndYear(2023);
    setThresholdPercentile(95.0);
    setMinConsecutiveDays(3);
    setUseDoyWindow(true);
  };

  const handleLocationChange = ({ latitude: lat, longitude: lon, regionName: name }) => {
    setLatitude(lat);
    setLongitude(lon);
    if (name) setRegionName(name);
  };

  const handleMapLocationSelect = (lat, lon) => {
    setLatitude(lat);
    setLongitude(lon);
    setRegionName(`Selected Coord (${lat.toFixed(3)}°, ${lon.toFixed(3)}°)`);
  };

  const queryParams = {
    latitude,
    longitude,
    region_name: regionName,
    hazard_type: hazardType,
    start_year: startYear,
    end_year: endYear,
    threshold_percentile: thresholdPercentile,
    min_consecutive_days: minConsecutiveDays,
    use_doy_window: useDoyWindow,
  };

  return (
    <div className="app-container">
      {/* 1. Header / Navbar */}
      <Navbar
        theme={theme}
        setTheme={setTheme}
        apiHealth={apiHealth}
        cachedStatus={analysisData?.cached}
        executionTime={analysisData?.execution_time_ms ?? null}
      />

      {/* 2. Top Interactive Control Hub */}
      <div className="controls-hub-grid">
        {/* Left Column: Region Search & Controls */}
        <div className="left-controls-col">
          <div className="glass-panel" style={{ padding: '1.25rem' }}>
            <RegionSelector
              latitude={latitude}
              longitude={longitude}
              regionName={regionName}
              onLocationChange={handleLocationChange}
            />
          </div>

          <HazardControls
            hazardType={hazardType}
            setHazardType={setHazardType}
            startYear={startYear}
            setStartYear={setStartYear}
            endYear={endYear}
            setEndYear={setEndYear}
            thresholdPercentile={thresholdPercentile}
            setThresholdPercentile={setThresholdPercentile}
            minConsecutiveDays={minConsecutiveDays}
            setMinConsecutiveDays={setMinConsecutiveDays}
            useDoyWindow={useDoyWindow}
            setUseDoyWindow={setUseDoyWindow}
            isLoading={isLoading}
            onAnalyze={() => runAnalysis(false)}
            onReset={handleReset}
          />
        </div>

        {/* Right Column: Interactive Map */}
        <div className="right-map-col">
          <MapPicker
            latitude={latitude}
            longitude={longitude}
            regionName={regionName}
            onLocationSelect={handleMapLocationSelect}
          />
        </div>
      </div>

      {/* 3. Export & Cache Status Toolbar */}
      {analysisData && (
        <ExportToolbar
          queryParams={queryParams}
          analysisData={analysisData}
          cached={analysisData.cached}
          executionTime={analysisData.execution_time_ms}
          onForceRefresh={() => runAnalysis(true)}
          isRefreshing={isRefreshing}
        />
      )}

      {/* 4. Error Display */}
      {error && (
        <div className="error-hero glass-panel animate-fade-in">
          <AlertCircle size={36} color="var(--danger)" />
          <h3>Analysis Error</h3>
          <p>{error}</p>
          <button className="btn-secondary" onClick={() => runAnalysis(false)}>
            <RefreshCw size={16} />
            <span>Retry Analysis</span>
          </button>
        </div>
      )}

      {/* 5. Loading Skeleton Hero */}
      {isLoading && !analysisData && (
        <div className="loading-hero glass-panel animate-fade-in">
          <div className="loading-spinner-wrap">
            <div className="spinner-outer"></div>
          </div>
          <h3>Ingesting Historical Meteorological Data</h3>
          <p>
            Fetching daily time-series from Open-Meteo ERA5, evaluating 95th percentile exceedances,
            and executing Mann-Kendall trend tests...
          </p>
        </div>
      )}

      {/* 6. Main Analytics Visualizations */}
      {analysisData && !error && (
        <>
          {/* Executive Insight Banner */}
          <InsightBanner
            summary={analysisData.summary}
            trends={analysisData.trends}
            regionName={regionName}
          />

          {/* 5 KPI Metric Cards */}
          <SummaryCards
            summary={analysisData.summary}
            trends={analysisData.trends}
            hazardType={hazardType}
            onOpenDetails={() => setIsModalOpen(true)}
          />

          {/* Interactive Chart Grid */}
          <div className="charts-grid">
            {/* Chart 1: Frequency & OLS Regression */}
            <FrequencyChart
              annualData={analysisData.annual_data}
              regression={analysisData.trends.event_frequency_regression}
              mannKendall={analysisData.trends.event_frequency_mann_kendall}
              hazardType={hazardType}
            />

            {/* Chart 2: Duration & Sen's Slope */}
            <DurationChart
              annualData={analysisData.annual_data}
              regression={analysisData.trends.hazard_days_regression}
              mannKendall={analysisData.trends.hazard_days_mann_kendall}
            />

            {/* Chart 3: Cumulative Thermal Intensity */}
            <IntensityChart
              annualData={analysisData.annual_data}
              hazardType={hazardType}
            />

            {/* Chart 4: Daily Meteorological Timeline with Heatwave Exceedances */}
            <DailyTimelineChart
              dailyTimeline={analysisData.daily_timeline}
              hazardType={hazardType}
            />
          </div>

          {/* Detected Events Table */}
          <EventsTable
            events={analysisData.events}
            hazardType={hazardType}
          />
        </>
      )}

      {/* 7. Detailed Statistical Methodology Modal */}
      <StatisticalDetailsModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        trends={analysisData?.trends}
        dataQuality={analysisData?.data_quality}
        summary={analysisData?.summary}
        queryParams={queryParams}
      />

      {/* 8. Footer */}
      <footer className="app-footer">
        <div className="footer-left">
          <span>Climate Hazard Trend Analyzer • Full-Stack Case Study for Dygnify Ventures</span>
          <span>Data Sources: Open-Meteo Historical Archive (ECMWF ERA5 / ERA5-Land Reanalysis)</span>
        </div>
        <div className="footer-right">
          <a href="/api/v1/docs" target="_blank" rel="noopener noreferrer">
            FastAPI OpenAPI Docs ↗
          </a>
          <a href="#top" onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}>
            Back to Top ↑
          </a>
        </div>
      </footer>
    </div>
  );
}
