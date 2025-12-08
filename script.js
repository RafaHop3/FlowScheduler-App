// ✅ CORREÇÃO CRÍTICA: Substituído o localhost pela URL pública do Render.
const API_BASE_URL = 'https://flowscheduler-app.onrender.com';

// Define loadEmpregados fora do DOMContentLoaded para que possa ser usada globalmente
// e para evitar erros de escopo.
async function loadEmpregados() {
    try {
        // Acessa o endpoint /empregados/
        const response = await fetch(`${API_BASE_URL}/empregados/`);
        
        // CRÍTICO: Se houver um erro, é provável que seja CORS ou API offline/erro interno.
        if (!response.ok) {
            throw new Error(`Erro ao buscar dados da API: ${response.status} - Verifique a aba Rede no console.`);
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
            // Garante que as colunas correspondem ao cabeçalho (ID, Nome, Cargo, Email)
            row.insertCell().textContent = emp.id;
            row.insertCell().textContent = emp.nome;
            row.insertCell().textContent = emp.cargo;
            row.insertCell().textContent = emp.email;
        });

    } catch (error) {
        console.error('Erro ao carregar empregados:', error);
        document.querySelector('#empregados-table tbody').innerHTML = `<tr><td colspan="4">Erro de Conexão: ${error.message}</td></tr>`;
    }
}


// --- LÓGICA PRINCIPAL (POST/GET) ---
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

        // O objeto JSON para o POST
        const data = { nome: nome, cargo: cargo, email: email }; 

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
                loadEmpregados(); // Chama a função global para atualizar a lista
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

    // Carrega a lista ao iniciar a página
    loadEmpregados();
    
    // Inicia a checagem de tarefas após o DOM estar pronto
    checkUrgentTasks();
    setInterval(checkUrgentTasks, 30000);
});


// --- LÓGICA DE ALERTA DE TAREFAS (SEÇÃO ADICIONAL) ---

// CRIA O CONTAINER DE ALERTA DINAMICAMENTE
const alertContainer = document.createElement('div');
alertContainer.id = 'task-alerts';

// Tenta inserir antes do main, mas apenas se o main existir
document.addEventListener('DOMContentLoaded', () => {
    const mainElement = document.querySelector('main');
    if (mainElement) {
        document.body.insertBefore(alertContainer, mainElement);
    } else {
        document.body.appendChild(alertContainer); // Fallback
    }
});


async function checkUrgentTasks() {
    try {
        // Acessa o endpoint /tarefas/
        const response = await fetch(`${API_BASE_URL}/tarefas/`);
        
        if (!response.ok) {
            console.warn("Não foi possível carregar tarefas para alerta (endpoint /tarefas/ retornou erro).");
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
            alertBox.style.cssText = `
                background-color: #f44336; /* Vermelho */
                color: white;
                padding: 10px;
                margin: 10px auto;
                text-align: center;
                max-width: 1000px;
                border-radius: 4px;
            `;
            
            alertBox.textContent = `🚨 ATENÇÃO: Você tem ${urgencyCount} tarefas pendentes! Verifique a gestão de tarefas.`;
            alertContainer.appendChild(alertBox);
        }

    } catch (error) {
        // Ignora erros de conexão aqui, pois o loadEmpregados já lida com o erro principal
        console.warn('Alerta: Falha ao checar tarefas urgentes. A API pode estar indisponível ou o endpoint /tarefas/ não existe.', error);
    }
}
