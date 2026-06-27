import requests, json, time
API = 'http://localhost:8086'
KEY = 'f8baeb69ea9311098aaa8992ada6ab1c6aeb42cfdcef3391c5f5d9ed353b2108'
def test_root():
    r = requests.get(f'{API}/')
    assert r.status_code == 200, "Root failed"
    data = r.json()
    assert data['status'] == 'online', "Status not online"
def test_memory_stats():
    r = requests.get(f'{API}/memory/stats', headers={'X-API-Key': KEY})
    assert r.status_code == 200, "Memory stats failed"
def test_agents():
    r = requests.get(f'{API}/agents', headers={'X-API-Key': KEY})
    assert r.status_code == 200, "Agents failed"
def test_system_status():
    r = requests.get(f'{API}/system/status', headers={'X-API-Key': KEY})
    assert r.status_code == 200, "System status failed"
    data = r.json()
    assert data['status'] == 'online', "System not online"
if __name__ == '__main__':
    test_root(); test_memory_stats(); test_agents(); test_system_status()
    print("✅ All tests passed")
