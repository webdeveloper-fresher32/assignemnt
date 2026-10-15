from fastapi import APIRouter
from backend.app.db import get_db
from backend.app.config import settings

router = APIRouter()

@router.get("/health")
async def health_check():
    db = get_db()
    db_stats = db.get_stats()
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "database": db_stats
    }

@router.post("/cache/clear")
async def clear_cache():
    db = get_db()
    cleared = db.clear_cache()
    return {
        "status": "success",
        "cleared_records": cleared
    }
