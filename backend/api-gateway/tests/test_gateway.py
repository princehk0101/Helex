import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app

client = TestClient(app)

def test_public_routes_bypass_auth():
    # health check
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "api-gateway"}

    # We can't fully test /api/v1/auth/login proxying without a running backend,
    # but we can test that the gateway tries to process it (meaning it bypasses JWT).
    # Since we are mocking the proxy or if we don't mock, it will return 502 Bad Gateway
    # which means auth succeeded (it bypassed the 401).
    response = client.post("/api/v1/auth/login", json={"email": "a", "password": "b"})
    # It either hits 502 (if no backend running) or 200 (if running)
    assert response.status_code in [200, 502]

def test_protected_routes_require_jwt():
    # Sending to a protected route without token
    response = client.get("/api/v1/projects/123")
    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "UNAUTHORIZED"

@patch('app.middleware.auth.verify_token')
def test_protected_routes_with_invalid_jwt(mock_verify):
    mock_verify.return_value = None
    response = client.get("/api/v1/projects/123", headers={"Authorization": "Bearer invalid_token"})
    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "UNAUTHORIZED"

@patch('app.middleware.auth.verify_token')
@patch('app.proxy.client.send')
def test_protected_routes_with_valid_jwt(mock_send, mock_verify):
    # Mock JWT verify
    mock_verify.return_value = {"sub": "user-uuid-here"}
    
    # Mock httpx response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.headers = {}
    mock_response.aiter_raw = MagicMock()
    # Mocking async generator for aiter_raw
    async def mock_aiter():
        yield b'{"project": "test"}'
    mock_response.aiter_raw.return_value = mock_aiter()
    mock_send.return_value = mock_response

    response = client.get("/api/v1/projects/123", headers={"Authorization": "Bearer valid_token"})
    assert response.status_code == 200
    assert response.json() == {"project": "test"}
