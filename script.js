// ✅ URL da sua API no Render (Já atualizada com o final -1)
const API_BASE_URL = 'https://flowscheduler-app-1.onrender.com';

// --- INICIALIZAÇÃO ---
document.addEventListener('DOMContentLoaded', () => {
    // Carrega as listas assim que a página abre
    loadEmpregados();
    loadTarefas();

    // Configura os ouvintes de evento para os formulários
    // Verifica se o elemento existe antes de adicionar o listener para evitar erros
    const empregadoForm = document.getElementById('empregado-form');
    if (empregadoForm) empregadoForm.addEventListener('submit', handleCreateEmpregado);

    const tarefaForm = document.getElementById('tarefa-form');
    if (tarefaForm) tarefaForm.addEventListener('submit', handleCreateTarefa);
});

// =======================================================
// 1. LÓGICA DE EMPREGADOS (GET, POST, DELETE)
// =======================================================

async function loadEmpregados() {
    try {
        const response = await fetch(`${API_BASE_URL}/empregados/`);
        
        if (!response.ok) {
            throw new Error(`Erro ao buscar dados: ${response.status}`);
        }
        
        const empregados = await response.json();
        
        const tbody = document.querySelector('#empregados-table tbody');
        const select = document.getElementById('empregado-select'); // O Dropdown de tarefas
        
        // Limpa a tabela e o dropdown antes de preencher
        if (tbody) tbody.innerHTML = '';
        if (select) select.innerHTML = '<option value="">-- Selecione um Responsável --</option>'; 

        empregados.forEach(emp => {
            // A. Preenche a Tabela de Empregados
            if (tbody) {
                const row = tbody.insertRow();
                row.innerHTML = `
                    <td>${emp.id}</td>
                    <td>${emp.nome}</td>
                    <td>${emp.cargo}</td>
                    <td>
                        <button onclick="deleteEmpregado(${emp.id})" style="background-color: #f44336; color: white; border: none; padding: 5px 10px; cursor: pointer; border-radius: 4px;">Excluir</button>
                    </td>
                `;
            }

            // B. Preenche o Dropdown de Associação (VITAL PARA AS TAREFAS)
            if (select) {
                const option = document.createElement('option');
                option.value = emp.id; // O valor enviado pro banco será o ID
                option.textContent = `${emp.nome} (Cargo: ${emp.cargo})`; // O texto que aparece na lista
                select.appendChild(option);
            }
        });

    } catch (error) {
        console.error('Erro ao carregar empregados:', error);
        const tbody = document.querySelector('#empregados-table tbody');
        if (tbody) tbody.innerHTML = `<tr><td colspan="4">Erro de conexão: ${error.message}</td></tr>`;
    }
}

async function handleCreateEmpregado(e) {
    e.preventDefault();
    
    const nomeInput = document.getElementById('nome');
    const cargoInput = document.getElementById('cargo');
    const emailInput = document.getElementById('email');

    const data = {
        nome: nomeInput.value,
        cargo: cargoInput.value,
        email: emailInput.value
    };

    try {
        const response = await fetch(`${API_BASE_URL}/empregados/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            alert('Empregado cadastrado com sucesso!');
            // Limpa o formulário
            nomeInput.value = '';
            cargoInput.value = '';
            emailInput.value = '';
            
            loadEmpregados(); // Atualiza a tabela e o dropdown
        } else {
            const errorData = await response.json();
            alert(`Erro ao salvar: ${errorData.detail || response.statusText}`);
        }
    } catch (error) {
        console.error('Erro de rede:', error);
        alert('Erro de conexão com a API.');
    }
}

async function deleteEmpregado(id) {
    if(!confirm("Tem certeza? Isso pode apagar tarefas associadas a este usuário.")) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/empregados/${id}`, { method: 'DELETE' });
        
        if (response.ok) {
            loadEmpregados(); // Recarrega a lista
            loadTarefas();    // Recarrega tarefas (pois algumas podem ter perdido o dono)
        } else {
            alert('Erro ao excluir empregado.');
        }
    } catch (error) {
        console.error('Erro ao excluir:', error);
        alert('Erro de conexão.');
    }
}

// =======================================================
// 2. LÓGICA DE TAREFAS/FUNÇÕES (GET, POST, DELETE)
// =======================================================

async function loadTarefas() {
    try {
        const response = await fetch(`${API_BASE_URL}/tarefas/`);
        
        if (!response.ok) {
            throw new Error("Erro ao buscar tarefas");
        }

        const tarefas = await response.json();
        const tbody = document.querySelector('#tarefas-table tbody');
        
        if (tbody) {
            tbody.innerHTML = '';

            if (tarefas.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;">Nenhuma tarefa cadastrada.</td></tr>';
                return;
            }

            tarefas.forEach(task => {
                const row = tbody.insertRow();
                // Verifica status para exibição
                const status = task.concluida ? "✅ Concluída" : "🕒 Pendente";
                
                row.innerHTML = `
                    <td>${task.titulo}</td>
                    <td>${task.prazo}</td>
                    <td style="text-align: center;">${task.empregado_id ? task.empregado_id : '<span style="color:gray; font-style:italic;">Sem dono</span>'}</td>
                    <td>${status}</td>
                    <td>
                        <button onclick="deleteTarefa(${task.id})" style="background-color: #f44336; color: white; border: none; padding: 5px 10px; cursor: pointer; border-radius: 4px;">X</button>
                    </td>
                `;
            });
            
            // Checa alertas urgentes baseado nos dados carregados
            checkUrgentTasks(tarefas);
        }
    } catch (error) {
        console.error('Erro ao carregar tarefas:', error);
    }
}

async function handleCreateTarefa(e) {
    e.preventDefault();
    
    const tituloInput = document.getElementById('titulo-tarefa');
    const prazoInput = document.getElementById('prazo-tarefa');
    // Pega o ID do funcionário escolhido no menu
    const empregadoSelect = document.getElementById('empregado-select');
    const empregadoId = empregadoSelect.value;
    
    const data = {
        titulo: tituloInput.value,
        prazo: prazoInput.value,
        // Se escolheu alguém, manda o ID (número). Se não, manda null.
        empregado_id: empregadoId ? parseInt(empregadoId) : null, 
        concluida: false
    };

    try {
        const response = await fetch(`${API_BASE_URL}/tarefas/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            alert('Tarefa criada e associada com sucesso!');
            tituloInput.value = '';
            prazoInput.value = '';
            empregadoSelect.value = ''; // Reseta o select
            
            loadTarefas();
        } else {
            const errorData = await response.json();
            alert(`Erro ao criar tarefa: ${errorData.detail || 'Erro desconhecido'}`);
        }
    } catch (error) {
        console.error(error);
        alert('Erro de conexão ao criar tarefa.');
    }
}

async function deleteTarefa(id) {
    if(!confirm("Excluir esta tarefa permanentemente?")) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/tarefas/${id}`, { method: 'DELETE' });
        if (response.ok) {
            loadTarefas();
        } else {
            alert('Erro ao excluir tarefa.');
        }
    } catch (error) {
        console.error(error);
        alert('Erro de conexão.');
    }
}

// =======================================================
// 3. LÓGICA DE ALERTAS (Dashboard)
// =======================================================

// Cria o container de alerta dinamicamente
const alertContainer = document.createElement('div');
alertContainer.id = 'task-alerts';
document.addEventListener('DOMContentLoaded', () => {
    const mainElement = document.querySelector('main');
    if (mainElement) {
        document.body.insertBefore(alertContainer, mainElement);
    } else {
        document.body.appendChild(alertContainer);
    }
});

function checkUrgentTasks(tarefas) {
    if (!tarefas) return;

    const pendingTasks = tarefas.filter(t => !t.concluida);
    alertContainer.innerHTML = ''; // Limpa alertas anteriores

    if (pendingTasks.length > 0) {
        const urgencyCount = pendingTasks.length > 5 ? '5+' : pendingTasks.length;
        
        const alertBox = document.createElement('div');
        alertBox.style.cssText = `
            background-color: #ff9800; /* Laranja para alerta */
            color: white;
            padding: 15px;
            margin: 20px auto;
            text-align: center;
            max-width: 90%;
            border-radius: 8px;
            font-weight: bold;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        `;
        
        alertBox.textContent = `🚨 Painel de Controle: Existem ${urgencyCount} tarefas pendentes no sistema.`;
        alertContainer.appendChild(alertBox);
    }
}
