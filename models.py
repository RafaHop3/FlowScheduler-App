from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

# Classe base para a definição das tabelas
Base = declarative_base()

class Empregado(Base):
    __tablename__ = "empregados" # ✅ Corrigido (estava 'emperegados')

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    cargo = Column(String)
    email = Column(String, unique=True, index=True) # Email único para login
    
    # --- NOVOS CAMPOS DE SEGURANÇA (CRÍTICO) ---
    senha_hash = Column(String)  # Para guardar a senha criptografada
    funcao = Column(String, default="user") # Define se é 'admin' ou 'user'

    # Relação: Permite acessar as tarefas de um empregado
    # cascade="all, delete-orphan" remove as tarefas se o empregado for deletado
    tarefas = relationship("Tarefa", back_populates="empregado", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Empregado(id={self.id}, nome='{self.nome}', cargo='{self.cargo}', funcao='{self.funcao}')>"

class Tarefa(Base):
    __tablename__ = "tarefas"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, index=True)
    descricao = Column(String, nullable=True)
    prazo = Column(String)
    concluida = Column(Boolean, default=False)
    
    # Chave Estrangeira ligando à tabela 'empregados'
    empregado_id = Column(Integer, ForeignKey("empregados.id"), nullable=True)
    
    # Relação de volta para o empregado
    empregado = relationship("Empregado", back_populates="tarefas")

    def __repr__(self):
        return f"<Tarefa(id={self.id}, titulo='{self.titulo}', empregado_id={self.empregado_id})>"
