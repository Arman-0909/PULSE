document.addEventListener('DOMContentLoaded', () => {
    // Clock
    const cl = document.getElementById('clock');
    if (cl) {
        const tick = () => { const n = new Date(), p = v => String(v).padStart(2,'0'); cl.textContent = `${p(n.getHours())}:${p(n.getMinutes())}:${p(n.getSeconds())}`; };
        tick(); setInterval(tick, 1000);
    }

    // Custom selects
    document.querySelectorAll('.sel-wrap').forEach(wrap => {
        const trigger = wrap.querySelector('.sel-trigger');
        const hidden  = document.getElementById(wrap.dataset.target);
        wrap.querySelectorAll('.sel-opt').forEach(opt => {
            opt.addEventListener('click', () => {
                trigger.textContent = opt.textContent;
                hidden.value = opt.dataset.value;
                wrap.querySelectorAll('.sel-opt').forEach(o => o.style.fontWeight = '');
                opt.style.fontWeight = '500';
                wrap.classList.remove('open');
            });
        });
        trigger.addEventListener('click', e => {
            e.stopPropagation();
            document.querySelectorAll('.sel-wrap.open').forEach(w => { if (w !== wrap) w.classList.remove('open'); });
            wrap.classList.toggle('open');
        });
    });
    document.addEventListener('click', () => document.querySelectorAll('.sel-wrap.open').forEach(w => w.classList.remove('open')));

    // Modal close on backdrop / Escape
    ['delModal','editModal'].forEach(id => {
        document.getElementById(id)?.addEventListener('click', e => { if (e.target.id === id) closeModals(); });
    });
    document.addEventListener('keydown', e => { if (e.key === 'Escape') closeModals(); });
});

function closeModals() {
    document.getElementById('delModal').classList.remove('show');
    document.getElementById('editModal').classList.remove('show');
}

function confirmDel(id, name) {
    document.getElementById('delName').textContent = name;
    document.getElementById('delForm').action = '/delete-service/' + id;
    document.getElementById('delModal').classList.add('show');
}

function openEdit(id, name, url, gid) {
    document.getElementById('eName').value  = name;
    document.getElementById('eUrl').value   = url;
    document.getElementById('eGid').value   = gid || '';
    document.getElementById('editForm').action = '/edit-service/' + id;
    const wrap = document.querySelector('#editModal .sel-wrap');
    if (wrap) {
        const trigger = wrap.querySelector('.sel-trigger');
        wrap.querySelectorAll('.sel-opt').forEach(o => {
            if (o.dataset.value === (gid || '')) { trigger.textContent = o.textContent; o.style.fontWeight = '500'; }
            else o.style.fontWeight = '';
        });
    }
    document.getElementById('editModal').classList.add('show');
}
