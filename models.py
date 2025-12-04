# models.py
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# Classe base para a definição das tabelas
Base = declarative_base()

class Empregado(Base):
    __tablename__ = 'empregados'
    
    id = Column(Integer, primary_key=True)
    nome = Column(String)
    cargo = Column(String)
    email = Column(String, unique=True)
    # Relação: Permite acessar as tarefas de um empregado
    tarefas = relationship("Tarefa", backref="empregado") 

    def __repr__(self):
        return f"<Empregado(id={self.id}, nome='{self.nome}', cargo='{self.cargo}')>"

class Tarefa(Base):
    __tablename__ = 'tarefas'
    
    id = Column(Integer, primary_key=True)
    titulo = Column(String)
    descricao = Column(String)
    prazo = Column(String)
    concluida = Column(Boolean, default=False)
    
    # CRÍTICO: nullable=True para permitir tarefas não atribuídas (resolve o bug de salvamento)
    empregado_id = Column(Integer, ForeignKey('empregados.id'), nullable=True) 

    def __repr__(self):
        return f"<Tarefa(id={self.id}, titulo='{self.titulo}', empregado_id={self.empregado_id})>"