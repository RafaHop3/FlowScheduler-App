from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import os

# Importa database e models
from database import get_db
from models import Base, Empregado, Tarefa

# --- CONFIGURAÇÃO DE SEGURANÇA ---
SECRET_KEY = "segredo-super-secreto-mude-isso-em-producao" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI(title="Flow Scheduler API (Seguro)")

# ✅ LISTA DE ORIGENS PERMITIDAS (CORS)
origins = [
    "http://localhost:8000",
    "http://127.0.0.1:5500", 
    "https://flowscheduler-app-1.onrender.com",
    "https://flow-scheduler-web.onrender.com", 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- SCHEMAS (Pydantic) ---

class EmpregadoCreate(BaseModel):
    nome: str
    cargo: str
    email: str
    senha: str 

class EmpregadoSchema(BaseModel):
    id: int
    nome: str
    cargo: str
    email: str
    funcao: str
    class Config:
        from_attributes = True

class TarefaSchema(BaseModel):
    id: int
    titulo: str
    descricao: Optional[str] = None
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

class Token(BaseModel):
    access_token: str
    token_type: str

# --- FUNÇÕES DE SEGURANÇA ---

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(Empregado).filter(Empregado.email == email).first()
    if user is None:
        raise credentials_exception
    return user

@app.get("/", tags=["Root"])
def read_root():
    # Mensagem atualizada para confirmar que o código novo subiu
    return {"message": "Flow Scheduler API Segura está online!"}

# --- ROTAS PÚBLICAS (Login e Registro) ---

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(Empregado).filter(Empregado.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.senha_hash):
        raise HTTPException(status_code=400, detail="Email ou senha incorretos")
    
    access_token = create_access_token(data={"sub": user.email, "role": user.funcao, "id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/empregados/registrar", response_model=EmpregadoSchema)
def registrar_empregado(empregado: EmpregadoCreate, db: Session = Depends(get_db)):
    if db.query(Empregado).filter(Empregado.email == empregado.email).first():
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    hashed_password = get_password_hash(empregado.senha)
    
    count = db.query(Empregado).count()
    role = "admin" if count == 0 else "user"

    novo_emp = Empregado(
        nome=empregado.nome,
        cargo=empregado.cargo,
        email=empregado.email,
        senha_hash=hashed_password,
        funcao=role
    )
    db.add(novo_emp)
    db.commit()
    db.refresh(novo_emp)
    return novo_emp

# --- ROTAS PROTEGIDAS ---

@app.get("/empregados/", response_model=List[EmpregadoSchema])
def listar_todos_empregados(db: Session = Depends(get_db), current_user: Empregado = Depends(get_current_user)):
    if current_user.funcao == "admin":
        return db.query(Empregado).all()
    else:
        return [current_user]

@app.delete("/empregados/{empregado_id}")
def deletar_empregado(empregado_id: int, db: Session = Depends(get_db), current_user: Empregado = Depends(get_current_user)):
    if current_user.funcao != "admin":
        raise HTTPException(status_code=403, detail="Apenas admins podem excluir usuários")
    
    emp = db.query(Empregado).filter(Empregado.id == empregado_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Empregado não encontrado")
        
    db.delete(emp)
    db.commit()
    return {"message": "Empregado deletado"}

# --- TAREFAS ---

@app.get("/tarefas/", response_model=List[TarefaSchema])
def listar_tarefas(db: Session = Depends(get_db), current_user: Empregado = Depends(get_current_user)):
    if current_user.funcao == "admin":
        return db.query(Tarefa).all()
    else:
        return db.query(Tarefa).filter(Tarefa.empregado_id == current_user.id).all()

@app.post("/tarefas/", response_model=TarefaSchema)
def criar_tarefa(tarefa: TarefaCreate, db: Session = Depends(get_db), current_user: Empregado = Depends(get_current_user)):
    dono_id = current_user.id
    if current_user.funcao == "admin" and tarefa.empregado_id:
        dono_id = tarefa.empregado_id
    
    nova_tarefa = Tarefa(
        titulo=tarefa.titulo,
        prazo=tarefa.prazo,
        concluida=tarefa.concluida,
        empregado_id=dono_id
    )
    db.add(nova_tarefa)
    db.commit()
    db.refresh(nova_tarefa)
    return nova_tarefa

@app.delete("/tarefas/{tarefa_id}")
def deletar_tarefa(tarefa_id: int, db: Session = Depends(get_db), current_user: Empregado = Depends(get_current_user)):
    tarefa = db.query(Tarefa).filter(Tarefa.id == tarefa_id).first()
    if not tarefa:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    
    if current_user.funcao != "admin" and tarefa.empregado_id != current_user.id:
        raise HTTPException(status_code=403, detail="Sem permissão")

    db.delete(tarefa)
    db.commit()
    return {"message": "Tarefa deletada"}
