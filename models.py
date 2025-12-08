from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Empregado(Base):
    __tablename__ = "empregados"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    cargo = Column(String)
    email = Column(String, unique=True, index=True)
    
    # Removemos senha e função para simplificar
    tarefas = relationship("Tarefa", back_populates="empregado", cascade="all, delete-orphan")

class Tarefa(Base):
    __tablename__ = "tarefas"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, index=True)
    descricao = Column(String, nullable=True)
    prazo = Column(String)
    concluida = Column(Boolean, default=False)
    
    empregado_id = Column(Integer, ForeignKey("empregados.id"), nullable=True)
    empregado = relationship("Empregado", back_populates="tarefas")
