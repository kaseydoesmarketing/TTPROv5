import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_healthz():
	r = client.get("/api/healthz")
	assert r.status_code == 200
	assert r.json().get("ok") is True 