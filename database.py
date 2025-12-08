from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine
from models import Base, Empregado, Tarefa
import os
from typing import Any, List

# --- Configuração do DB ---

# CRÍTICO: Usa a variável de ambiente DATABASE_URL do Railway. 
# Localmente, usa SQLite.
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///flow_scheduler.db")

# Criação do Engine
engine = create_engine(
    DATABASE_URL, 
    # Necessário apenas para SQLite: check_same_thread=False
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {} 
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Funções de Injeção de Dependência ---

def get_db():
    """Retorna uma sessão do banco de dados que será fechada automaticamente pelo FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
# -----------------------------------------------------------------
# --- Funções CRUD (Busca e Leitura) ---
# -----------------------------------------------------------------

def get_empregado_by_id(db_session: Session, empregado_id: int):
    """Busca um empregado pelo ID."""
    return db_session.query(Empregado).filter(Empregado.id == empregado_id).first()

def get_empregados(db_session: Session):
    """Lista todos os empregados."""
    return db_session.query(Empregado).all()

def get_tarefa_by_id(db_session: Session, tarefa_id: int):
    """Busca uma tarefa pelo ID."""
    return db_session.query(Tarefa).filter(Tarefa.id == tarefa_id).first()

def get_tarefas(db_session: Session, skip: int = 0, limit: int = 100) -> List[Tarefa]:
    """
    Lista todas as tarefas com paginação, OTIMIZADO para incluir o nome do empregado 
    no objeto Tarefa antes de ser serializado pela API.
    """
    # Faz um LEFT OUTER JOIN para incluir o nome do empregado (mesmo que seja NULO)
    tarefas_com_empregado = db_session.query(
        Tarefa, 
        Empregado.nome.label('empregado_nome') # Renomeia o campo nome do empregado
    ).outerjoin(
        Empregado, Tarefa.empregado_id == Empregado.id
    ).offset(skip).limit(limit).all()

    # Mapeia o resultado do JOIN para um objeto Tarefa com o atributo 'empregado_nome'
    resultado = []
    for tarefa, empregado_nome in tarefas_com_empregado:
        # Adiciona o nome do empregado dinamicamente ao objeto Tarefa para serialização (Pydantic)
        setattr(tarefa, 'empregado_nome', empregado_nome)
        resultado.append(tarefa)
        
    return resultado

# --- NOVAS FUNÇÕES DE LEITURA E RELATÓRIO ---

def get_tarefas_by_empregado_id(db_session: Session, empregado_id: int):
    """Lista todas as tarefas atribuídas a um empregado específico."""
    return db_session.query(Tarefa).filter(Tarefa.empregado_id == empregado_id).all()

def listar_proximas_tarefas(db_session: Session = SessionLocal()):
    """
    Lista tarefas pendentes (limitado a 5), ordenadas por prazo. 
    Inclui o nome do empregado responsável para exibição no Dashboard.
    """
    # Esta função já estava correta e realiza o JOIN necessário
    tarefas_com_empregado = db_session.query(
        Tarefa, 
        Empregado.nome.label('empregado_nome')
    ).outerjoin(
        Empregado, Tarefa.empregado_id == Empregado.id
    ).filter(
        Tarefa.concluida == False
    ).order_by(
        Tarefa.prazo.asc()
    ).limit(5).all()

    resultado = []
    for tarefa, empregado_nome in tarefas_com_empregado:
        setattr(tarefa, 'empregado_nome', empregado_nome)
        resultado.append(tarefa)
        
    return resultado

# -----------------------------------------------------------------
# --- Funções CRUD (Criação, Atualização, Exclusão) (INALTERADAS) ---
# -----------------------------------------------------------------

def create_empregado(db_session: Session, empregado_data: Any):
    """Cria e salva um novo empregado."""
    db_empregado = Empregado(**empregado_data.dict()) 
    db_session.add(db_empregado)
    db_session.commit()
    db_session.refresh(db_empregado)
    return db_empregado

def create_tarefa(db_session: Session, tarefa_data: Any):
    """Cria e salva uma nova tarefa."""
    db_tarefa = Tarefa(**tarefa_data.dict())
    db_session.add(db_tarefa)
    db_session.commit()
    db_session.refresh(db_tarefa)
    return db_tarefa

def update_empregado(db_session: Session, db_empregado: Empregado, empregado_data: Any):
    """Atualiza as informações de um empregado existente."""
    data_to_update = empregado_data.dict(exclude_unset=True)
    for key, value in data_to_update.items():
        setattr(db_empregado, key, value)
    db_session.commit()
    db_session.refresh(db_empregado)
    return db_empregado

def update_tarefa(db_session: Session, db_tarefa: Tarefa, tarefa_data: Any):
    """Atualiza uma tarefa existente."""
    data_to_update = tarefa_data.dict(exclude_unset=True)
    for key, value in data_to_update.items():
        setattr(db_tarefa, key, value)
    db_session.commit()
    db_session.refresh(db_tarefa)
    return db_tarefa

def delete_empregado(db_session: Session, db_empregado: Empregado):
    """Deleta um empregado."""
    db_session.delete(db_empregado)
    db_session.commit()
    return {"message": "Empregado deletado com sucesso"}

def delete_tarefa(db_session: Session, db_tarefa: Tarefa):
    """Deleta uma tarefa."""
    db_session.delete(db_tarefa)
    db_session.commit()
    return {"message": "Tarefa deletada com sucesso"}