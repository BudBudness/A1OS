import threading
import time
import http.client
from .server import ReusableHTTPServer
from .routes import GeneratedRouter

def test_api_subsystem():
    # Spawn ephemeral server instance on a high test port
    test_port = 9091
    server = ReusableHTTPServer(('', test_port), GeneratedRouter)
    
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.2) # Allow local socket loopback bind sequence
    
    # Run loopback HTTP health check verification validation test
    client = http.client.HTTPConnection("127.0.0.1", test_port)
    client.request("GET", "/health")
    response = client.getresponse()
    
    assert response.status == 200
    print("✅ Web API Interface Subsystem Integration Tests Passed.")
    server.shutdown()

if __name__ == "__main__":
    test_api_subsystem()