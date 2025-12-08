// ✅ URL da sua API no Render
const API_BASE_URL = 'https://flowscheduler-app-1.onrender.com';

document.addEventListener('DOMContentLoaded', () => {
    // 1. Configura as Abas
    setupTabs();

    // 2. Carrega os dados iniciais
    loadEmpregados();
    loadTarefas();

    // 3. Configura os formulários (proteção contra erro se o elemento não existir)
    const empForm = document.getElementById('empregado-form');
    if (empForm) empForm.addEventListener('submit', handleCreateEmpregado);

    const taskForm = document.getElementById('tarefa-form');
    if (taskForm) taskForm.addEventListener('submit', handleCreateTarefa);
});

// --- LÓGICA DAS ABAS (NOVO) ---
function setupTabs() {
    const tabs = document.querySelectorAll('.tab-btn');
    const contents = document.querySelectorAll('.tab-content');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // Remove 'active' de todos
            tabs.forEach(t => t.classList.remove('active'));
            contents.forEach(c => c.classList.remove('active'));

            // Adiciona 'active' no clicado
            tab.classList.add('active');
            
            // Mostra o conteúdo correspondente
            const targetId = tab.getAttribute('data-target');
            document.getElementById(targetId).classList.add('active');
        });
    });
}

// --- LÓGICA DE EMPREGADOS ---
async function loadEmpregados() {
    try {
        const response = await fetch(`${API_BASE_URL}/empregados/`);
        if (!response.ok) throw new Error("Erro ao buscar empregados");
        
        const empregados = await response.json();
        
        const tbody = document.querySelector('#empregados-table tbody');
        const select = document.getElementById('empregado-select'); 
        
        if (tbody) tbody.innerHTML = '';
        if (select) select.innerHTML = '<option value="">-- Selecione um Responsável --</option>'; 

        empregados.forEach(emp => {
            // Tabela
            if (tbody) {
                const row = tbody.insertRow();
                row.innerHTML = `
                    <td>${emp.id}</td>
                    <td>${emp.nome}</td>
                    <td>${emp.cargo}</td>
                    <td><button onclick="deleteEmpregado(${emp.id})" style="background-color: #f44336; padding: 5px 10px; font-size: 12px;">Excluir</button></td>
                `;
            }
            // Dropdown
            if (select) {
                const option = document.createElement('option');
                option.value = emp.id;
                option.textContent = `${emp.nome} (${emp.cargo})`;
                select.appendChild(option);
            }
        });
    } catch (error) {
        console.error(error);
    }
}

async function handleCreateEmpregado(e) {
    e.preventDefault();
    const data = {
        nome: document.getElementById('nome').value,
        cargo: document.getElementById('cargo').value,
        email: document.getElementById('email').value
    };

    try {
        await fetch(`${API_BASE_URL}/empregados/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        alert('Empregado salvo!');
        document.getElementById('empregado-form').reset();
        loadEmpregados();
    } catch (error) {
        alert('Erro ao salvar.');
    }
}

async function deleteEmpregado(id) {
    if(!confirm("Tem certeza?")) return;
    await fetch(`${API_BASE_URL}/empregados/${id}`, { method: 'DELETE' });
    loadEmpregados();
    loadTarefas(); // Atualiza tarefas pois podem ter perdido o dono
}

// --- LÓGICA DE TAREFAS ---
async function loadTarefas() {
    try {
        const response = await fetch(`${API_BASE_URL}/tarefas/`);
        if (!response.ok) throw new Error("Erro ao buscar tarefas");

        const tarefas = await response.json();
        const tbody = document.querySelector('#tarefas-table tbody');
        
        if (tbody) {
            tbody.innerHTML = '';
            tarefas.forEach(task => {
                const row = tbody.insertRow();
                const status = task.concluida ? "✅ Feito" : "🕒 Pendente";
                row.innerHTML = `
                    <td>${task.titulo}</td>
                    <td>${task.prazo}</td>
                    <td style="text-align:center">${task.empregado_id ? task.empregado_id : '-'}</td>
                    <td>${status}</td>
                    <td><button onclick="deleteTarefa(${task.id})" style="background-color: #f44336; padding: 5px 10px; font-size: 12px;">X</button></td>
                `;
            });
            checkUrgentTasks(tarefas);
        }
    } catch (error) {
        console.error(error);
    }
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

    try {
        const res = await fetch(`${API_BASE_URL}/tarefas/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (res.ok) {
            alert('Tarefa Criada!');
            document.getElementById('tarefa-form').reset();
            loadTarefas();
        }
    } catch (error) {
        alert('Erro ao criar tarefa.');
    }
}

async function deleteTarefa(id) {
    if(!confirm("Excluir tarefa?")) return;
    await fetch(`${API_BASE_URL}/tarefas/${id}`, { method: 'DELETE' });
    loadTarefas();
}

// --- ALERTAS ---
const alertContainer = document.createElement('div');
alertContainer.id = 'task-alerts';
document.addEventListener('DOMContentLoaded', () => {
    const header = document.querySelector('header');
    if (header) header.parentNode.insertBefore(alertContainer, header.nextSibling);
});

function checkUrgentTasks(tarefas) {
    const pending = tarefas.filter(t => !t.concluida);
    alertContainer.innerHTML = '';
    if (pending.length > 0) {
        const div = document.createElement('div');
        div.style.cssText = "background: #ff9800; color: white; padding: 10px; text-align: center; font-weight: bold;";
        div.textContent = `🚨 Atenção: ${pending.length} tarefas pendentes.`;
        alertContainer.appendChild(div);
    }
}
