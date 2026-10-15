from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class BaseNoSQLStore(ABC):
    """Abstract NoSQL Document Store Interface for Climate Hazard Analytics"""
    
    @abstractmethod
    def get_analysis(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached analysis document by cache_key"""
        pass
        
    @abstractmethod
    def save_analysis(self, cache_key: str, document: Dict[str, Any], ttl_days: int = 14) -> bool:
        """Store or update analysis document with TTL"""
        pass
        
    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """Return cache health and storage statistics"""
        pass

    @abstractmethod
    def clear_cache(self) -> int:
        """Clear all cached records, returning count of deleted records"""
        pass
