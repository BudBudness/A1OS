document.addEventListener('DOMContentLoaded', () => {
    const statusDot = document.getElementById('statusDot');
    const statusText = document.getElementById('statusText');
    const memoryCount = document.getElementById('memoryCount');
    const recentList = document.getElementById('recentList');
    
    async function checkStatus() {
        try {
            const res = await fetch('http://localhost:8086/');
            const text = await res.text();
            if (text.includes('A1OS')) {
                statusDot.className = 'status-dot online';
                statusText.textContent = 'Online';
                document.getElementById('apiStatus').textContent = '● Online';
                return true;
            }
        } catch {
            statusDot.className = 'status-dot offline';
            statusText.textContent = 'Offline';
            document.getElementById('apiStatus').textContent = '● Offline';
        }
        return false;
    }
    
    async function loadDashboard() {
        try {
            const res = await fetch('http://localhost:8086/search?q=');
            const data = await res.json();
            if (Array.isArray(data)) {
                memoryCount.textContent = data.length;
                recentList.innerHTML = data.slice(0, 5).map(item => 
                    `<li>${item.text || 'Untitled'}</li>`
                ).join('') || '<li class="empty-state">No memory entries</li>';
            }
        } catch {
            memoryCount.textContent = '?';
        }
    }
    
    async function performSearch() {
        const input = document.getElementById('searchInput');
        const results = document.getElementById('searchResults');
        const q = input.value.trim();
        if (!q) { results.innerHTML = '<p class="empty-state">Enter a query</p>'; return; }
        try {
            const res = await fetch(`http://localhost:8086/search?q=${encodeURIComponent(q)}`);
            const data = await res.json();
            if (Array.isArray(data) && data.length) {
                results.innerHTML = data.map(item => 
                    `<div class="result-item">${item.text}</div>`
                ).join('');
            } else {
                results.innerHTML = '<p class="empty-state">No results</p>';
            }
        } catch {
            results.innerHTML = '<p class="empty-state error">Search failed</p>';
        }
    }
    
    async function handleAdd(e) {
        e.preventDefault();
        const text = document.getElementById('addText').value.trim();
        const feedback = document.getElementById('addFeedback');
        if (!text) return;
        try {
            const res = await fetch('http://localhost:8086/add', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text })
            });
            const data = await res.json();
            if (data.ok) {
                feedback.className = 'success';
                feedback.textContent = '✅ Saved!';
                document.getElementById('addText').value = '';
                loadDashboard();
            }
        } catch {
            feedback.className = 'error';
            feedback.textContent = '❌ Failed';
        }
    }
    
    // Navigation
    document.querySelectorAll('.nav-item').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
            document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));
            document.getElementById(`view-${btn.dataset.view}`).classList.add('active');
            btn.classList.add('active');
        });
    });
    
    // Search
    document.getElementById('searchBtn').addEventListener('click', performSearch);
    document.getElementById('searchInput').addEventListener('keypress', e => { if (e.key === 'Enter') performSearch(); });
    
    // Add
    document.getElementById('addForm').addEventListener('submit', handleAdd);
    
    // Settings
    document.getElementById('saveSettings').addEventListener('click', () => {
        const url = document.getElementById('apiUrl').value.trim();
        if (url) {
            localStorage.setItem('apiUrl', url);
            document.getElementById('settingsFeedback').textContent = '✅ Saved!';
            setTimeout(() => location.reload(), 1000);
        }
    });
    
    document.getElementById('apiUrl').value = 'http://localhost:8086';
    checkStatus();
    loadDashboard();
    setInterval(checkStatus, 30000);
    window.performSearch = performSearch;
});
