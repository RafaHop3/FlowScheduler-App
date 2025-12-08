// ✅ URL "Chumbada" da API (Para não ter erro)
const API_BASE_URL = 'https://flowscheduler-app-1.onrender.com';

document.addEventListener('DOMContentLoaded', () => {
    setupTabs();
    loadEmpregados();
    loadTarefas();

    document.getElementById('empregado-form').addEventListener('submit', handleCreateEmpregado);
    document.getElementById('tarefa-form').addEventListener('submit', handleCreateTarefa);
    
    // Alertas
    setupAlertSystem();
});

// --- EMPREGADOS ---
async function loadEmpregados() {
    try {
        const res = await fetch(`${API_BASE_URL}/empregados/`);
        const data = await res.json();
        
        const tbody = document.querySelector('#empregados-table tbody');
        const select = document.getElementById('empregado-select');
        
        tbody.innerHTML = '';
        select.innerHTML = '<option value="">-- Selecione --</option>';

        data.forEach(emp => {
            // Tabela
            const row = tbody.insertRow();
            row.innerHTML = `<td>${emp.id}</td><td>${emp.nome}</td><td>${emp.cargo}</td>
                <td><button onclick="deleteEmpregado(${emp.id})" style="background:#f44336; color:white; border:none; padding:5px;">X</button></td>`;
            
            // Dropdown
            const opt = document.createElement('option');
            opt.value = emp.id;
            opt.textContent = emp.nome;
            select.appendChild(opt);
        });
    } catch (e) { console.error(e); }
}

async function handleCreateEmpregado(e) {
    e.preventDefault();
    const data = {
        nome: document.getElementById('nome').value,
        cargo: document.getElementById('cargo').value,
        email: document.getElementById('email').value
    };
    await fetch(`${API_BASE_URL}/empregados/`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    });
    alert("Salvo!");
    document.getElementById('empregado-form').reset();
    loadEmpregados();
}

async function deleteEmpregado(id) {
    if(!confirm("Excluir?")) return;
    await fetch(`${API_BASE_URL}/empregados/${id}`, { method: 'DELETE' });
    loadEmpregados(); loadTarefas();
}

// --- TAREFAS ---
async function loadTarefas() {
    try {
        const res = await fetch(`${API_BASE_URL}/tarefas/`);
        const data = await res.json();
        const tbody = document.querySelector('#tarefas-table tbody');
        tbody.innerHTML = '';
        
        data.forEach(t => {
            const row = tbody.insertRow();
            const status = t.concluida ? "✅" : "🕒";
            row.innerHTML = `<td>${t.titulo}</td><td>${t.prazo}</td><td style="text-align:center">${t.empregado_id || '-'}</td><td>${status}</td>
                <td><button onclick="deleteTarefa(${t.id})" style="background:#f44336; color:white; border:none; padding:5px;">X</button></td>`;
        });
        checkUrgentTasks(data);
    } catch (e) { console.error(e); }
}

async function handleCreateTarefa(e) {
    e.preventDefault();
    const empId = document.getElementById('empregado-select').value;
    const data = {
        titulo: document.getElementById('titulo-tarefa').value,
        prazo: document.getElementById('prazo-tarefa').value,
        empregado_id: empId ? parseInt(empId) : null,
        concluida: false
    };
    await fetch(`${API_BASE_URL}/tarefas/`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    });
    alert("Tarefa Criada!");
    document.getElementById('tarefa-form').reset();
    loadTarefas();
}

async function deleteTarefa(id) {
    if(!confirm("Excluir?")) return;
    await fetch(`${API_BASE_URL}/tarefas/${id}`, { method: 'DELETE' });
    loadTarefas();
}

// --- UTIL ---
function setupTabs() {
    const tabs = document.querySelectorAll('.tab-btn');
    const contents = document.querySelectorAll('.tab-content');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            contents.forEach(c => c.classList.remove('active'));
            tab.classList.add('active');
            document.getElementById(tab.getAttribute('data-target')).classList.add('active');
        });
    });
}

const alertContainer = document.createElement('div');
function setupAlertSystem() {
    const main = document.querySelector('main');
    main.insertBefore(alertContainer, main.firstChild);
}
function checkUrgentTasks(tarefas) {
    const pending = tarefas.filter(t => !t.concluida);
    alertContainer.innerHTML = '';
    if (pending.length > 0) {
        alertContainer.innerHTML = `<div style="background:#ff9800; color:white; padding:10px; margin-bottom:20px; text-align:center; border-radius:5px;">🚨 ${pending.length} tarefas pendentes.</div>`;
    }
}
