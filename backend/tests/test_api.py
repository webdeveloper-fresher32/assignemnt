import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "online"

def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "database" in data

def test_geocoding_search():
    response = client.get("/api/v1/geocoding/search?q=London")
    assert response.status_code == 200
    results = response.json()
    assert isinstance(results, list)
    if len(results) > 0:
        assert "latitude" in results[0]
        assert "longitude" in results[0]

def test_analyze_endpoint_validation():
    # Invalid latitude (> 90)
    bad_payload = {
        "latitude": 120.0,
        "longitude": 77.0,
        "start_year": 2000,
        "end_year": 2020
    }
    response = client.post("/api/v1/hazards/analyze", json=bad_payload)
    assert response.status_code == 422  # Pydantic validation error

    # Start year > end year
    bad_range_payload = {
        "latitude": 28.6,
        "longitude": 77.2,
        "start_year": 2020,
        "end_year": 2000
    }
    response = client.post("/api/v1/hazards/analyze", json=bad_range_payload)
    assert response.status_code == 422
