import http.server
import socketserver
import json
import os

PORT = 8030

HTML_CONTENT = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>A1OS Conversational Matrix</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
:root{--bg-base:#06060a;--bg-card:#0c0c14;--border:#1a1a2e;--accent:#34c759;--text-main:#a5a5b2;--text-bright:#ffffff;--font-mono:"Courier New",monospace;}
*{box-sizing:border-box;margin:0;padding:0;font-family:var(--font-mono);}
body{background:var(--bg-base);color:var(--text-main);height:100vh;display:flex;flex-direction:column;overflow:hidden;}
header{height:60px;background:var(--bg-card);border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between;padding:0 20px;}
header h1{font-size:14px;color:var(--text-bright);letter-spacing:1px;}
main{flex:1;display:flex;gap:15px;padding:15px;overflow:hidden;}
.chat-container{flex:2;background:var(--bg-card);border:1px solid var(--border);border-radius:8px;display:flex;flex-direction:column;overflow:hidden;}
.chat-history{flex:1;overflow-y:auto;padding:15px;display:flex;flex-direction:column;gap:12px;}
.msg{padding:12px;border-radius:8px;max-width:85%;font-size:13px;line-height:1.4;}
.msg.user{background:#1a1a3a;color:var(--text-bright);align-self:flex-end;}
.msg.ai{background:#111122;color:var(--text-main);align-self:flex-start;border:1px solid var(--border);}
.input-area{padding:12px;border-top:1px solid var(--border);display:flex;gap:10px;background:#090911;}
.input-area input{flex:1;background:var(--bg-base);border:1px solid var(--border);border-radius:6px;padding:0 15px;color:var(--text-bright);outline:none;}
.input-area button{background:#14381d;border:none;color:var(--accent);padding:0 20px;border-radius:6px;cursor:pointer;font-weight:bold;}
.sidebar{flex:1;display:flex;flex-direction:column;gap:15px;}
.card{background:var(--bg-card);border:1px solid var(--border);border-radius:8px;padding:15px;}
.card h3{font-size:11px;text-transform:uppercase;color:var(--text-main);}
.card .val{font-size:28px;font-weight:bold;color:var(--text-bright);margin-top:5px;}
@media(max-width:768px){main{flex-direction:column;}.sidebar{display:grid;grid-template-columns:1fr 1fr;gap:10px;}}
</style>
</head>
<body>
<header>
<h1>A1OS INTEGRATED CONVERSATION MATRIX</h1>
<div style="color:var(--accent);font-size:12px;"><i class="fa-solid fa-circle"></i> KERNEL ONLINE</div>
</header>
<main>
<div class="chat-container">
<div class="chat-history" id="chat">
<div class="msg ai">A1OS System Core initialized successfully. Local agent execution pipeline standing by...</div>
</div>
<div class="input-area">
<input id="in" placeholder="Message local AI agent pipeline..." autocomplete="off">
<button id="run">EXEC</button>
</div>
</div>
<div class="sidebar">
<div class="card"><h3>Active Agents</h3><div class="val">1</div></div>
<div class="card"><h3>Pending Tasks</h3><div class="val">0</div></div>
</div>
</main>
<script>
const chat=document.getElementById("chat");
const inp=document.getElementById("in");
function send(){
const v=inp.value.trim();if(!v)return;
chat.innerHTML+='<div class="msg user">'+v+'</div>';
inp.value="";
setTimeout(()=>{
chat.innerHTML+='<div class="msg ai"><b>[A1OS_CORE]:</b> Frame array serialized. Agent pipeline executing instruction step successfully.</div>';
chat.scrollTop=chat.scrollHeight;
},500);
chat.scrollTop=chat.scrollHeight;
}
document.getElementById("run").addEventListener("click",send);
inp.addEventListener("keypress",e=>{if(e.key==="Enter")send();});
</script>
</body>
</html>"""

class MonolithicServer(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(HTML_CONTENT.encode())
    def log_message(self, format, *args): return

print(f"[*] Overriding all subsystems. Deploying Monolith Server on Port {PORT}...")
socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("", PORT), MonolithicServer) as httpd:
    try: httpd.serve_forever()
    except KeyboardInterrupt: pass
