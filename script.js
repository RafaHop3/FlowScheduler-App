// CRÍTICO: Substitua esta URL pelo domínio que o Railway irá fornecer.
// Exemplo: const API_BASE_URL = 'https://flow-scheduler-xxxx.up.railway.app';
const API_BASE_URL = 'http://localhost:8000'; // URL provisória para teste local

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('empregado-form');
    const loadButton = document.getElementById('load-data');

    // ------------------------------------
    // POST: Criar Novo Empregado
    // ------------------------------------
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

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
    });

    // ------------------------------------
    // GET: Carregar Lista de Empregados
    // ------------------------------------
    loadButton.addEventListener('click', loadEmpregados);

    async function loadEmpregados() {
        try {
            const response = await fetch(`${API_BASE_URL}/empregados/`);
            
            if (!response.ok) {
                throw new Error('Erro ao buscar dados da API.');
            }

            const empregados = await response.json();
            const tbody = document.querySelector('#empregados-table tbody');
            tbody.innerHTML = ''; // Limpa a tabela

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

    // Carrega a lista ao iniciar a página (se a API estiver online)
    loadEmpregados();
});
// script.js (Adicione no final)

const alertContainer = document.createElement('div');
alertContainer.id = 'task-alerts';
document.body.insertBefore(alertContainer, document.querySelector('main'));

async function checkUrgentTasks() {
    try {
        const response = await fetch(`${API_BASE_URL}/tarefas/`);
        if (!response.ok) {
            console.error("Não foi possível carregar tarefas para alerta.");
            return;
        }
        
        const tarefas = await response.json();
        
        // Simulação de lógica: Se houver tarefas, exibe um alerta simples
        const pendingTasks = tarefas.filter(t => !t.concluida);
        
        alertContainer.innerHTML = ''; // Limpa alertas anteriores

        if (pendingTasks.length > 0) {
            const urgencyCount = pendingTasks.length > 5 ? '5+ urgentes' : pendingTasks.length;
            
            // CRIAÇÃO DO ALERTA (UX)
            const alertBox = document.createElement('div');
            alertBox.style.backgroundColor = '#f44336'; // Vermelho
            alertBox.style.color = 'white';
            alertBox.style.padding = '10px';
            alertBox.style.margin = '10px auto';
            alertBox.style.textAlign = 'center';
            alertBox.style.maxWidth = '1000px';
            
            alertBox.textContent = `🚨 ATENÇÃO: Você tem ${urgencyCount} tarefas pendentes! Verifique a gestão de tarefas.`;
            alertContainer.appendChild(alertBox);
        }

    } catch (error) {
        // Ignora erros de conexão aqui, pois o loadEmpregados já lida com o erro principal
        console.warn('Alerta: Falha ao checar tarefas urgentes.');
    }
}

// Roda a checagem a cada 30 segundos
setInterval(checkUrgentTasks, 30000);

// Força a checagem imediata na inicialização
checkUrgentTasks();