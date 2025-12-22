import pytest


class TestMain:
    """Test main application endpoints"""
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns correct message"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert data["message"] == "TradeValue API"
        assert data["version"] == "0.1.0"