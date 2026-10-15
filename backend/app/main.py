import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from backend.app.config import settings
from backend.app.core.rate_limiter import limiter
from backend.app.api.v1.endpoints import hazards, geocoding, health

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("climate_analyzer")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Full-stack historical weather and climate hazard trend analysis API. Computes percentile heatwave indicators, Mann-Kendall trend tests, and statistical summaries backed by NoSQL caching.",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc"
)

# Attach SlowAPI Rate Limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(hazards.router, prefix=f"{settings.API_V1_STR}/hazards", tags=["Climate Hazards"])
app.include_router(geocoding.router, prefix=f"{settings.API_V1_STR}/geocoding", tags=["Geocoding"])
app.include_router(health.router, prefix=f"{settings.API_V1_STR}", tags=["System Health"])

@app.get("/", tags=["Root"])
async def root():
    return {
        "title": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "documentation": f"{settings.API_V1_STR}/docs",
        "endpoints": {
            "analyze": f"{settings.API_V1_STR}/hazards/analyze",
            "export_csv": f"{settings.API_V1_STR}/hazards/export/csv",
            "export_pdf": f"{settings.API_V1_STR}/hazards/export/pdf",
            "geocoding": f"{settings.API_V1_STR}/geocoding/search",
            "health": f"{settings.API_V1_STR}/health"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
