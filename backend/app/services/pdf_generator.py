import io
from datetime import datetime, timezone
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from backend.app.models.responses import AnalysisResponse

class PDFReportGenerator:
    """
    Generates a professional executive climate hazard trend report in PDF format.
    """

    @classmethod
    def generate_report(cls, data: AnalysisResponse) -> io.BytesIO:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40
        )

        styles = getSampleStyleSheet()
        
        # Custom palette
        PRIMARY = colors.HexColor("#0f172a") # Slate 900
        ACCENT = colors.HexColor("#f97316")  # Orange 500
        MUTED = colors.HexColor("#475569")   # Slate 600
        BG_LIGHT = colors.HexColor("#f8fafc")# Slate 50
        BORDER = colors.HexColor("#e2e8f0")  # Slate 200

        title_style = ParagraphStyle(
            "ReportTitle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=22,
            leading=26,
            textColor=PRIMARY
        )
        
        subtitle_style = ParagraphStyle(
            "ReportSubtitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=11,
            leading=15,
            textColor=MUTED
        )

        h2_style = ParagraphStyle(
            "SectionHeader",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=18,
            textColor=PRIMARY,
            spaceAfter=8
        )

        body_style = ParagraphStyle(
            "ReportBody",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            textColor=PRIMARY
        )

        quote_style = ParagraphStyle(
            "QuoteStyle",
            parent=styles["Normal"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=16,
            textColor=colors.HexColor("#c2410c") # Orange 700
        )

        elements = []

        # 1. Header Banner
        elements.append(Paragraph("CLIMATE HAZARD TREND REPORT", subtitle_style))
        region_name = data.query_params.get("region_name", "Selected Region")
        hazard_name = data.query_params.get("hazard_type", "Heatwave").capitalize()
        elements.append(Paragraph(f"{hazard_name} Analysis: {region_name}", title_style))
        
        coords = f"Coordinates: {data.query_params.get('latitude', 0):.4f}°, {data.query_params.get('longitude', 0):.4f}° | Time Span: {data.query_params.get('start_year', '')}–{data.query_params.get('end_year', '')}"
        generated_date = f"Generated on: {datetime.now(timezone.utc).strftime('%B %d, %Y')} | Source: Open-Meteo ERA5"
        elements.append(Paragraph(f"{coords}<br/>{generated_date}", subtitle_style))
        elements.append(Spacer(1, 12))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=ACCENT, spaceAfter=14))

        # 2. Executive Headline Insight
        headline_table_data = [
            [Paragraph(f"<b>Key Insight:</b> {data.summary.headline}", quote_style)],
            [Paragraph(f"<b>Confidence:</b> {data.summary.statistical_confidence}", body_style)]
        ]
        headline_table = Table(headline_table_data, colWidths=[532])
        headline_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), BG_LIGHT),
            ("BOX", (0, 0), (-1, -1), 1, BORDER),
            ("PADDING", (0, 0), (-1, -1), 10),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        elements.append(headline_table)
        elements.append(Spacer(1, 16))

        # 3. Core Metrics Summary Table
        elements.append(Paragraph("Hazard Summary Metrics", h2_style))
        metrics_data = [
            ["Indicator", "Value", "Indicator", "Value"],
            ["Total Events Detected", str(data.summary.total_events), "Total Hazard Days", f"{data.summary.total_days} days"],
            ["Average Duration", f"{data.summary.avg_duration_days} days", "Longest Event", f"{data.summary.max_event_duration} days"],
            ["Annual Average Frequency", f"{data.summary.annual_average_events} events/yr", "Peak Active Year", str(data.summary.most_active_year)],
            ["Percentile Threshold", f"{data.summary.percentile_threshold_value}°C", "Trend Direction", data.summary.trend_direction]
        ]
        t_metrics = Table(metrics_data, colWidths=[150, 116, 150, 116])
        t_metrics.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, BG_LIGHT]),
            ("PADDING", (0, 0), (-1, -1), 6),
        ]))
        elements.append(t_metrics)
        elements.append(Spacer(1, 16))

        # 4. Statistical Trend Detection (Linear Regression & Mann-Kendall)
        elements.append(Paragraph("Statistical Trend Analysis (OLS & Non-Parametric)", h2_style))
        reg = data.trends.event_frequency_regression
        mk = data.trends.event_frequency_mann_kendall
        
        trends_table_data = [
            ["Method", "Metric", "Value", "Interpretation"],
            ["Linear Regression (OLS)", "Slope (β)", f"{reg.slope:+.4f}/yr", f"{reg.percentage_change:+.1f}% change overall"],
            ["Linear Regression (OLS)", "R² Goodness of Fit", f"{reg.r_squared:.4f}", f"Std Error: {reg.std_err:.4f}"],
            ["Linear Regression (OLS)", "p-value", f"{reg.p_value:.4f}", "Significant" if reg.p_value < 0.05 else "Not Significant"],
            ["Mann-Kendall Test", "Tau Correlation (τ)", f"{mk.tau:.4f}", f"Z-Score: {mk.z_score:.2f}"],
            ["Mann-Kendall Test", "Sen's Slope", f"{mk.sens_slope:+.4f}/yr", f"Trend: {mk.trend.capitalize()}"],
            ["Mann-Kendall Test", "p-value", f"{mk.p_value:.4f}", "H0 rejected (p < 0.05)" if mk.is_significant else "H0 accepted"]
        ]
        t_trends = Table(trends_table_data, colWidths=[140, 130, 100, 162])
        t_trends.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8.5),
            ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, BG_LIGHT]),
            ("PADDING", (0, 0), (-1, -1), 5),
        ]))
        elements.append(t_trends)
        elements.append(Spacer(1, 16))

        # 5. Top 5 Most Severe Events
        if data.events:
            elements.append(Paragraph("Top Severe Hazard Events Recorded", h2_style))
            top_events = sorted(data.events, key=lambda e: (e.duration_days, e.peak_value), reverse=True)[:5]
            ev_data = [["Start Date", "End Date", "Duration", "Peak Value", "Cumulative Excess"]]
            for ev in top_events:
                ev_data.append([
                    ev.start_date,
                    ev.end_date,
                    f"{ev.duration_days} days",
                    f"{ev.peak_value}°C",
                    f"{ev.cumulative_excess}°C-days"
                ])
            t_events = Table(ev_data, colWidths=[100, 100, 100, 110, 122])
            t_events.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#334155")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
                ("PADDING", (0, 0), (-1, -1), 5),
            ]))
            elements.append(t_events)
            elements.append(Spacer(1, 16))

        # 6. Data Quality & Scientific Caveats
        elements.append(Paragraph("Methodology & Domain Context", h2_style))
        elements.append(Paragraph(f"<b>Scientific Caveat:</b> {data.summary.scientific_caveat}", body_style))
        elements.append(Spacer(1, 6))
        elements.append(Paragraph(
            f"<b>Data Quality:</b> {data.data_quality.valid_days}/{data.data_quality.total_days} days valid "
            f"({data.data_quality.missing_percentage}% missing, {data.data_quality.outliers_detected} outliers sanitized). "
            f"Data Source: {data.data_quality.data_source}.",
            subtitle_style
        ))

        doc.build(elements)
        buffer.seek(0)
        return buffer
