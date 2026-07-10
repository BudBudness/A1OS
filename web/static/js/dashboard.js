async function checkHealth() {
    try {
        const response = await fetch('/v1/health');
        const data = await response.json();
        document.getElementById('status').textContent = 'Online ✅';
        document.getElementById('status').style.color = '#3fb950';
        document.getElementById('workers').textContent = 'analytics';
        document.getElementById('uptime').textContent = 'Running';
    } catch {
        document.getElementById('status').textContent = 'Offline ❌';
        document.getElementById('status').style.color = '#f85149';
    }
}

async function executeTask() {
    const target = document.getElementById('taskTarget').value;
    const data = document.getElementById('taskData').value;
    try {
        const response = await fetch('/v1/execute', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ target, role: 'user', data, action: 'run' })
        });
        const result = await response.json();
        document.getElementById('result').textContent = JSON.stringify(result, null, 2);
    } catch (error) {
        document.getElementById('result').textContent = 'Error: ' + error;
    }
}

checkHealth();
setInterval(checkHealth, 30000);
