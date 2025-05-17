"""
Simple tests for status endpoints that don't require database access
"""
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_root_endpoint():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert "Hello from Sector Wars 2102 Game API!" in response.json()["message"]

def test_status_endpoint():
    """Test if the status endpoint is properly configured with the new API version path."""
    response = client.get("/api/v1/status")
    assert response.status_code == 200
    assert "message" in response.json()
    assert "status" in response.json()
    
def test_health_endpoint():
    """Test the health check endpoint."""
    response = client.get("/api/v1/status/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"