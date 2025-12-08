// ✅ URL BASE DA API (Usada para as rotas internas do sistema)
const API_BASE_URL = 'https://flowscheduler-app-1.onrender.com';

// Recupera o token salvo no navegador
let authToken = localStorage.getItem('token'); 

// =======================================================
// 🚀 INICIALIZAÇÃO DO SISTEMA
// =======================================================
document.addEventListener('DOMContentLoaded', () => {
    
    // 1. Controle de Telas (Login vs Sistema)
    const loginScreen = document.getElementById('login-screen');
    const appScreen = document.getElementById('app-screen');

    if (authToken) {
        // Se tem token, vai direto para o sistema
        if (loginScreen) loginScreen.style.display = 'none';
        if (appScreen) appScreen.style.display = 'block';
        loadEmpregados();
        loadTarefas();
    } else {
        // Se não tem token, mostra login
        if (loginScreen) loginScreen.style.display = 'flex';
        if (appScreen) appScreen.style.display = 'none';
    }

    // 2. Configura botões (com verificação se existem na tela)
    const loginForm = document.getElementById('login-form');
    if (loginForm) loginForm.addEventListener('submit', handleLogin);

    const registerForm = document.getElementById('register-form');
    if (registerForm) registerForm.addEventListener('submit', handleRegister);

    const empForm = document.getElementById('empregado-form');
    if (empForm) empForm.addEventListener('submit', handleCreateEmpregado);

    const taskForm = document.getElementById('tarefa-form');
    if (taskForm) taskForm.addEventListener('submit', handleCreateTarefa);

    // 3. Configurações visuais
    setupTabs();
    setupAlertSystem();
});

// =======================================================
// 🔐 AUTENTICAÇÃO (URLs DIRETAS PARA EVITAR ERROS)
// =======================================================

async function handleLogin(e) {
    e.preventDefault();
    const email = document.getElementById('login-email').value;
    const senha = document.getElementById('login-senha').value;
    const msg = document.getElementById('login-msg');

    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', senha);

    try {
        console.log("Tentando login em: https://flowscheduler-app-1.onrender.com/token");
        
        // URL DIRETA (HARDCODED)
        const response = await fetch('https://flowscheduler-app-1.onrender.com/token', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData
        });

        if (response.ok) {
            const data = await response.json();
            authToken = data.access_token;
            localStorage.setItem('token', authToken);
            if (msg) msg.textContent = "";
            location.reload(); // Recarrega para entrar no sistema limpo
        } else {
            if (msg) msg.textContent = "Login falhou. Verifique seus dados.";
            console.error("Erro Login:", response.status);
        }
    } catch (error) {
        console.error(error);
        if (msg) msg.textContent = "Erro de conexão com a API.";
    }
}

async function handleRegister(e) {
    e.preventDefault();
    const data = {
        nome: document.getElementById('reg-nome').value,
        cargo: document.getElementById('reg-cargo').value,
        email: document.getElementById('reg-email').value,
        senha: document.getElementById('reg-senha').value
    };

    try {
        console.log("Tentando registrar em: https://flowscheduler-app-1.onrender.com/empregados/registrar");

        // URL DIRETA (HARDCODED)
        const res = await fetch('https://flowscheduler-app-1.onrender.com/empregados/registrar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (res.ok) {
            alert("Conta criada com sucesso! Faça login no formulário acima.");
            document.getElementById('register-form').reset();
        } else {
            const err = await res.json();
            alert("Erro ao criar conta: " + (err.detail || res.statusText));
        }
    } catch (error) {
        console.error("Erro Registro:", error);
        alert("Erro de conexão com a API. Verifique o console.");
    }
}

function logout() {
    localStorage.removeItem('token');
    location.reload();
}

// =======================================================
// 🛡️ FUNÇÃO DE REQUISIÇÃO SEGURA
// =======================================================
async function fetchSecure(endpoint, options = {}) {
    if (!authToken) {
        logout();
        return null;
    }

    if (!options.headers) options.headers = {};
    options.headers['Authorization'] = `Bearer ${authToken}`;

    try {
        // Usa a constante para rotas internas
        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);

        if (response.status === 401) {
            alert("Sessão expirada. Faça login novamente.");
            logout();
            return null;
        }
        return response;
    } catch (error) {
        console.error("Erro FetchSecure:", error);
        return null;
    }
}

// =======================================================
// 👥 LÓGICA DE DADOS (EMPREGADOS & TAREFAS)
// =======================================================

async function loadEmpregados() {
    const response = await fetchSecure('/empregados/');
    if (!response || !response.ok) return;

    const empregados = await response.json();
    const tbody = document.querySelector('#empregados-table tbody');
    const select = document.getElementById('empregado-select');
    
    if (tbody) tbody.innerHTML = '';
    if (select) select.innerHTML = '<option value="">-- Selecione --</option>';

    empregados.forEach(emp => {
        if (tbody) {
            const row = tbody.insertRow();
            row.innerHTML = `<td>${emp.id}</td><td>${emp.nome}</td><td>${emp.cargo}</td>
                <td><button onclick="deleteEmpregado(${emp.id})" style="background:#f44336; color:white; border:none; padding:5px; border-radius:4px; cursor:pointer;">X</button></td>`;
        }
        if (select) {
            const opt = document.createElement('option');
            opt.value = emp.id;
            opt.textContent = emp.nome;
            select.appendChild(opt);
        }
    });
}

async function handleCreateEmpregado(e) {
    e.preventDefault();
    const data = {
        nome: document.getElementById('nome').value,
        cargo: document.getElementById('cargo').value,
        email: document.getElementById('email').value,
        senha: document.getElementById('senha').value
    };

    const res = await fetchSecure('/empregados/registrar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });

    if (res && res.ok) {
        alert("Empregado cadastrado!");
        document.getElementById('empregado-form').reset();
        loadEmpregados();
    } else {
        alert("Erro ao cadastrar.");
    }
}

async function deleteEmpregado(id) {
    if(!confirm("Excluir?")) return;
    const res = await fetchSecure(`/empregados/${id}`, { method: 'DELETE' });
    if (res && res.ok) { loadEmpregados(); loadTarefas(); }
    else alert("Erro ao excluir.");
}

async function loadTarefas() {
    const response = await fetchSecure('/tarefas/');
    if (!response || !response.ok) return;

    const tarefas = await response.json();
    const tbody = document.querySelector('#tarefas-table tbody');
    if (tbody) {
        tbody.innerHTML = '';
        tarefas.forEach(t => {
            const row = tbody.insertRow();
            row.innerHTML = `<td>${t.titulo}</td><td>${t.prazo}</td><td>${t.empregado_id || '-'}</td><td>${t.concluida ? "✅" : "🕒"}</td>
                <td><button onclick="deleteTarefa(${t.id})" style="background:#f44336; color:white; border:none; padding:5px; border-radius:4px; cursor:pointer;">X</button></td>`;
        });
        checkUrgentTasks(tarefas);
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

    const res = await fetchSecure('/tarefas/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });

    if (res && res.ok) {
        alert("Tarefa criada!");
        document.getElementById('tarefa-form').reset();
        loadTarefas();
    } else {
        alert("Erro ao criar tarefa.");
    }
}

async function deleteTarefa(id) {
    if(!confirm("Excluir?")) return;
    const res = await fetchSecure(`/tarefas/${id}`, { method: 'DELETE' });
    if (res && res.ok) loadTarefas();
    else alert("Erro ao excluir.");
}

// --- UTILITÁRIOS ---
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
alertContainer.id = 'task-alerts';
function setupAlertSystem() {
    const header = document.querySelector('#app-screen header');
    if (header) header.parentNode.insertBefore(alertContainer, header.nextSibling);
}
function checkUrgentTasks(tarefas) {
    const pending = tarefas.filter(t => !t.concluida);
    alertContainer.innerHTML = '';
    if (pending.length > 0) {
        const div = document.createElement('div');
        div.style.cssText = "background:#ff9800; color:white; padding:10px; margin:10px; text-align:center; font-weight:bold; border-radius:5px;";
        div.textContent = `🚨 ${pending.length} tarefas pendentes.`;
        alertContainer.appendChild(div);
    }
}
