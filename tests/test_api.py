import requests
import json

def test_root():
    r = requests.get("http://localhost:8086/")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "online"

def test_memory():
    r = requests.post("http://localhost:8086/memory", json={"text": "test"})
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] == True

def test_health():
    r = requests.get("http://localhost:8086/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "healthy"

if __name__ == "__main__":
    test_root()
    test_memory()
    test_health()
    print("✅ All tests passed!")