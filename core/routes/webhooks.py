import json

def handle_whatsapp_request(handler):
    if handler.command == "POST":
        content_length = int(handler.headers.get('Content-Length', 0))
        payload = json.loads(handler.rfile.read(content_length).decode("utf-8"))
        
        try:
            changes = payload['entry'][0]['changes'][0]['value']
            if 'messages' in changes:
                msg = changes['messages'][0]
                incoming_text = msg['text']['body']
                sender = msg['from']
                
                print(f"\n[WHATSAPP-IN] From: {sender} | Content: {incoming_text}")
                # Local execution hooks drop directly here (e.g., bash scripts, local database inserts)
                
        except KeyError:
            pass

        handler.send_response(202)
        handler.send_header("Content-Type", "application/json")
        handler.end_headers()
        handler.wfile.write(json.dumps({"status": "captured"}).encode("utf-8"))
