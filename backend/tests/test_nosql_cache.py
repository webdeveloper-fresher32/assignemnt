import os
import shutil
import pytest
from backend.app.db.tinydb_store import TinyDBStore

@pytest.fixture
def temp_store(tmp_path):
    test_dir = str(tmp_path / ".test_data")
    store = TinyDBStore(db_dir=test_dir, db_filename="test_cache.json")
    yield store
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)

def test_tinydb_save_and_retrieve(temp_store):
    key = "test_key_123"
    doc = {"region": "Delhi", "events": 15, "headline": "Heatwaves up"}
    
    # Save
    success = temp_store.save_analysis(key, doc, ttl_days=1)
    assert success is True
    
    # Retrieve
    retrieved = temp_store.get_analysis(key)
    assert retrieved is not None
    assert retrieved["region"] == "Delhi"
    assert retrieved["events"] == 15
    
    # Non-existent key
    assert temp_store.get_analysis("non_existent") is None

def test_tinydb_stats_and_clear(temp_store):
    temp_store.save_analysis("k1", {"val": 1})
    temp_store.save_analysis("k2", {"val": 2})
    
    stats = temp_store.get_stats()
    assert stats["total_cached_documents"] == 2
    
    cleared = temp_store.clear_cache()
    assert cleared == 2
    assert temp_store.get_stats()["total_cached_documents"] == 0
