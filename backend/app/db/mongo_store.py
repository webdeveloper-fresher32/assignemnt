import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
from backend.app.db.base import BaseNoSQLStore
from backend.app.config import settings

logger = logging.getLogger(__name__)

class MongoStore(BaseNoSQLStore):
    """
    MongoDB NoSQL Document Store.
    Used when MONGODB_URI is provided.
    """
    def __init__(self, uri: str = settings.MONGODB_URI, db_name: str = settings.MONGODB_DB_NAME):
        from pymongo import MongoClient
        self.client = MongoClient(uri, serverSelectionTimeoutMS=2000)
        self.db = self.client[db_name]
        self.collection = self.db["climate_hazard_cache"]
        # Ensure unique index on cache_key and TTL index on expires_at
        self.collection.create_index("cache_key", unique=True)
        self.collection.create_index("expires_at", expireAfterSeconds=0)
        logger.info(f"Connected to MongoDB at {uri}, collection: climate_hazard_cache")

    def get_analysis(self, cache_key: str) -> Optional[Dict[str, Any]]:
        try:
            doc = self.collection.find_one_and_update(
                {"cache_key": cache_key},
                {"$inc": {"access_count": 1}, "$set": {"last_accessed_at": datetime.now(timezone.utc)}}
            )
            if doc and "data" in doc:
                return doc["data"]
            return None
        except Exception as e:
            logger.error(f"MongoDB get_analysis error: {e}")
            return None

    def save_analysis(self, cache_key: str, document: Dict[str, Any], ttl_days: int = 14) -> bool:
        try:
            now = datetime.now(timezone.utc)
            expires_at = now + timedelta(days=ttl_days)
            payload = {
                "cache_key": cache_key,
                "data": document,
                "created_at": now,
                "expires_at": expires_at,
                "access_count": 1,
                "last_accessed_at": now
            }
            self.collection.update_one(
                {"cache_key": cache_key},
                {"$set": payload},
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"MongoDB save_analysis error: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        try:
            count = self.collection.count_documents({})
            return {
                "store_type": "MongoDB (Distributed NoSQL)",
                "total_cached_documents": count,
                "database": settings.MONGODB_DB_NAME
            }
        except Exception as e:
            return {"error": str(e), "store_type": "MongoDB"}

    def clear_cache(self) -> int:
        try:
            res = self.collection.delete_many({})
            return res.deleted_count
        except Exception as e:
            logger.error(f"MongoDB clear_cache error: {e}")
            return 0
