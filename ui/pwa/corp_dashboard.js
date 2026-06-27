// Corporation Dashboard
function loadCorpDashboard() {
    const container = document.getElementById('corp-dashboard');
    if (!container) return;
    container.style.display = 'block';
    container.innerHTML = '<h3>🏢 A1OS Corporation</h3><div id="corp-status"></div>';
    
    fetch('/agents', {headers: {'X-API-Key': 'f8baeb69ea9311098aaa8992ada6ab1c6aeb42cfdcef3391c5f5d9ed353b2108'}})
        .then(r => r.json())
        .then(agents => {
            let html = '<div style="margin-top:12px;"><strong>Agents</strong><br>';
            agents.forEach(a => {
                html += `<div style="padding:4px 0;border-bottom:1px solid #2a2a3e;">${a.name}: <span style="color:${a.status === 'working' ? '#fdcb6e' : '#64748b'}">${a.status}</span></div>`;
            });
            html += '</div>';
            document.getElementById('corp-status').innerHTML = html;
        });
    
    fetch('/workflows', {headers: {'X-API-Key': 'f8baeb69ea9311098aaa8992ada6ab1c6aeb42cfdcef3391c5f5d9ed353b2108'}})
        .then(r => r.json())
        .then(workflows => {
            let html = '<div style="margin-top:12px;"><strong>Workflows</strong><br>';
            workflows.forEach(w => {
                html += `<div style="padding:4px 0;border-bottom:1px solid #2a2a3e;">${w.name}: <span style="color:${w.status === 'running' ? '#fdcb6e' : '#64748b'}">${w.status}</span></div>`;
            });
            html += '</div>';
            document.getElementById('corp-status').innerHTML += html;
        });
}
setInterval(loadCorpDashboard, 10000);
loadCorpDashboard();
