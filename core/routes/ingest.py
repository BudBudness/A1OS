import json
import threading

def run_async_scrape(payload):
    # This keeps long tasks off the main web server loop
    print(f"\n[LIVE_LOG] Starting background data aggregation for payload: {json.dumps(payload)}")

def handle_intelligence_ingest(handler):
    if handler.command == "POST":
        content_length = int(handler.headers.get('Content-Length', 0))
        payload = json.loads(handler.rfile.read(content_length).decode("utf-8"))
        print(f"\n[LIVE_LOG] Ingestion Request Received: {json.dumps(payload)}")
        
        # Fire background execution worker
        t = threading.Thread(target=run_async_scrape, args=(payload,))
        t.daemon = True
        t.start()
        
        handler.send_response(202)
        handler.send_header("Content-Type", "application/json")
        handler.end_headers()
        handler.wfile.write(json.dumps({"status": "dispatched"}).encode("utf-8"))
