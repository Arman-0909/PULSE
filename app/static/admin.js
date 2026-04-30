document.addEventListener('DOMContentLoaded', () => {
    // Custom dropdowns
    document.querySelectorAll('.custom-select').forEach(sel => {
        const trigger = sel.querySelector('.custom-select-trigger');
        const opts = sel.querySelectorAll('.custom-select-option');
        const hidden = document.getElementById(sel.dataset.target);
        
        trigger.addEventListener('click', e => {
            e.stopPropagation();
            document.querySelectorAll('.custom-select.open').forEach(s => { 
                if (s !== sel) s.classList.remove('open'); 
            });
            sel.classList.toggle('open');
        });
        
        opts.forEach(o => o.addEventListener('click', () => {
            trigger.textContent = o.textContent; 
            hidden.value = o.dataset.value;
            opts.forEach(x => x.classList.remove('selected')); 
            o.classList.add('selected');
            sel.classList.remove('open');
        }));
    });
    
    document.addEventListener('click', () => {
        document.querySelectorAll('.custom-select.open').forEach(s => s.classList.remove('open'));
    });

    // Close modals on outside click or escape
    document.getElementById('deleteModal').addEventListener('click', e => { 
        if (e.target === document.getElementById('deleteModal')) closeModal(); 
    });
    
    document.getElementById('editModal').addEventListener('click', e => { 
        if (e.target === document.getElementById('editModal')) closeEdit(); 
    });
    
    document.addEventListener('keydown', e => { 
        if (e.key === 'Escape') { 
            closeModal(); 
            closeEdit(); 
        } 
    });
});

// Modal functions
function confirmDelete(id, name) { 
    document.getElementById('deleteName').textContent = name; 
    document.getElementById('deleteForm').action = '/delete-service/' + id; 
    document.getElementById('deleteModal').classList.add('show'); 
}

function closeModal() { 
    document.getElementById('deleteModal').classList.remove('show'); 
}

function openEdit(id, name, url, gid) {
    document.getElementById('editName').value = name; 
    document.getElementById('editUrl').value = url;
    document.getElementById('editGroup').value = gid || ''; 
    document.getElementById('editForm').action = '/edit-service/' + id;
    
    const es = document.querySelector('#editModal .custom-select');
    const et = es.querySelector('.custom-select-trigger');
    
    es.querySelectorAll('.custom-select-option').forEach(o => { 
        o.classList.toggle('selected', o.dataset.value === (gid || '')); 
        if (o.dataset.value === (gid || '')) et.textContent = o.textContent; 
    });
    
    document.getElementById('editModal').classList.add('show');
}

function closeEdit() { 
    document.getElementById('editModal').classList.remove('show'); 
}
