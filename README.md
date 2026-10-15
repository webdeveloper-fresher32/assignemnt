# Climate Hazard Trend Analyzer 🌍🔥

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.3+-61DAFB?style=flat&logo=react)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-5.0+-646CFF?style=flat&logo=vite)](https://vitejs.dev)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python)](https://www.python.org)
[![Chart.js](https://img.shields.io/badge/Chart.js-4.4+-FF6384?style=flat&logo=chartdotjs)](https://www.chartjs.org)
[![Leaflet](https://img.shields.io/badge/Leaflet-1.9+-199900?style=flat&logo=leaflet)](https://leafletjs.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A full-stack climate intelligence web application built for the **Full-Stack Developer** case study at **Dygnify Ventures Pvt Ltd**.

The application ingests decades of historical meteorological data, performs robust data cleansing and outlier detection, applies domain-specific climatological hazard detection rules (ETCCDI standard), conducts non-parametric **Mann-Kendall trend tests** and **Sen's slope** estimations, caches results in a NoSQL document database, and renders interactive Chart.js visualizations alongside a Leaflet region selection map.

---

## 📑 Table of Contents
1. [Core Features](#-core-features)
2. [Bonus Challenges Implemented](#-bonus-challenges-implemented)
3. [Architecture & System Design](#-architecture--system-design)
4. [Data Sources & Ingestion](#-data-sources--ingestion)
5. [Climate Hazard Logic & Mathematical Definitions](#-climate-hazard-logic--mathematical-definitions)
6. [Data Handling, Cleaning & Outlier Detection](#-data-handling-cleaning--outlier-detection)
7. [NoSQL Caching & Performance](#-nosql-caching--performance)
8. [Security & Rate Limiting](#-security--rate-limiting)
9. [Setup & Installation](#-setup--installation)
10. [API Reference & Documentation](#-api-reference--documentation)
11. [Running Tests](#-running-tests)
12. [Assumptions & Domain Critical Thinking](#-assumptions--domain-critical-thinking)
13. [AI Tools Used & Disclosure](#-ai-tools-used--disclosure)
14. [What Would Be Improved With More Time](#-what-would-be-improved-with-more-time)

---

## 🌟 Core Features

### Frontend (React + Vite)
- **Geographic Region Selection**:
  - Global search with debounced real-time geocoding autocomplete.
  - Interactive **Leaflet Map** with click-to-pin, draggable marker, and coordinate HUD.
  - Quick preset buttons for major cities across all continents (New Delhi, Phoenix, Madrid, London, Tokyo, Sydney, Cairo, São Paulo).
  - Manual latitude/longitude input with bounding validation (-90° to 90°, -180° to 180°).
- **Hazard Type Selection**:
  - **Heatwave** (Default, fully featured ETCCDI standard).
  - **Extreme Precipitation** (WMO R95p / daily rainfall thresholds).
  - **Drought** (Consecutive dry days with precipitation < 1.0mm).
- **Time Range Controls**:
  - Dual year range sliders (e.g. 1990–2023, 1980–2023, or custom multi-decadal spans up to 1950).
  - Quick time presets (1990–2023, 1980–2023, Full Era).
- **Interactive Visualizations (Chart.js & react-chartjs-2)**:
  1. **Hazard Frequency Trend**: Annual event count bars + 3-year moving average line + OLS linear regression fit.
  2. **Hazard Duration & Persistence**: Total hazard days/year + longest single event + Sen's slope line.
  3. **Thermal Severity**: Cumulative excess heat index ($^\circ\text{C}\cdot\text{days}$) + annual mean temperature.
  4. **Daily Meteorological Timeline**: High-resolution daily maximum temperature timeline against the 95th percentile threshold curve, highlighting active heatwave days with glowing indicators.
- **Executive Summary Insights**:
  - Dynamic natural-language headline (e.g., *"Heatwaves have increased by 42.5% in Phoenix between 1990 and 2023."*).
  - 5 KPI summary cards (Total Events, Total Hazard Days, Average Duration, Threshold Temperature, Sen's Slope).
  - Statistical significance badge ($p < 0.05$ verified via Mann-Kendall test).

### Backend (Python + FastAPI)
- **High-Performance API Design**:
  - Clean modular architecture (`api/`, `core/`, `models/`, `services/`, `db/`).
  - Strict Pydantic v2 input and response schemas.
  - Async non-blocking operations with connection pooling via `httpx`.
  - Rate limiting via `slowapi` to protect against quota exhaustion and denial-of-service.
- **Scientific Climate Engine**:
  - NumPy, Pandas, and SciPy for vectorized statistical computation.
  - ETCCDI TX95p moving-window seasonal percentile calculation.
  - Consecutive run-length encoding (RLE) event extraction.
  - Ordinary Least Squares (OLS) Linear Regression and non-parametric Mann-Kendall trend tests.
- **Dual NoSQL Persistence Layer**:
  - Embedded zero-config NoSQL document store (`TinyDB`) out-of-the-box in `.data/nosql_cache.json`.
  - Distributed `MongoDB` integration with automatic TTL indexing when `MONGODB_URI` is configured.
  - SHA-256 parameter hashing for instant sub-3ms cache hits.

---

## 🏆 Bonus Challenges Implemented

| Bonus Challenge | Implementation Details |
|---|---|
| **Interactive Map UI for Region Selection** | Built with **Leaflet** & `react-leaflet`. Users can click anywhere on Earth to update coordinates, inspect zoom levels, and preview elevation and coordinates via live HUD overlay. |
| **PDF & CSV Export of Insights** | 1. **CSV Export**: `/api/v1/hazards/export/csv` generates structured CSV with annual metrics and detected events.<br>2. **PDF Export**: `/api/v1/hazards/export/pdf` uses **ReportLab** to build a formatted executive climate report with tables, summary metrics, statistical tests, and domain notes. |
| **Advanced Trend Detection (Mann-Kendall & Sen's Slope)** | Computes Kendall's $S$ statistic, tie-corrected variance $\text{Var}(S)$, standardized $Z$ score, two-tailed p-value, and Theil-Sen non-parametric median slope estimator. |

---

## 🏗 Architecture & System Design

```
                     ┌────────────────────────────────────────┐
                     │            User Browser (React)        │
                     │  - Leaflet Map (Click-to-Pin)          │
                     │  - Chart.js Visualizations (4 Charts)  │
                     │  - PDF/CSV Export Toolbar              │
                     └──────────────────┬─────────────────────┘
                                        │ HTTP / JSON
                                        ▼
                     ┌────────────────────────────────────────┐
                     │         FastAPI Backend (Port 8000)    │
                     │  - Rate Limiter (SlowAPI)              │
                     │  - Pydantic v2 Validation              │
                     └──────────┬───────────────────┬─────────┘
                                │                   │
                     Cache Hit? │                   │ Cache Miss?
                                ▼                   ▼
               ┌───────────────────────┐   ┌───────────────────────────┐
               │   NoSQL Document Store│   │ Open-Meteo Historical API │
               │   - TinyDB (Embedded) │   │ (ECMWF ERA5 Reanalysis)   │
               │   - MongoDB (Optional)│   └─────────────┬─────────────┘
               └───────────────────────┘                 │
                                                         ▼
                                           ┌───────────────────────────┐
                                           │       Data Cleaning       │
                                           │ - Gap reindexing (daily)  │
                                           │ - Linear interpolation    │
                                           │ - Outlier filtration      │
                                           └─────────────┬─────────────┘
                                                         │
                                                         ▼
                                           ┌───────────────────────────┐
                                           │  Climate Detection Engine │
                                           │ - ETCCDI 95th percentile  │
                                           │ - Run-length encoding     │
                                           │ - Cumulative excess heat  │
                                           └─────────────┬─────────────┘
                                                         │
                                                         ▼
                                           ┌───────────────────────────┐
                                           │      Trend Analysis       │
                                           │ - OLS Linear Regression   │
                                           │ - Mann-Kendall Test       │
                                           │ - Sen's Slope Estimator   │
                                           └─────────────┬─────────────┘
                                                         │
                                                         ▼
                                           ┌───────────────────────────┐
                                           │ Persist in NoSQL Cache &  │
                                           │ Stream JSON / CSV / PDF   │
                                           └───────────────────────────┘
```

---

## 📡 Data Sources & Ingestion

- **Primary Source**: Open-Meteo Historical Weather API (`https://archive-api.open-meteo.com/v1/archive`).
- **Underlying Climatological Reanalysis**: 
  - ECMWF **ERA5** (Global atmospheric reanalysis from 1940 to present, 0.25° grid resolution, ~25–31 km).
  - ECMWF **ERA5-Land** (High-resolution terrestrial surface reanalysis, 0.1° grid resolution, ~9 km).
- **Variables Ingested**:
  - `temperature_2m_max` ($^\circ\text{C}$): Maximum daily 2-meter air temperature.
  - `temperature_2m_min` ($^\circ\text{C}$): Minimum daily 2-meter air temperature.
  - `precipitation_sum` ($\text{mm}$): Total daily precipitation.
- **Resilience Features**:
  - Asynchronous HTTP connection pooling (`httpx.AsyncClient`).
  - Exponential backoff retry loop (handles transient HTTP 429 / 502 gracefully).
  - 20-second request timeout guards.

---

## 🧮 Climate Hazard Logic & Mathematical Definitions

### 1. Percentile-Based Heatwave Definition (ETCCDI Standard)
A **heatwave** is defined as an episode of **$\ge 3$ consecutive days** where the daily maximum temperature ($T_{\max}$) equals or exceeds the **95th percentile** ($T_{95}$) for that geographic location:

$$\text{Exceedance}_t = \begin{cases} 1 & \text{if } T_{\max, t} \ge T_{95, t} \\ 0 & \text{otherwise} \end{cases}$$

$$\text{Heatwave Event} = \left\{ [t_{\text{start}}, t_{\text{end}}] \;\middle|\; \forall t \in [t_{\text{start}}, t_{\text{end}}], \text{Exceedance}_t = 1 \text{ and } (t_{\text{end}} - t_{\text{start}} + 1) \ge 3 \right\}$$

#### Seasonal Day-of-Year (DOY) Rolling Window:
To prevent seasonal bias (e.g. only detecting heatwaves in the hottest month while ignoring anomalous spring/autumn heat spikes), the engine calculates the threshold for each calendar day using a centered **15-day moving window** across the baseline period (TX95p definition):

$$T_{95}(\text{DOY}) = \text{Percentile}_{95}\Big( \big\{ T_{\max}(d, y) \;\big|\; d \in [\text{DOY}-7, \text{DOY}+7], y \in \text{BaselineYears} \big\} \Big)$$

### 2. Cumulative Excess Heat Factor (Thermal Intensity)
The physical severity of a heatwave depends on both temperature and persistence. The engine computes the cumulative excess heat ($E$) in $^\circ\text{C}\cdot\text{days}$:

$$E = \sum_{t=t_{\text{start}}}^{t_{\text{end}}} \max\left(0, T_{\max, t} - T_{95, t}\right)$$

### 3. Non-Parametric Mann-Kendall Trend Test
Because annual heatwave event counts are discrete integer values (often zero in cool years) and do not follow a Gaussian normal distribution, the **Mann-Kendall test** is used to evaluate monotonic trends:

$$S = \sum_{k=1}^{n-1} \sum_{j=k+1}^n \text{sgn}(x_j - x_k)$$

Where:
$$\text{sgn}(\theta) = \begin{cases} +1 & \theta > 0 \\ 0 & \theta = 0 \\ -1 & \theta < 0 \end{cases}$$

Variance with tie correction (where $t_i$ is the number of tied data values in group $i$):
$$\text{Var}(S) = \frac{n(n-1)(2n+5) - \sum_{i=1}^m t_i(t_i-1)(2t_i+5)}{18}$$

Standardized test statistic $Z$:
$$Z = \begin{cases} \frac{S-1}{\sqrt{\text{Var}(S)}} & \text{if } S > 0 \\ 0 & \text{if } S = 0 \\ \frac{S+1}{\sqrt{\text{Var}(S)}} & \text{if } S < 0 \end{cases}$$

Trend significance is assessed via the two-tailed p-value:
$$p = 2 \cdot \left(1 - \Phi(|Z|)\right)$$
If $p < 0.05$, the secular trend is declared **Statistically Significant**.

### 4. Sen's Slope Estimator
The slope is computed non-parametrically using **Sen's robust estimator**, which calculates the median of all pairwise slopes:

$$Q = \text{Median}\left( \frac{x_j - x_k}{j - k} \right) \quad \forall 1 \le k < j \le n$$

---

## 🧹 Data Handling, Cleaning & Outlier Detection

Real-world observational and reanalysis datasets can contain sensor dropouts, transmission errors, and calendar misalignments. The backend implements a specialized `DataCleaner` pipeline:

1. **Continuous Calendar Reindexing**: Creates a complete daily `DatetimeIndex` from `min(date)` to `max(date)`. Any dropped dates (e.g. leap year omissions or missing API days) are detected.
2. **Missing Data Imputation**:
   - Short gaps ($\le 3$ consecutive missing days) are interpolated linearly:
     $$T_t = T_{t-1} + \frac{T_{t+k} - T_{t-1}}{k+1}$$
   - Edge missingness is resolved via bounded forward/backward fill.
3. **Physical Range Outlier Detection**:
   - Rejects physically impossible atmospheric temperatures outside $[-70^\circ\text{C}, +65^\circ\text{C}]$.
   - Clips negative precipitation to $0.0\text{ mm}$.
4. **Statistical Rolling Outlier Detection**:
   - Identifies sensor spikes that deviate by more than **$4$ standard deviations** from a 31-day centered rolling mean:
     $$|T_t - \mu_{31}(t)| > 4 \cdot \sigma_{31}(t)$$
   - Outliers are sanitized to avoid corrupting percentiles or trend lines.
5. **Data Quality Audit Report**:
   - Every API response includes a `DataQualityReport` object detailing total days, missing days, imputed count, outliers detected, and data provenance.

---

## 💾 NoSQL Caching & Performance

To meet the requirement *"Store this data in a NoSQL database. On an API call, read this data from the database and return JSON summaries and trend plots"*:

1. **Deterministic Cache Key**: A SHA-256 hash is computed over all query dimensions:
   ```python
   key = sha256(json.dumps({
       "lat": round(latitude, 3),
       "lon": round(longitude, 3),
       "start": start_year,
       "end": end_year,
       "hazard": hazard_type,
       "p": percentile,
       "min_days": min_days,
       "doy": use_doy_window
   }))
   ```
2. **Dual NoSQL Store Support**:
   - **TinyDB (Embedded NoSQL)**: Stores documents in `.data/nosql_cache.json`. Requires zero setup, zero external daemons, and works out-of-the-box on any evaluator's machine.
   - **MongoDB (Distributed NoSQL)**: If `MONGODB_URI` is provided, automatically uses MongoDB with a unique index on `cache_key` and a native TTL index on `expires_at`.
3. **Performance Benchmark**:
   - **First Call (Cache Miss / Remote Ingestion)**: ~2,500 – 3,000 ms.
   - **Subsequent Call (NoSQL Cache Hit)**: **2.5 ms** (over **1,000x speedup**).

---

## 🔒 Security & Rate Limiting

- **Rate Limiting**: Integrated via `slowapi` using a sliding window:
  - Main analysis endpoint: `20 requests/minute` per client IP.
  - General endpoints: `60 requests/minute`.
  - Rate limit exceedances return `HTTP 429 Too Many Requests` with retry headers.
- **Strict Input Validation**:
  - Pydantic models enforce physical latitude bounds ($-90.0 \le \text{lat} \le 90.0$) and longitude ($-180.0 \le \text{lon} \le 180.0$).
  - Year checks ensure $start\_year \le end\_year$ and span $\ge 3$ years for statistical validity.
  - String inputs are trimmed and bounded against injection vectors.
- **CORS Middleware**: Explicitly configured for local development and production origins.

---

## 🚀 Setup & Installation

### Option 1: One-Click Local Startup (Recommended)

1. **Clone the repository**:
   ```bash
   git clone <your-repo-link>
   cd Assignemt
   ```

2. **Run the one-click startup script**:
   ```bash
   ./start.sh
   ```
   *This automatically creates the Python virtualenv, installs dependencies, builds the frontend, and launches both the FastAPI backend (`http://127.0.0.1:8000`) and the React Vite dev server (`http://127.0.0.1:5173`).*

---

### Option 2: Manual Local Setup

#### Backend Setup:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Run the FastAPI server
PYTHONPATH=.. uvicorn app.main:app --port 8000 --reload
```
*API will be available at `http://127.0.0.1:8000` with Swagger docs at `http://127.0.0.1:8000/api/v1/docs`.*

#### Frontend Setup:
```bash
cd frontend
npm install
npm run dev
```
*Frontend will be available at `http://127.0.0.1:5173`.*

---

### Option 3: Docker Compose Setup

Run the full stack (FastAPI + React Nginx + MongoDB):
```bash
docker-compose up --build
```
- Frontend: `http://localhost:80` (or `http://localhost:5173`)
- Backend API: `http://localhost:8000`
- MongoDB: `localhost:27017`

---

## 📖 API Reference & Documentation

Interactive Swagger OpenAPI documentation is available at:
👉 **`http://127.0.0.1:8000/api/v1/docs`**

### Key Endpoints:

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/hazards/analyze` | Primary endpoint: ingests, cleans, caches, and returns JSON summaries, trends, and charts. |
| `POST` | `/api/v1/hazards/export/csv` | Streams CSV export containing annual metrics and detected events. |
| `POST` | `/api/v1/hazards/export/pdf` | Generates and streams an executive PDF report built with ReportLab. |
| `GET` | `/api/v1/geocoding/search` | Autocomplete global location search by city/region name. |
| `GET` | `/api/v1/health` | Health check reporting service status and NoSQL document counts. |
| `POST` | `/api/v1/cache/clear` | Clears all cached NoSQL documents. |

#### Sample Request (`POST /api/v1/hazards/analyze`):
```json
{
  "latitude": 28.6139,
  "longitude": 77.2090,
  "region_name": "New Delhi, India",
  "hazard_type": "heatwave",
  "start_year": 1990,
  "end_year": 2023,
  "threshold_percentile": 95.0,
  "min_consecutive_days": 3,
  "use_doy_window": true,
  "force_refresh": false
}
```

---

## 🧪 Running Tests

The test suite validates data cleaning, climate hazard detection logic, statistical trends, NoSQL caching, and FastAPI endpoints:

```bash
# Activate virtual environment
source backend/venv/bin/activate

# Run pytest test suite
PYTHONPATH=. pytest backend/tests -v
```

### Test Coverage Highlights:
- `test_climate_logic.py`: Injected 5-day heatwave test, consecutive days filter validation.
- `test_trend_analysis.py`: Monotonic increasing series Mann-Kendall test, Sen's slope test, oscillating series no-trend validation.
- `test_data_cleaning.py`: Missing date insertion, linear interpolation of gaps, and physical outlier suppression.
- `test_nosql_cache.py`: TinyDB document persistence, retrieval, TTL checks, and cache clearing.
- `test_api.py`: Input schema validation, bounds checking, and health endpoints.

---

## 🧠 Assumptions & Domain Critical Thinking

1. **ERA5 Grid Resolution vs Local Microclimates**:
   - The analysis uses ECMWF ERA5 reanalysis data at ~25 km resolution. While ERA5 captures large-scale synoptic heatwaves and thermodynamic warming trends with high fidelity, hyper-local urban heat islands (UHI) in dense concrete canyons may experience localized temperatures $2–4^\circ\text{C}$ higher than the reanalysis grid cell average.
2. **Multi-Decadal Climate Oscillations (ENSO / PDO)**:
   - Climate trends over shorter windows (e.g. 10–15 years) can be dominated by cyclic modes like the El Niño-Southern Oscillation (ENSO) or Indian Ocean Dipole (IOD). For honest climate reporting, the UI highlights when a trend is **not statistically significant** ($p \ge 0.05$) rather than overstating short-term fluctuations.
3. **Choice of Percentile Threshold**:
   - The standard 95th percentile corresponds to approximately the top 18 days per year. In equatorial climates with low seasonal temperature variation, small absolute temperature changes can cause large shifts in exceedance days; the application accommodates this through the day-of-year moving window (TX95p standard).
4. **Percentage Change Metric Robustness**:
   - Calculating percentage change as $\frac{Y_{\text{end}} - Y_{\text{start}}}{Y_{\text{start}}}$ can cause division-by-zero or extreme sensitivity if the initial year recorded zero heatwaves. The engine compares early multi-year baseline averages against recent multi-year averages to provide stable, honest percentage metrics.

---

## 🤖 AI Tools Used & Disclosure

In accordance with Dygnify Ventures' case study instructions (*"Tell us which ones you used and how in your README"*):

- **Tools Used**:
  - **Google Gemini / Antigravity AI Assistant**: Assisted in scaffolding the initial project structure, drafting mathematical formula implementations for the tie-corrected Mann-Kendall test and Sen's slope estimator, writing ReportLab PDF styling definitions, and writing comprehensive Pytest cases.
- **Human Review & Engineering**:
  - All scientific equations (ETCCDI TX95p windowing, Kendall's tau rank correlation, Sen's median slope) were manually cross-referenced against World Meteorological Organization (WMO) climate guidelines.
  - Architecture decisions (FastAPI + React Vite + dual TinyDB/MongoDB NoSQL pattern + SlowAPI rate limiting) were deliberately designed for self-contained, reproducible evaluation.

---

## 🔮 What Would Be Improved With More Time

1. **Spatial Bounding Box & Polygon Aggregation**:
   - Allow users to draw custom bounding polygons on the Leaflet map and spatially average ERA5 grid cells across an entire administrative district or river basin.
2. **Climate Model Future Projections (CMIP6)**:
   - Integrate future climate projections under IPCC Shared Socioeconomic Pathways (SSP2-4.5 and SSP5-8.5) from the Copernicus Climate Data Store to compare historical trends with projected 2030–2070 hazard trajectories.
3. **Compound Climate Hazards**:
   - Implement compound hazard detection (e.g., concurrent heatwaves and agricultural drought, or "wet-bulb" temperature exceedances $TW \ge 35^\circ\text{C}$ combining temperature and relative humidity).
4. **Distributed Redis / Celery Task Queue**:
   - For high-concurrency enterprise deployments, offload historical batch fetching across hundreds of global coordinates to Celery background workers with a Redis message broker.

---

## 📄 License
This project is open-source under the [MIT License](LICENSE).
