import logging
from backend.app.config import settings
from backend.app.db.base import BaseNoSQLStore
from backend.app.db.tinydb_store import TinyDBStore

logger = logging.getLogger(__name__)

_db_instance: BaseNoSQLStore = None

def get_db() -> BaseNoSQLStore:
    global _db_instance
    if _db_instance is not None:
        return _db_instance
        
    if settings.MONGODB_URI:
        try:
            from backend.app.db.mongo_store import MongoStore
            _db_instance = MongoStore()
            logger.info("Using MongoDB NoSQL Store")
            return _db_instance
        except Exception as e:
            logger.warning(f"Could not connect to MongoDB ({e}); falling back to embedded TinyDB Store.")
            
    _db_instance = TinyDBStore()
    logger.info("Using embedded TinyDB NoSQL Store")
    return _db_instance
