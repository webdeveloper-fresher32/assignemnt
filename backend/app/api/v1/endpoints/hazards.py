import time
import hashlib
import json
import io
import csv
from fastapi import APIRouter, Depends, Request, Response, HTTPException
from fastapi.responses import StreamingResponse
from backend.app.models.requests import AnalysisRequest, HazardType
from backend.app.models.responses import (
    AnalysisResponse, DailySeriesPoint, HazardEvent
)
from backend.app.core.rate_limiter import limiter
from backend.app.config import settings
from backend.app.db import get_db
from backend.app.services.weather_client import weather_client
from backend.app.services.data_cleaner import DataCleaner
from backend.app.services.hazard_detector import HazardDetector
from backend.app.services.trend_analyzer import TrendAnalyzer
from backend.app.services.insights_generator import InsightsGenerator
from backend.app.services.pdf_generator import PDFReportGenerator

router = APIRouter()

def compute_cache_key(req: AnalysisRequest) -> str:
    key_dict = {
        "lat": round(req.latitude, 3),
        "lon": round(req.longitude, 3),
        "start": req.start_year,
        "end": req.end_year,
        "hazard": req.hazard_type.value,
        "p": req.threshold_percentile,
        "min_days": req.min_consecutive_days,
        "b_start": req.baseline_start_year,
        "b_end": req.baseline_end_year,
        "doy": req.use_doy_window
    }
    raw = json.dumps(key_dict, sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

async def run_analysis(req: AnalysisRequest) -> AnalysisResponse:
    t0 = time.time()
    db = get_db()
    cache_key = compute_cache_key(req)
    
    # 1. Check NoSQL Database Cache
    if not req.force_refresh:
        cached_doc = db.get_analysis(cache_key)
        if cached_doc:
            cached_doc["cached"] = True
            cached_doc["execution_time_ms"] = round((time.time() - t0) * 1000, 2)
            return AnalysisResponse(**cached_doc)

    # 2. Fetch Historical Weather from Open-Meteo
    start_date = f"{req.start_year}-01-01"
    end_date = f"{req.end_year}-12-31"
    raw_weather = await weather_client.fetch_historical_daily(
        latitude=req.latitude,
        longitude=req.longitude,
        start_date=start_date,
        end_date=end_date
    )

    # 3. Clean & Audit Meteorological Data
    cleaned_df, quality_report = DataCleaner.clean_daily_weather(raw_weather)

    # 4. Detect Climate Hazards (ETCCDI Standard)
    events, annual_metrics, threshold_val, df_with_flags = HazardDetector.detect_hazards(
        df=cleaned_df,
        hazard_type=req.hazard_type,
        percentile=req.threshold_percentile,
        min_consecutive_days=req.min_consecutive_days,
        baseline_start_year=req.baseline_start_year,
        baseline_end_year=req.baseline_end_year,
        use_doy_window=req.use_doy_window
    )

    # 5. Scientific Trend Analysis (OLS & Mann-Kendall)
    trend_stats, annual_metrics = TrendAnalyzer.analyze_trends(annual_metrics)

    # 6. Generate Domain Insights
    insights = InsightsGenerator.generate_insights(
        region_name=req.region_name or "Selected Region",
        hazard_type=req.hazard_type,
        start_year=req.start_year,
        end_year=req.end_year,
        events=events,
        annual_metrics=annual_metrics,
        trend_stats=trend_stats,
        threshold_val=threshold_val
    )

    # 7. Build Timeline Sample (last 3 years daily points or sampled)
    recent_years = sorted(cleaned_df["year"].unique())[-3:]
    sample_slice = df_with_flags[df_with_flags["year"].isin(recent_years)]
    val_col = "t_max_imputed" if req.hazard_type == HazardType.HEATWAVE else "precip_imputed"
    
    daily_timeline = [
        DailySeriesPoint(
            date=row["date"].strftime("%Y-%m-%d"),
            value=round(float(row[val_col]), 2),
            threshold=round(float(row["threshold"]), 2),
            is_hazard=bool(row["is_hazard"])
        )
        for _, row in sample_slice.iterrows()
    ]

    execution_ms = round((time.time() - t0) * 1000, 2)

    response = AnalysisResponse(
        query_params=req.model_dump(),
        summary=insights,
        trends=trend_stats,
        annual_data=annual_metrics,
        events=events[:50],  # Return up to 50 most notable events
        daily_timeline=daily_timeline,
        data_quality=quality_report,
        cached=False,
        cached_at=None,
        execution_time_ms=execution_ms
    )

    # 8. Persist into NoSQL Database
    try:
        db.save_analysis(cache_key, response.model_dump(), ttl_days=settings.CACHE_TTL_DAYS)
    except Exception as e:
        # Don't fail the request if cache save encounters a non-fatal error
        pass

    return response

@router.post("/analyze", response_model=AnalysisResponse)
@limiter.limit(settings.RATE_LIMIT_ANALYZE)
async def analyze_hazard(request: Request, body: AnalysisRequest):
    """
    Main analysis endpoint:
    - Validates parameters
    - Queries NoSQL cache
    - Ingests climate data from Open-Meteo
    - Applies percentile hazard logic
    - Performs Mann-Kendall & OLS trend detection
    - Saves document to NoSQL DB
    """
    return await run_analysis(body)

@router.post("/export/csv")
async def export_csv(body: AnalysisRequest):
    """
    Bonus Feature: Export annual hazard statistics and event records to CSV format.
    """
    analysis = await run_analysis(body)
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Metadata Header
    writer.writerow(["# Climate Hazard Trend Analyzer - Data Export"])
    writer.writerow(["# Region", body.region_name])
    writer.writerow(["# Coordinates", f"{body.latitude}, {body.longitude}"])
    writer.writerow(["# Hazard Type", body.hazard_type.value])
    writer.writerow(["# Time Span", f"{body.start_year} - {body.end_year}"])
    writer.writerow(["# Insight", analysis.summary.headline])
    writer.writerow([])
    
    # Section 1: Annual Time Series
    writer.writerow(["--- ANNUAL METRICS ---"])
    writer.writerow([
        "Year", "Event Count", "Total Hazard Days", "Longest Event (Days)", 
        "Peak Value", "Cumulative Intensity", "Mean Temp/Value", 
        "Rolling 3yr Count", "Rolling 5yr Count", "Trend Line Fitted Count"
    ])
    for m in analysis.annual_data:
        writer.writerow([
            m.year, m.event_count, m.total_hazard_days, m.longest_event_days,
            m.max_peak_value or "", m.cumulative_intensity, m.mean_annual_temp or "",
            m.rolling_3yr_count or "", m.rolling_5yr_count or "", m.trend_line_count or ""
        ])
    
    writer.writerow([])
    # Section 2: Detected Events
    writer.writerow(["--- DETECTED HAZARD EVENTS ---"])
    writer.writerow(["Event ID", "Start Date", "End Date", "Duration (Days)", "Peak Value", "Mean Value", "Cumulative Excess"])
    for ev in analysis.events:
        writer.writerow([
            ev.id, ev.start_date, ev.end_date, ev.duration_days,
            ev.peak_value, ev.mean_value, ev.cumulative_excess
        ])
        
    output.seek(0)
    filename = f"climate_hazard_{body.region_name.replace(' ', '_').lower()}_{body.start_year}_{body.end_year}.csv"
    
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.post("/export/pdf")
async def export_pdf(body: AnalysisRequest):
    """
    Bonus Feature: Generates a high-resolution, beautifully formatted executive PDF report.
    """
    analysis = await run_analysis(body)
    pdf_buffer = PDFReportGenerator.generate_report(analysis)
    
    filename = f"climate_hazard_report_{body.region_name.replace(' ', '_').lower()}.pdf"
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
