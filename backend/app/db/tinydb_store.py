import os
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
from tinydb import TinyDB, Query
from backend.app.db.base import BaseNoSQLStore
from backend.app.config import settings

logger = logging.getLogger(__name__)

class TinyDBStore(BaseNoSQLStore):
    """
    Embedded NoSQL Document Store using TinyDB.
    Guarantees out-of-the-box NoSQL persistence without external DB dependencies.
    """
    
    def __init__(self, db_dir: str = settings.CACHE_DIR, db_filename: str = settings.CACHE_DB_FILE):
        os.makedirs(db_dir, exist_ok=True)
        self.db_path = os.path.join(db_dir, db_filename)
        self.db = TinyDB(self.db_path)
        self.table = self.db.table("climate_hazard_cache")
        logger.info(f"Initialized TinyDB NoSQL Store at {self.db_path}")

    def get_analysis(self, cache_key: str) -> Optional[Dict[str, Any]]:
        try:
            Item = Query()
            result = self.table.get(Item.cache_key == cache_key)
            if not result:
                return None
            
            # Check expiration
            expires_at = result.get("expires_at")
            if expires_at:
                exp_dt = datetime.fromisoformat(expires_at)
                if datetime.now(timezone.utc) > exp_dt:
                    logger.info(f"Cache key {cache_key} expired; removing.")
                    self.table.remove(Item.cache_key == cache_key)
                    return None
            
            # Update access count and timestamp
            access_count = result.get("access_count", 0) + 1
            self.table.update({"access_count": access_count, "last_accessed_at": datetime.now(timezone.utc).isoformat()}, Item.cache_key == cache_key)
            
            return result.get("data")
        except Exception as e:
            logger.error(f"Error reading from TinyDB cache: {e}")
            return None

    def save_analysis(self, cache_key: str, document: Dict[str, Any], ttl_days: int = 14) -> bool:
        try:
            now = datetime.now(timezone.utc)
            expires_at = (now + timedelta(days=ttl_days)).isoformat()
            
            payload = {
                "cache_key": cache_key,
                "data": document,
                "created_at": now.isoformat(),
                "expires_at": expires_at,
                "access_count": 1,
                "last_accessed_at": now.isoformat()
            }
            
            Item = Query()
            self.table.upsert(payload, Item.cache_key == cache_key)
            logger.info(f"Saved analysis document for cache_key={cache_key} (expires: {expires_at})")
            return True
        except Exception as e:
            logger.error(f"Error saving to TinyDB cache: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        try:
            total_records = len(self.table)
            file_size_bytes = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
            return {
                "store_type": "TinyDB (Embedded NoSQL)",
                "total_cached_documents": total_records,
                "file_path": self.db_path,
                "file_size_kb": round(file_size_bytes / 1024, 2)
            }
        except Exception as e:
            logger.error(f"Error getting TinyDB stats: {e}")
            return {"error": str(e), "store_type": "TinyDB"}

    def clear_cache(self) -> int:
        try:
            count = len(self.table)
            self.table.truncate()
            return count
        except Exception as e:
            logger.error(f"Error clearing TinyDB: {e}")
            return 0
