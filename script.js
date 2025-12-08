// script.js

// CRÍTICO: Substitua esta URL pelo domínio que o Railway irá fornecer.
// Exemplo: const API_BASE_URL = 'https://flow-scheduler-xxxx.up.railway.app';
const API_BASE_URL = 'http://localhost:8000'; // URL provisória para teste local

const alertContainer = document.createElement('div');
alertContainer.id = 'task-alerts';
// Insere o container de alertas no corpo, antes do conteúdo principal
document.body.insertBefore(alertContainer, document.querySelector('main'));


// =================================================================
// 1. FUNÇÕES DE ACESSO À API (GET / POST)
// =================================================================

/**
 * [GET] Carrega a lista de empregados e preenche a tabela.
 */
async function loadEmpregados() {
    const tbody = document.querySelector('#empregados-table tbody');
    tbody.innerHTML = ''; // Limpa a tabela

    try {
        const response = await fetch(`${API_BASE_URL}/empregados/`);
        
        if (!response.ok) {
            throw new Error(`Erro ${response.status}: Falha ao buscar dados da API.`);
        }

        const empregados = await response.json();

        if (empregados.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4">Nenhum empregado cadastrado.</td></tr>';
            return;
        }

        empregados.forEach(emp => {
            const row = tbody.insertRow();
            row.insertCell().textContent = emp.id;
            row.insertCell().textContent = emp.nome;
            row.insertCell().textContent = emp.cargo;
            row.insertCell().textContent = emp.email;
        });

    } catch (error) {
        console.error('Erro ao carregar empregados:', error);
        document.querySelector('#empregados-table tbody').innerHTML = `<tr><td colspan="4">Erro: ${error.message}</td></tr>`;
    }
}


/**
 * [POST] Envia dados do novo empregado para a API.
 */
async function submitNewEmpregado(e) {
    e.preventDefault();

    const form = document.getElementById('empregado-form');
    const nome = document.getElementById('nome').value;
    const cargo = document.getElementById('cargo').value;
    const email = document.getElementById('email').value;

    const data = { nome, cargo, email };

    try {
        const response = await fetch(`${API_BASE_URL}/empregados/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });

        if (response.ok) {
            alert("Empregado salvo com sucesso!");
            form.reset();
            loadEmpregados(); // Recarrega a lista após o sucesso
        } else {
            const error = await response.json();
            alert(`Falha ao salvar: ${error.detail || response.statusText}`);
        }
    } catch (error) {
        console.error('Erro de rede:', error);
        alert("Erro de conexão com a API.");
    }
}


// =================================================================
// 2. FUNÇÃO DE ALERTA DE TAREFAS (UX)
// =================================================================

/**
 * [GET] Checa se há tarefas pendentes e exibe um alerta.
 */
async function checkUrgentTasks() {
    try {
        // Nota: Idealmente, usaríamos um endpoint como /tarefas/pendentes/urgentes
        const response = await fetch(`${API_BASE_URL}/tarefas/`); 
        if (!response.ok) {
            console.error("Não foi possível carregar tarefas para alerta.");
            return;
        }
        
        const tarefas = await response.json();
        
        const pendingTasks = tarefas.filter(t => !t.concluida);
        
        alertContainer.innerHTML = ''; // Limpa alertas anteriores

        if (pendingTasks.length > 0) {
            const urgencyCount = pendingTasks.length > 5 ? 'mais de 5' : pendingTasks.length;
            
            // CRIAÇÃO DO ALERTA (UX)
            const alertBox = document.createElement('div');
            alertBox.style.cssText = 'background-color: #f44336; color: white; padding: 10px; margin: 10px auto; text-align: center; max-width: 1000px; border-radius: 5px;';
            
            alertBox.textContent = `🚨 ATENÇÃO: Você tem ${urgencyCount} tarefas pendentes! Verifique a gestão de tarefas.`;
            alertContainer.appendChild(alertBox);
        }

    } catch (error) {
        console.warn('Alerta: Falha ao checar tarefas urgentes. Rede ou API fora do ar.');
    }
}


// =================================================================
// 3. INICIALIZAÇÃO DA PÁGINA
// =================================================================

document.addEventListener('DOMContentLoaded', () => {
    // Liga os event listeners
    document.getElementById('empregado-form').addEventListener('submit', submitNewEmpregado);
    document.getElementById('load-data').addEventListener('click', loadEmpregados);
    
    // Inicializa a lista de empregados
    loadEmpregados();
    
    // Inicializa o sistema de alerta de tarefas
    checkUrgentTasks();
    // Roda a checagem de tarefas a cada 30 segundos
    setInterval(checkUrgentTasks, 30000);
});