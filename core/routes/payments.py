import json

def handle_pesapal_payment(handler):
    if handler.command == "POST":
        content_length = int(handler.headers.get('Content-Length', 0))
        payload = json.loads(handler.rfile.read(content_length).decode("utf-8"))
        print(f"\n[LIVE_LOG] Pesapal Verification payload: {json.dumps(payload)}")
        handler.send_response(200)
        handler.send_header("Content-Type", "application/json")
        handler.end_headers()
        handler.wfile.write(json.dumps({"Response": "OK", "Status": "Reconciled"}).encode("utf-8"))
