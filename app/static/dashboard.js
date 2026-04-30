function drawSparkline(id, data, isUp) {
    const c = document.getElementById(id);
    if (!c || !data.length) return;
    const w = c.offsetWidth, h = 32, max = Math.max(...data, 1);
    const step = w / (data.length - 1 || 1);
    const pts = data.map((v, i) => `${i * step},${h - (v / max) * (h - 4) - 2}`).join(' ');
    const fill = `0,${h} ${pts} ${(data.length - 1) * step},${h}`;
    const color = isUp ? 'var(--green)' : 'var(--red)';
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
    
    const wsStatus = document.getElementById('ws-chip');
    
    ws.onopen = () => {
        if (wsStatus) {
            wsStatus.innerHTML = '<div class="dot"></div> All OK';
            wsStatus.className = 'chip';
        }
        if (refreshTimer) clearInterval(refreshTimer);
    };
    
    ws.onmessage = () => refreshDashboard();
    
    ws.onclose = () => {
        if (wsStatus) {
            wsStatus.innerHTML = '<div class="dot"></div> Reconnecting...';
            wsStatus.className = 'chip err';
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
        
        // Update stats (total, online, offline, avg)
        const vals = document.querySelectorAll('.stat-val');
        if (vals[0]) vals[0].textContent = stats.total;
        if (vals[1]) vals[1].textContent = stats.online;
        if (vals[2]) vals[2].textContent = stats.offline;
        if (vals[3]) vals[3].innerHTML = `${stats.avg_response}<span style="font-size:11px;color:var(--t2);margin-left:2px">ms</span>`;
        
        // Update endpoint cards
        services.forEach(s => {
            const row = document.querySelector(`[data-svc="${s.name}"]`);
            if (row) {
                const badge = row.querySelector('.svc-status');
                if (badge) {
                    badge.className = `badge ${s.status} svc-status`;
                    badge.innerHTML = `<span class="dot" style="width:5px;height:5px;border-radius:50%;background:currentColor;display:inline-block"></span> ${s.status}`;
                }
                
                const uv = row.querySelector('.svc-uptime');
                if (uv) uv.textContent = `${s.uptime}%`;
                
                const rv = row.querySelector('.svc-resp');
                if (rv) rv.textContent = `${s.response_time}ms`;
                
                const cv = row.querySelector('.svc-checked');
                if (cv && s.last_checked) {
                    const t = s.last_checked.includes('T') ? s.last_checked.split('T')[1].split('.')[0] : s.last_checked;
                    cv.textContent = t;
                }
            }
            
            drawSparkline(`spark-${s.id}`, s.sparkline, s.status === 'up');
        });
    } catch (e) { 
        console.error('Refresh failed:', e); 
    }
}

document.addEventListener('DOMContentLoaded', () => {
    // Live clock
    const clockEl = document.getElementById('clock');
    if (clockEl) {
        const tick = () => {
            const now = new Date(), p = n => String(n).padStart(2,'0');
            clockEl.textContent = `${p(now.getHours())}:${p(now.getMinutes())}:${p(now.getSeconds())}`;
        };
        tick(); setInterval(tick, 1000);
    }

    // Initial sparklines
    const sparkDataEl = document.getElementById('spark-data');
    if (sparkDataEl) {
        try {
            JSON.parse(sparkDataEl.textContent)
                .forEach(s => drawSparkline('spark-' + s.id, s.sparkline, s.status === 'up'));
        } catch (e) { console.error(e); }
    }

    connectWS();
    refreshTimer = setInterval(refreshDashboard, 15000);
});
