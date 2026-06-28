import os

html_content = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=yes">
<title>A1OS Sovereign Control</title>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
:root{--bg-base:#06060a;--bg-card:#0c0c14;--border:#1a1a2e;--accent:#34c759;--warn:#f2a134;--text-main:#a5a5b2;--text-bright:#ffffff;--font-mono:"Courier New",monospace}
*{box-sizing:border-box;margin:0;padding:0;font-family:var(--font-mono);-webkit-font-smoothing:antialiased}
body{background:var(--bg-base);color:var(--text-main);height:100vh;overflow:hidden;display:flex;flex-direction:column}
header{height:60px;background:var(--bg-card);border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between;padding:0 20px;flex-shrink:0}
header h1{font-size:15px;font-weight:bold;color:var(--text-bright);letter-spacing:1px}
.status-pill{padding:6px 14px;border-radius:20px;font-size:11px;background:#141c10;color:var(--accent);border:1px solid #14381d;display:flex;align-items:center;gap:8px}
main{flex:1;overflow-y:auto;padding:20px;display:flex;flex-direction:column;gap:15px}
.matrix-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:15px}
.card{background:var(--bg-card);border:1px solid var(--border);border-radius:8px;padding:18px;display:flex;flex-direction:column;gap:10px}
.card h3{font-size:11px;color:var(--text-main);text-transform:uppercase;letter-spacing:1px}
.card .val{font-size:32px;font-weight:bold;color:var(--text-bright)}
.card .label{font-size:12px;color:var(--text-main)}
.console-box{flex:1;background:#030305;border:1px solid var(--border);border-radius:8px;padding:15px;overflow-y:auto;display:flex;flex-direction:column;gap:8px;font-size:13px;min-height:250px}
.log-entry{display:flex;gap:10px;line-height:1.4}
.log-ts{color:#555566}
.log-tag{color:var(--accent)}
.log-warn{color:var(--warn)}
#input-gateway{height:55px;background:var(--bg-card);border-top:1px solid var(--border);display:flex;align-items:center;padding:0 20px;flex-shrink:0}
.prompt{color:var(--accent);margin-right:12px;font-weight:bold}
input{background:transparent;border:none;color:var(--text-bright);width:100%;height:100%;outline:none;font-size:14px;font-family:var(--font-mono)}
</style>
</head>
<body>
<header>
<h1>A1OS KERNEL MATRIX CONTROL</h1>
<div class="status-pill" id="sys-pill"><i class="fa-solid fa-circle"></i> CONNECTING</div>
</header>
<main>
<div class="matrix-grid">
<div class="card"><h3>🤖 Active Agents</h3><div id="count-agents" class="val">0</div><div class="label">Registry</div></div>
<div class="card"><h3>📋 Pending Tasks</h3><div id="count-tasks" class="val">0</div><div class="label">Queue Layer</div></div>
<div class="card"><h3>✅ Completed</h3><div id="count-done" class="val">0</div><div class="label">Archived Receivables</div></div>
</div>
<div class="console-box" id="console">
<div class="log-entry"><span class="log-ts">[00:00:00]</span> <span class="log-tag">[SYSTEM]</span> Sovereign core state execution layer synchronized.</div>
</div>
</main>
<div id="input-gateway">
<span class="prompt">A1OS // &gt;</span>
<input id="input" placeholder="Drop core instruction matrix frame array..." autocomplete="off"/>
</div>
<script>
const BASE="http://localhost:8086";
const cons=document.getElementById("console");
async function sync(){try{const r=await fetch(BASE+"/api/status");const d=await r.json();
document.getElementById("sys-pill").style.color="#34c759";
document.getElementById("sys-pill").innerHTML='<i class="fa-solid fa-circle"></i> KERNEL ONLINE';
document.getElementById("count-agents").innerText=d.active_agents;
document.getElementById("count-tasks").innerText=d.pending_tasks;
document.getElementById("count-done").innerText=d.completed_tasks;
}catch(e){
document.getElementById("sys-pill").style.color="#ff9500";
document.getElementById("sys-pill").innerHTML='<i class="fa-solid fa-circle"></i> LINK DETACHED';
}}
document.getElementById("input").addEventListener("keypress",e=>{if(e.key==="Enter"){
const cmd=e.target.value;const ts=new Date().toTimeString().split(' ')[0];
cons.innerHTML+='<div class="log-entry"><span class="log-ts">['+ts+']</span> <span class="log-warn">[COMMAND]</span> Dispatched frame override payload: '+cmd+'</div>';
cons.scrollTop=cons.scrollHeight;e.target.value="";}});
setInterval(sync,2000);sync();
</script>
</body>
</html>"""

with open(os.path.expanduser("~/A1OS/ui/pwa/index.html"), "w") as f:
    f.write(html_content)
print("[✔] Master PWA Web Asset Layer: TARGET COMPILED")
