// ✅ URL da sua API Backend no Render
const API_BASE_URL = 'https://flowscheduler-app-1.onrender.com';

// Recupera o token salvo no navegador (se existir)
let authToken = localStorage.getItem('token'); 

// =======================================================
// 🚀 INICIALIZAÇÃO DO SISTEMA
// =======================================================
document.addEventListener('DOMContentLoaded', () => {
    
    // 1. Verifica se o usuário já está logado
    if (authToken) {
        showApp(); // Se tem token, pula o login e mostra o painel
    } else {
        // Garante que a tela de login esteja visível se não houver token
        document.getElementById('login-screen').style.display = 'flex';
        document.getElementById('app-screen').style.display = 'none';
    }

    // 2. Configura os botões da Tela de Login/Registro
    const loginForm = document.getElementById('login-form');
    if (loginForm) loginForm.addEventListener('submit', handleLogin);

    const registerForm = document.getElementById('register-form');
    if (registerForm) registerForm.addEventListener('submit', handleRegister);

    // 3. Configura o Sistema Principal (Abas e Formulários Internos)
    setupTabs();
    setupAlertSystem(); // Configura o container de alertas

    const empForm = document.getElementById('empregado-form');
    if (empForm) empForm.addEventListener('submit', handleCreateEmpregado);

    const taskForm = document.getElementById('tarefa-form');
    if (taskForm) taskForm.addEventListener('submit', handleCreateTarefa);
});

// =======================================================
// 🔐 AUTENTICAÇÃO (LOGIN, REGISTRO & TOKEN)
// =======================================================

async function handleLogin(e) {
    e.preventDefault();
    const email = document.getElementById('login-email').value;
    const senha = document.getElementById('login-senha').value;
    const msg = document.getElementById('login-msg');

    // O FastAPI OAuth2 espera dados de formulário (x-www-form-urlencoded)
    const formData = new URLSearchParams();
    formData.append('username', email); // FastAPI usa o campo 'username' para o login
    formData.append('password', senha);

    try {
        const response = await fetch(`${API_BASE_URL}/token`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData
        });

        if (response.ok) {
            const data = await response.json();
            authToken = data.access_token;
            localStorage.setItem('token', authToken); // Salva o token
            if (msg) msg.textContent = "";
            showApp(); // Entra no sistema
        } else {
            if (msg) msg.textContent = "Acesso negado: Verifique e-mail e senha.";
        }
    } catch (error) {
        console.error(error);
        if (msg) msg.textContent = "Erro de conexão com o servidor.";
    }
}

async function handleRegister(e) {
    e.preventDefault();
    // Pega dados do formulário de "Criar Conta"
    const data = {
        nome: document.getElementById('reg-nome').value,
        cargo: document.getElementById('reg-cargo').value,
        email: document.getElementById('reg-email').value,
        senha: document.getElementById('reg-senha').value
    };

    try {
        const res = await fetch(`${API_BASE_URL}/empregados/registrar`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (res.ok) {
            alert("Conta criada com sucesso! Use o formulário de cima para entrar.");
            document.getElementById('register-form').reset();
        } else {
            const err = await res.json();
            alert("Erro ao criar conta: " + (err.detail || "Dados inválidos"));
        }
    } catch (error) {
        alert("Erro de conexão com a API.");
    }
}

function logout() {
    localStorage.removeItem('token'); // Apaga o token
    location.reload(); // Recarrega a página para voltar ao login
}

function showApp() {
    // Esconde login, mostra sistema
    document.getElementById('login-screen').style.display = 'none';
    document.getElementById('app-screen').style.display = 'block';
    
    // Carrega os dados protegidos
    loadEmpregados();
    loadTarefas();
}

// --- FUNÇÃO AUXILIAR DE SEGURANÇA ---
// Adiciona o Token automaticamente em todas as requisições
async function fetchSecure(endpoint, options = {}) {
    if (!authToken) {
        logout();
        return null;
    }

    // Cria cabeçalhos se não existirem
    if (!options.headers) options.headers = {};
    
    // Adiciona o Token JWT no cabeçalho Authorization
    options.headers['Authorization'] = `Bearer ${authToken}`;

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);

        // Se der erro 401 (Token inválido/expirado), desloga o usuário
        if (response.status === 401) {
            alert("Sessão expirada. Por favor, faça login novamente.");
            logout();
            return null;
        }
        return response;
    } catch (error) {
        console.error("Erro na requisição segura:", error);
        return null;
    }
}

// =======================================================
// 👥 LÓGICA DE EMPREGADOS
// =======================================================

async function loadEmpregados() {
    // Usa fetchSecure para enviar o token
    const response = await fetchSecure('/empregados/');
    if (!response || !response.ok) return;

    const empregados = await response.json();
    
    const tbody = document.querySelector('#empregados-table tbody');
    const select = document.getElementById('empregado-select');
    
    if (tbody) tbody.innerHTML = '';
    if (select) select.innerHTML = '<option value="">-- Selecione um Responsável --</option>';

    empregados.forEach(emp => {
        // Preenche a Tabela
        if (tbody) {
            const row = tbody.insertRow();
            row.innerHTML = `
                <td>${emp.id}</td>
                <td>${emp.nome}</td>
                <td>${emp.cargo}</td>
                <td><button onclick="deleteEmpregado(${emp.id})" style="background-color: #f44336; padding: 5px 10px; border:none; color:white; border-radius:4px; cursor:pointer;">Excluir</button></td>
            `;
        }
        // Preenche o Dropdown de tarefas
        if (select) {
            const opt = document.createElement('option');
            opt.value = emp.id;
            opt.textContent = `${emp.nome} (${emp.cargo})`;
            select.appendChild(opt);
        }
    });
}

async function handleCreateEmpregado(e) {
    e.preventDefault();
    
    // Pega os dados do formulário interno (dashboard)
    const data = {
        nome: document.getElementById('nome').value,
        cargo: document.getElementById('cargo').value,
        email: document.getElementById('email').value,
        senha: document.getElementById('senha').value // Novo campo de senha
    };

    // Usa a rota de registro (reaproveitada para criar usuários logado)
    const res = await fetchSecure('/empregados/registrar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });

    if (res && res.ok) {
        alert("Empregado cadastrado com sucesso!");
        document.getElementById('empregado-form').reset();
        loadEmpregados(); // Atualiza a lista
    } else {
        alert("Erro ao cadastrar. Verifique se o e-mail já existe.");
    }
}

async function deleteEmpregado(id) {
    if(!confirm("Tem certeza que deseja excluir?")) return;
    
    const res = await fetchSecure(`/empregados/${id}`, { method: 'DELETE' });
    
    if (res && res.ok) {
        loadEmpregados();
        loadTarefas(); // Atualiza tarefas para refletir a exclusão
    } else {
        alert("Erro ao excluir. Talvez você não tenha permissão de Admin.");
    }
}

// =======================================================
// 📋 LÓGICA DE TAREFAS
// =======================================================

async function loadTarefas() {
    const response = await fetchSecure('/tarefas/');
    if (!response || !response.ok) return;

    const tarefas = await response.json();
    const tbody = document.querySelector('#tarefas-table tbody');
    
    if (tbody) {
        tbody.innerHTML = '';
        if (tarefas.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" style="text-align:center">Nenhuma tarefa encontrada.</td></tr>';
            return;
        }

        tarefas.forEach(task => {
            const row = tbody.insertRow();
            const status = task.concluida ? "✅ Feito" : "🕒 Pendente";
            
            row.innerHTML = `
                <td>${task.titulo}</td>
                <td>${task.prazo}</td>
                <td style="text-align:center">${task.empregado_id || '-'}</td>
                <td>${status}</td>
                <td><button onclick="deleteTarefa(${task.id})" style="background-color: #f44336; padding: 5px 10px; border:none; color:white; border-radius:4px; cursor:pointer;">X</button></td>
            `;
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
        alert('Tarefa Criada!');
        document.getElementById('tarefa-form').reset();
        loadTarefas();
    } else {
        alert('Erro ao criar tarefa.');
    }
}

async function deleteTarefa(id) {
    if(!confirm("Excluir tarefa?")) return;
    const res = await fetchSecure(`/tarefas/${id}`, { method: 'DELETE' });
    
    if (res && res.ok) {
        loadTarefas();
    } else {
        alert("Erro ao excluir tarefa.");
    }
}

// =======================================================
// ⚙️ UTILITÁRIOS (ABAS E ALERTAS)
// =======================================================

function setupTabs() {
    const tabs = document.querySelectorAll('.tab-btn');
    const contents = document.querySelectorAll('.tab-content');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            contents.forEach(c => c.classList.remove('active'));

            tab.classList.add('active');
            const targetId = tab.getAttribute('data-target');
            document.getElementById(targetId).classList.add('active');
        });
    });
}

const alertContainer = document.createElement('div');
alertContainer.id = 'task-alerts';

function setupAlertSystem() {
    const appScreen = document.getElementById('app-screen');
    const header = appScreen ? appScreen.querySelector('header') : null;
    if (header) {
        header.parentNode.insertBefore(alertContainer, header.nextSibling);
    }
}

function checkUrgentTasks(tarefas) {
    const pending = tarefas.filter(t => !t.concluida);
    alertContainer.innerHTML = '';
    if (pending.length > 0) {
        const div = document.createElement('div');
        div.style.cssText = "background: #ff9800; color: white; padding: 10px; margin: 10px; text-align: center; font-weight: bold; border-radius: 5px;";
        div.textContent = `🚨 Atenção: Você tem ${pending.length} tarefas pendentes.`;
        alertContainer.appendChild(div);
    }
}
