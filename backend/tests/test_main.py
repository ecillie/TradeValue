"""Tests for app/main.py (FastAPI app, root route, OpenAPI)."""


class TestRoot:
    root_path = "/"

    def test_root_endpoint(self, client):
        response = client.get(self.root_path)
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert data["message"] == "TradeValue API"
        assert data["version"] == "0.1.0"


class TestOpenApi:
    """OpenAPI / docs wiring."""

    def test_openapi_json(self, client):
        r = client.get("/openapi.json")
        assert r.status_code == 200
        assert r.json()["info"]["title"] == "TradeValue API"

    def test_docs_available(self, client):
        r = client.get("/docs")
        assert r.status_code == 200

    def test_players_paths_in_spec(self, client):
        spec = client.get("/openapi.json").json()
        paths = spec.get("paths", {})
        assert any("/api/players" in p for p in paths)
