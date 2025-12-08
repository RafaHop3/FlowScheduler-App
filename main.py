from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

# Importa funções de persistência e injeção de dependência
from database import (
    get_db, 
    get_empregados, get_empregado_by_id, create_empregado, update_empregado, delete_empregado,
    get_tarefas, get_tarefa_by_id, create_tarefa, update_tarefa, delete_tarefa,
    get_tarefas_by_empregado_id
)

# -----------------------------------------------------------------
# --- Schemas de Saída (Output) ---
# -----------------------------------------------------------------

class EmpregadoSchema(BaseModel):
    id: int
    nome: str
    cargo: str
    email: str
    
    class Config:
        from_attributes = True # ✅ CORREÇÃO: Pydantic V2 usa from_attributes
        # orm_mode = True # <-- Remova esta linha se estiver usando Pydantic V2

class TarefaSchema(BaseModel):
    id: int
    titulo: str
    descricao: Optional[str] = None
    prazo: str
    empregado_id: Optional[int] = None
    concluida: bool = False
    
    class Config:
        from_attributes = True # ✅ CORREÇÃO: Pydantic V2 usa from_attributes
        # orm_mode = True # <-- Remova esta linha se estiver usando Pydantic V2

# -----------------------------------------------------------------
# --- Schemas de Entrada (Input) e Atualização ---
# (Manter como estava, pois não usam orm_mode)
# -----------------------------------------------------------------

class EmpregadoCreate(BaseModel):
    nome: str
    cargo: str
    email: str

class TarefaBase(BaseModel):
    titulo: str
    descricao: Optional[str] = None
    prazo: str
    empregado_id: Optional[int] = None
    concluida: bool = False

class EmpregadoUpdate(BaseModel):
    nome: Optional[str] = None
    cargo: Optional[str] = None
    email: Optional[str] = None

class TarefaUpdate(BaseModel):
    titulo: Optional[str] = None
    descricao: Optional[str] = None
    prazo: Optional[str] = None
    empregado_id: Optional[int] = None
    concluida: Optional[bool] = None


# -----------------------------------------------------------------
# --- Configuração do FastAPI (CORS CRÍTICO) ---
# -----------------------------------------------------------------

app = FastAPI(title="Flow Scheduler API")

# Defina a URL onde o frontend está sendo executado (pode ser o Render Static Site ou localhost)
# Mantenha o localhost para testes locais.
origins = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:5500", # Exemplo comum de Live Server
    "https://flowscheduler-app.onrender.com", # Necessário para o Render Docs/Health Checks
    # ADICIONE AQUI A URL DO SEU FRONTEND HOSPEDADO (SE APLICÁVEL)
    # Exemplo: "https://flow-scheduler-frontend-xxxx.onrender.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)
# -----------------------------------------------------------------


@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Flow Scheduler API está online! Acesse /docs para a documentação."}


# -----------------------------------------------------------------
# --- Endpoints de Empregados (CRUD Completo) ---
# -----------------------------------------------------------------

@app.get("/empregados/", response_model=List[EmpregadoSchema], tags=["Empregados"])
def listar_empregados_api(db: Session = Depends(get_db)):
    """[GET] Lista todos os empregados cadastrados."""
    return get_empregados(db)

@app.post("/empregados/", response_model=EmpregadoSchema, tags=["Empregados"], status_code=201)
def criar_empregado_api(empregado: EmpregadoCreate, db: Session = Depends(get_db)):
    """[POST] Cria um novo empregado."""
    return create_empregado(db, empregado)

@app.put("/empregados/{empregado_id}", response_model=EmpregadoSchema, tags=["Empregados"])
def atualizar_empregado_api(empregado_id: int, empregado: EmpregadoUpdate, db: Session = Depends(get_db)):
    """[PUT] Atualiza TODAS as informações de um empregado."""
    db_empregado = get_empregado_by_id(db, empregado_id)
    if not db_empregado:
        raise HTTPException(status_code=404, detail="Empregado não encontrado.")
        
    return update_empregado(db, db_empregado, empregado)

@app.delete("/empregados/{empregado_id}", tags=["Empregados"])
def deletar_empregado_api(empregado_id: int, db: Session = Depends(get_db)):
    """[DELETE] Deleta um empregado pelo ID."""
    db_empregado = get_empregado_by_id(db, empregado_id)
    if not db_empregado:
        raise HTTPException(status_code=404, detail="Empregado não encontrado.")
        
    return delete_empregado(db, db_empregado)


# -----------------------------------------------------------------
# --- Endpoints de Tarefas (CRUD Completo) ---
# -----------------------------------------------------------------

@app.get("/tarefas/", response_model=List[TarefaSchema], tags=["Tarefas"])
def listar_tarefas_api(db: Session = Depends(get_db)):
    """[GET] Lista todas as tarefas."""
    return get_tarefas(db)

# --- NOVO ENDPOINT DE FILTRO POR EMPREGADO ---

@app.get("/tarefas/empregado/{empregado_id}", response_model=List[TarefaSchema], tags=["Tarefas"])
def listar_tarefas_por_empregado_api(empregado_id: int, db: Session = Depends(get_db)):
    """[GET] Lista todas as tarefas atribuídas a um empregado específico."""
    
    # 1. Checa se o empregado existe
    if not get_empregado_by_id(db, empregado_id):
        raise HTTPException(status_code=404, detail="Empregado não encontrado.")
    
    # 2. Busca as tarefas usando a nova função no database.py
    tarefas = get_tarefas_by_empregado_id(db, empregado_id)
    return tarefas

# ---------------------------------------------

@app.post("/tarefas/", response_model=TarefaSchema, tags=["Tarefas"], status_code=201)
def criar_tarefa_api(tarefa: TarefaBase, db: Session = Depends(get_db)):
    """[POST] Cria uma nova tarefa."""
    
    # Validação: Se um empregado_id é fornecido, ele deve existir
    if tarefa.empregado_id:
        if not get_empregado_by_id(db, tarefa.empregado_id):
            raise HTTPException(status_code=404, detail="Empregado_id não encontrado.")
            
    return create_tarefa(db, tarefa)

@app.put("/tarefas/{tarefa_id}", response_model=TarefaSchema, tags=["Tarefas"])
def atualizar_tarefa_api(tarefa_id: int, tarefa: TarefaUpdate, db: Session = Depends(get_db)):
    """[PUT] Atualiza TODAS as informações de uma tarefa."""
    db_tarefa = get_tarefa_by_id(db, tarefa_id)
    if not db_tarefa:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada.")
    
    # Validação de FK
    if tarefa.empregado_id is not None:
        if not get_empregado_by_id(db, tarefa.empregado_id):
            raise HTTPException(status_code=404, detail="Empregado_id não encontrado para atribuição.")

    return update_tarefa(db, db_tarefa, tarefa)

@app.delete("/tarefas/{tarefa_id}", tags=["Tarefas"])
def deletar_tarefa_api(tarefa_id: int, db: Session = Depends(get_db)):
    """[DELETE] Deleta uma tarefa pelo ID."""
    db_tarefa = get_tarefa_by_id(db, tarefa_id)
    if not db_tarefa:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada.")
        
    return delete_tarefa(db, db_tarefa)
