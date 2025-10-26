from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_metadata_endpoint():
    r = client.get("/metadata")
    assert r.status_code == 200

def test_query_endpoint():
    r = client.post("/query", json={"query": "What is AI?"})
    assert r.status_code == 200
    j = r.json()
    assert "answer" in j
