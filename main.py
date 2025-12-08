from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from database import get_db
from models import Base, Empregado, Tarefa

app = FastAPI(title="Flow Scheduler API (Open)")

# Configuração CORS (Permite tudo para evitar dor de cabeça)
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- SCHEMAS ---
class EmpregadoSchema(BaseModel):
    id: int
    nome: str
    cargo: str
    email: str
    class Config:
        from_attributes = True

class EmpregadoCreate(BaseModel):
    nome: str
    cargo: str
    email: str

class TarefaSchema(BaseModel):
    id: int
    titulo: str
    prazo: str
    empregado_id: Optional[int] = None
    concluida: bool = False
    class Config:
        from_attributes = True

class TarefaCreate(BaseModel):
    titulo: str
    prazo: str
    empregado_id: Optional[int] = None
    concluida: bool = False

@app.get("/")
def read_root():
    return {"message": "API Rodando sem Login (Modo Demonstração)"}

# --- ROTAS EMPREGADOS ---

@app.get("/empregados/", response_model=List[EmpregadoSchema])
def listar_empregados(db: Session = Depends(get_db)):
    return db.query(Empregado).all()

@app.post("/empregados/", response_model=EmpregadoSchema)
def criar_empregado(empregado: EmpregadoCreate, db: Session = Depends(get_db)):
    db_emp = Empregado(nome=empregado.nome, cargo=empregado.cargo, email=empregado.email)
    db.add(db_emp)
    db.commit()
    db.refresh(db_emp)
    return db_emp

@app.delete("/empregados/{empregado_id}")
def deletar_empregado(empregado_id: int, db: Session = Depends(get_db)):
    emp = db.query(Empregado).filter(Empregado.id == empregado_id).first()
    if emp:
        db.delete(emp)
        db.commit()
    return {"message": "Deletado"}

# --- ROTAS TAREFAS ---

@app.get("/tarefas/", response_model=List[TarefaSchema])
def listar_tarefas(db: Session = Depends(get_db)):
    return db.query(Tarefa).all()

@app.post("/tarefas/", response_model=TarefaSchema)
def criar_tarefa(tarefa: TarefaCreate, db: Session = Depends(get_db)):
    nova_tarefa = Tarefa(
        titulo=tarefa.titulo, 
        prazo=tarefa.prazo, 
        concluida=tarefa.concluida,
        empregado_id=tarefa.empregado_id
    )
    db.add(nova_tarefa)
    db.commit()
    db.refresh(nova_tarefa)
    return nova_tarefa

@app.delete("/tarefas/{tarefa_id}")
def deletar_tarefa(tarefa_id: int, db: Session = Depends(get_db)):
    t = db.query(Tarefa).filter(Tarefa.id == tarefa_id).first()
    if t:
        db.delete(t)
        db.commit()
    return {"message": "Deletada"}
