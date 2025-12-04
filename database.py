from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine
from models import Base, Empregado, Tarefa
import os
from typing import Any 

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

# Cria as tabelas (se não existirem)
Base.metadata.create_all(engine) 

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

def get_tarefas(db_session: Session, skip: int = 0, limit: int = 100):
    """Lista todas as tarefas com paginação (útil para APIs)."""
    return db_session.query(Tarefa).offset(skip).limit(limit).all()

# -----------------------------------------------------------------
# --- Funções CRUD (Criação) ---
# -----------------------------------------------------------------

def create_empregado(db_session: Session, empregado_data: Any):
    """Cria e salva um novo empregado."""
    # empregado_data é um objeto Pydantic injetado pelo FastAPI
    db_empregado = Empregado(**empregado_data.dict()) 
    
    db_session.add(db_empregado)
    db_session.commit()
    db_session.refresh(db_empregado) # Recarrega para obter o ID
    return db_empregado

def create_tarefa(db_session: Session, tarefa_data: Any):
    """Cria e salva uma nova tarefa."""
    db_tarefa = Tarefa(**tarefa_data.dict())
    
    db_session.add(db_tarefa)
    db_session.commit()
    db_session.refresh(db_tarefa)
    return db_tarefa

# -----------------------------------------------------------------
# --- Funções CRUD (Atualização) ---
# -----------------------------------------------------------------

def update_empregado(db_session: Session, db_empregado: Empregado, empregado_data: Any):
    """Atualiza as informações de um empregado existente."""
    data_to_update = empregado_data.dict(exclude_unset=True) # exclude_unset ignora campos não enviados (para PATCH)
    
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

# -----------------------------------------------------------------
# --- Funções CRUD (Exclusão) ---
# -----------------------------------------------------------------

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