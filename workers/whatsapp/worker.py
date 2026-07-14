import json, psycopg2, psycopg2.extras, requests, uuid
from datetime import datetime

class WhatsAppWorker:
    def __init__(self):
        self.name = "whatsapp"
        self.DB_PATH = "dbname=a1os_db user=u0_a433 host=/data/data/com.termux/files/usr/tmp"
        self.green_api_url = "https://api.green-api.com"
    
    def _get_db(self):
        return psycopg2.connect(self.DB_PATH)
    
    async def process(self, payload):
        action = payload.get('action')
        data = payload.get('data', {})
        if action == "send":
            return self._send_message(data)
        elif action == "receive":
            return self._receive_messages(data)
        elif action == "broadcast":
            return self._send_broadcast(data)
        elif action == "contacts":
            return self._get_contacts(data)
        elif action == "history":
            return self._get_history(data)
        elif action == "auto_reply":
            return self._set_auto_reply(data)
        elif action == "get_auto_replies":
            return self._get_auto_replies()
        elif action == "webhook":
            return self._handle_webhook(data)
        else:
            return {"error": f"Unknown action: {action}"}
    
    def _send_message(self, data):
        instance = data.get('instance')
        chat_id = data.get('chat_id')
        message = data.get('message')
        url = f"{self.green_api_url}/waInstance{instance}/sendMessage"
        resp = requests.post(url, json={"chatId": chat_id, "message": message})
        self._log_message(chat_id, message, "sent", resp.json())
        return {"status": "sent", "response": resp.json()}
    
    def _receive_messages(self, data):
        instance = data.get('instance')
        url = f"{self.green_api_url}/waInstance{instance}/receiveNotification"
        resp = requests.get(url)
        if resp.status_code == 200 and resp.json():
            for notif in resp.json():
                if 'body' in notif and 'senderData' in notif:
                    chat_id = notif['senderData']['chatId']
                    message = notif['body']['text'] if 'text' in notif['body'] else ""
                    self._log_message(chat_id, message, "received", notif)
                    self._trigger_auto_reply(instance, chat_id, message)
                requests.delete(f"{self.green_api_url}/waInstance{instance}/deleteNotification", json={"receiptId": notif['receiptId']})
        return {"messages": resp.json() if resp.status_code == 200 else []}
    
    def _send_broadcast(self, data):
        instance = data.get('instance')
        contacts = data.get('contacts', [])
        message = data.get('message')
        results = []
        for contact in contacts:
            url = f"{self.green_api_url}/waInstance{instance}/sendMessage"
            resp = requests.post(url, json={"chatId": contact, "message": message})
            results.append({"contact": contact, "status": resp.status_code})
            self._log_message(contact, message, "broadcast", resp.json())
        return {"broadcast": results, "total": len(results)}
    
    def _get_contacts(self, data):
        instance = data.get('instance')
        url = f"{self.green_api_url}/waInstance{instance}/getContacts"
        resp = requests.get(url)
        return {"contacts": resp.json() if resp.status_code == 200 else []}
    
    def _get_history(self, data):
        conn = self._get_db()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT * FROM whatsapp_messages ORDER BY created_at DESC LIMIT 100")
        msgs = cur.fetchall()
        cur.close(); conn.close()
        return {"messages": [dict(m) for m in msgs]}
    
    def _log_message(self, chat_id, message, direction, response):
        conn = self._get_db()
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS whatsapp_messages (id SERIAL PRIMARY KEY, chat_id TEXT, message TEXT, direction TEXT, response JSONB, created_at TIMESTAMP DEFAULT NOW())")
        cur.execute("INSERT INTO whatsapp_messages (chat_id, message, direction, response) VALUES (%s,%s,%s,%s)", (chat_id, message, direction, json.dumps(response)))
        conn.commit(); cur.close(); conn.close()
    
    def _set_auto_reply(self, data):
        conn = self._get_db()
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS auto_replies (id SERIAL PRIMARY KEY, keyword TEXT, reply TEXT, active BOOLEAN DEFAULT TRUE, created_at TIMESTAMP DEFAULT NOW())")
        cur.execute("INSERT INTO auto_replies (keyword, reply) VALUES (%s,%s) RETURNING id", (data.get('keyword'), data.get('reply')))
        aid = cur.fetchone()[0]
        conn.commit(); cur.close(); conn.close()
        return {"status": "auto_reply_set", "id": aid}
    
    def _get_auto_replies(self):
        conn = self._get_db()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT * FROM auto_replies WHERE active = true")
        replies = cur.fetchall()
        cur.close(); conn.close()
        return {"auto_replies": [dict(r) for r in replies]}
    
    def _trigger_auto_reply(self, instance, chat_id, message):
        replies = self._get_auto_replies()
        for reply in replies.get('auto_replies', []):
            if reply['keyword'].lower() in message.lower():
                self._send_message({"instance": instance, "chat_id": chat_id, "message": reply['reply']})
                break
    
    def _handle_webhook(self, data):
        instance = data.get('instance')
        chat_id = data.get('chat_id')
        message = data.get('message')
        self._log_message(chat_id, message, "webhook", data)
        self._trigger_auto_reply(instance, chat_id, message)
        return {"status": "webhook_processed"}
