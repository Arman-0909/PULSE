function drawSparkline(id, data, isUp) {
    const c = document.getElementById(id);
    if (!c || !data.length) return;
    const w = c.offsetWidth, h = 32, max = Math.max(...data, 1);
    const step = w / (data.length - 1 || 1);
    const pts = data.map((v, i) => `${i * step},${h - (v / max) * (h - 4) - 2}`).join(' ');
    const fill = `0,${h} ${pts} ${(data.length - 1) * step},${h}`;
    const color = isUp ? 'var(--accent-green)' : 'var(--accent-red)';
    c.innerHTML = `<svg viewBox="0 0 ${w} ${h}" preserveAspectRatio="none">
        <defs><linearGradient id="g-${id}" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="${color}" stop-opacity="0.2"/>
            <stop offset="100%" stop-color="${color}" stop-opacity="0"/>
        </linearGradient></defs>
        <polygon points="${fill}" fill="url(#g-${id})"/>
        <polyline points="${pts}" fill="none" stroke="${color}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>`;
}

let ws, refreshTimer;

function connectWS() {
    const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
    ws = new WebSocket(protocol + '//' + location.host + '/ws');
    
    const wsStatus = document.getElementById('wsStatus');
    
    ws.onopen = () => {
        if (wsStatus) {
            wsStatus.innerHTML = '<div class="dot"></div> All OK';
            wsStatus.className = 'status-indicator';
        }
        if (refreshTimer) clearInterval(refreshTimer);
    };
    
    ws.onmessage = () => refreshDashboard();
    
    ws.onclose = () => {
        if (wsStatus) {
            wsStatus.innerHTML = '<div class="dot"></div> Reconnecting...';
            wsStatus.className = 'status-indicator error';
        }
        if (!refreshTimer) refreshTimer = setInterval(refreshDashboard, 15000);
        setTimeout(connectWS, 3000);
    };
}

async function refreshDashboard() {
    try {
        const [sRes, tRes] = await Promise.all([fetch('/api/services'), fetch('/api/stats')]);
        const services = await sRes.json();
        const stats = await tRes.json();
        
        // Update stats
        const vals = document.querySelectorAll('.metric-box-value');
        if (vals[0]) vals[0].textContent = stats.total;
        if (vals[1]) vals[1].textContent = stats.online;
        if (vals[2]) vals[2].textContent = stats.offline;
        if (vals[3]) vals[3].innerHTML = `${stats.avg_response}<span style="font-size:12px;color:var(--text-secondary);margin-left:4px;">ms</span>`;
        
        // Update cards
        services.forEach(s => {
            const card = document.querySelector(`.service-card[data-service="${s.name}"]`);
            if (!card) return;
            
            const badge = card.querySelector('.badge');
            if (badge) {
                badge.className = `badge ${s.status}`;
                badge.innerHTML = `<div class="dot"></div> ${s.status}`;
            }
            
            const uv = card.querySelector('.uptime-val');
            if (uv) uv.textContent = `${s.uptime}%`;
            
            const rv = card.querySelector('.response-val');
            if (rv) rv.textContent = `${s.response_time}ms`;
            
            const cv = card.querySelector('.checked-val');
            if (cv && s.last_checked) {
                const t = s.last_checked.includes('T') ? s.last_checked.split('T')[1].split('.')[0] : s.last_checked;
                cv.innerHTML = `<i data-lucide="clock"></i> ${t}`;
                if (typeof lucide !== 'undefined') {
                    lucide.createIcons();
                }
            }
            
            drawSparkline(`spark-${s.id}`, s.sparkline, s.status === 'up');
        });
    } catch (e) { 
        console.error('Refresh failed:', e); 
    }
}

document.addEventListener('DOMContentLoaded', () => {
    // Initial sparkline draw from injected data
    const sparkDataEl = document.getElementById('spark-data');
    if (sparkDataEl) {
        try {
            const sparkData = JSON.parse(sparkDataEl.textContent);
            sparkData.forEach(s => drawSparkline('spark-' + s.id, s.sparkline, s.status === 'up'));
        } catch (e) {
            console.error('Failed to parse spark data', e);
        }
    }

    // Start WebSocket
    connectWS();
    
    // Fallback polling
    refreshTimer = setInterval(refreshDashboard, 15000);
});
