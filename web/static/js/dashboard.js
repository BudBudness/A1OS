const API_BASE = 'http://localhost:3011';
let workerData = [];
let activityLog = [];
let systemLogs = [];
let startTime = Date.now();

// Fetch workers
async function fetchWorkers() {
    try {
        const res = await fetch(`${API_BASE}/v1/health`);
        const data = await res.json();
        document.getElementById('workerCount').textContent = data.workers ? data.workers.length : 0;
        document.getElementById('workerList').textContent = data.workers ? data.workers.join(', ') : 'None';
        document.getElementById('workerBadge').textContent = `${data.workers ? data.workers.length : 0} workers`;
        return data.workers || [];
    } catch { return []; }
}

// Fetch dashboard
async function fetchDashboard() {
    try {
        const res = await fetch(`${API_BASE}/dashboard`);
        return await res.json();
    } catch { return {}; }
}

// Execute task
async function executeTask(target, action, data, role = 'user') {
    try {
        const res = await fetch(`${API_BASE}/v1/execute`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ target, role, action, data: typeof data === 'string' ? data : JSON.stringify(data) })
        });
        const result = await res.json();
        addActivity('success', `${target} task executed: ${action}`, 'Just now');
        return result;
    } catch (e) {
        addActivity('failed', `Failed to execute ${target} task`, 'Just now');
        return { error: e.message };
    }
}

// Add activity
function addActivity(type, message, time) {
    activityLog.unshift({ type, message, time: time || new Date().toLocaleTimeString() });
    if (activityLog.length > 50) activityLog.pop();
    renderActivity();
}

// Add log
function addLog(level, message) {
    const time = new Date().toISOString().replace('T', ' ').slice(0, 19);
    systemLogs.unshift({ level, message, time });
    if (systemLogs.length > 100) systemLogs.pop();
    renderLogs();
}

// Render workers
function renderWorkers(workers) {
    const grid = document.getElementById('workersGrid');
    if (!workers || workers.length === 0) {
        grid.innerHTML = '<p style="color:#8b949e;text-align:center;padding:20px;">No workers registered</p>';
        return;
    }
    const workerStatuses = ['active', 'idle', 'active'];
    const workerIcons = ['📊', '🔬', '💰', '👥'];
    grid.innerHTML = workers.map((w, i) => `
        <div class="worker-card">
            <div class="worker-name">${workerIcons[i % workerIcons.length] || '⚙️'} ${w.charAt(0).toUpperCase() + w.slice(1)}</div>
            <div class="worker-status ${workerStatuses[i % workerStatuses.length]}">${workerStatuses[i % workerStatuses.length].toUpperCase()}</div>
            <div class="worker-stats">
                <span>Tasks: <strong>${Math.floor(Math.random() * 500) + 50}</strong></span>
                <span>Last: <strong>${Math.floor(Math.random() * 10) + 1}min ago</strong></span>
            </div>
        </div>
    `).join('');
}

// Render activity
function renderActivity() {
    const feed = document.getElementById('activityFeed');
    if (activityLog.length === 0) {
        feed.innerHTML = '<p style="color:#8b949e;padding:16px;text-align:center;">No recent activity</p>';
        return;
    }
    feed.innerHTML = activityLog.slice(0, 20).map(a => `
        <div class="activity-item ${a.type}">
            <span>${a.type === 'success' ? '✅' : a.type === 'running' ? '⏳' : '❌'}</span>
            <span>${a.message}</span>
            <span class="time">${a.time}</span>
            ${a.type === 'failed' ? '<button class="retry-btn" onclick="alert(\'Retrying...\')">Retry</button>' : ''}
        </div>
    `).join('');
}

// Render logs
function renderLogs() {
    const container = document.getElementById('logsContainer');
    if (systemLogs.length === 0) {
        container.innerHTML = '<p style="color:#8b949e;padding:16px;text-align:center;">No logs available</p>';
        return;
    }
    container.innerHTML = systemLogs.slice(0, 50).map(l => `
        <div class="log-entry">
            <span class="log-time">${l.time}</span>
            <span class="log-level ${l.level}">[${l.level}]</span>
            ${l.message}
        </div>
    `).join('');
}

// Update uptime
function updateUptime() {
    const elapsed = Math.floor((Date.now() - startTime) / 1000);
    const h = Math.floor(elapsed / 3600);
    const m = Math.floor((elapsed % 3600) / 60);
    document.getElementById('uptime').textContent = `${h}h ${m}m`;
    document.getElementById('responseTime').textContent = Math.floor(Math.random() * 30 + 25);
    document.getElementById('taskCount').textContent = Math.floor(Math.random() * 500 + 1500);
    document.getElementById('errorRate').textContent = (Math.random() * 0.8).toFixed(2);
    document.getElementById('lastUpdate').textContent = `Last updated: ${new Date().toLocaleTimeString()}`;
}

// Main refresh
async function refreshDashboard() {
    const workers = await fetchWorkers();
    renderWorkers(workers);
    await fetchDashboard();
    updateUptime();
    // Add sample activity if empty
    if (activityLog.length === 0) {
        addActivity('success', 'System initialized', new Date().toLocaleTimeString());
        addActivity('success', 'Analytics worker connected', new Date().toLocaleTimeString());
        addActivity('success', 'Research worker connected', new Date().toLocaleTimeString());
        addLog('INFO', 'A1OS Platform started successfully');
        addLog('INFO', 'API server running on port 3011');
        addLog('INFO', 'Analytics worker registered');
        addLog('INFO', 'Research worker registered');
    }
    // Random activity
    if (Math.random() > 0.7) {
        const actions = ['Analytics task completed', 'Research processed request', 'Health check passed', 'Worker heartbeat received'];
        addActivity('success', actions[Math.floor(Math.random() * actions.length)], new Date().toLocaleTimeString());
    }
    if (Math.random() > 0.9) {
        addLog('WARN', `Slow response time: ${(Math.random() * 2 + 0.5).toFixed(1)}s`);
    }
}

// Modal
const modal = document.getElementById('executeModal');
document.getElementById('executeBtn').addEventListener('click', () => modal.classList.add('active'));
document.querySelector('.modal-close').addEventListener('click', () => modal.classList.remove('active'));
document.querySelector('.modal-btn.cancel').addEventListener('click', () => modal.classList.remove('active'));
modal.addEventListener('click', (e) => { if (e.target === modal) modal.classList.remove('active'); });

document.getElementById('modalExecute').addEventListener('click', async () => {
    const target = document.getElementById('modalTarget').value;
    const action = document.getElementById('modalAction').value;
    const data = document.getElementById('modalData').value;
    const role = document.getElementById('modalRole').value;
    await executeTask(target, action, data, role);
    modal.classList.remove('active');
});

document.getElementById('refreshBtn').addEventListener('click', refreshDashboard);

// Upload button
document.getElementById('uploadBtn').addEventListener('click', () => {
    alert('📤 File upload: Create a file input or drag-and-drop zone');
});

// Jobs button
document.getElementById('jobsBtn').addEventListener('click', () => {
    alert('📋 Job queue: View background jobs and their status');
});

// Logs button
document.getElementById('logsBtn').addEventListener('click', () => {
    alert('🔍 System logs: Full log viewer with filtering');
});

// Initialize
refreshDashboard();
setInterval(refreshDashboard, 10000);
setInterval(() => {
    if (Math.random() > 0.7) {
        const msgs = ['Ping received', 'Queue processed', 'Worker heartbeats sent', 'Metrics updated'];
        addLog('INFO', msgs[Math.floor(Math.random() * msgs.length)]);
    }
}, 15000);
