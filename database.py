# database.py
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, desc 
from models import Base, Empregado, Tarefa 

# --- Configuração do DB ---
DATABASE_URL = 'sqlite:///flow_scheduler.db'
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine) 
Session = sessionmaker(bind=engine)

def get_session():
    """Retorna uma nova sessão do banco de dados."""
    return Session()

# --- Funções CRUD para Empregados ---
def adicionar_empregado(nome, cargo, email):
    session = get_session()
    novo_empregado = Empregado(nome=nome, cargo=cargo, email=email)
    try:
        session.add(novo_empregado)
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        print(f"Erro ao adicionar empregado: {e}")
        return False
    finally:
        session.close()

def listar_empregados():
    session = get_session()
    empregados = session.query(Empregado).all()
    session.close()
    return empregados

def buscar_empregado_por_id(empregado_id):
    session = get_session()
    empregado = session.query(Empregado).filter_by(id=empregado_id).first()
    session.close()
    return empregado

def atualizar_empregado(empregado_id, novo_nome, novo_cargo, novo_email):
    session = get_session()
    empregado = session.query(Empregado).filter_by(id=empregado_id).first()

    if empregado:
        try:
            empregado.nome = novo_nome
            empregado.cargo = novo_cargo
            empregado.email = novo_email
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Erro ao atualizar empregado {empregado_id}: {e}")
            return False
        finally:
            session.close()
    else:
        session.close()
        return False

def deletar_empregado(empregado_id):
    session = get_session()
    empregado = session.query(Empregado).filter_by(id=empregado_id).first()

    if empregado:
        try:
            session.delete(empregado)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Erro ao deletar empregado {empregado_id}: {e}")
            return False
        finally:
            session.close()
    else:
        session.close()
        return False

# --- Funções CRUD para Tarefas ---

def adicionar_tarefa(titulo, descricao, prazo, empregado_id=None):
    session = get_session()
    nova_tarefa = Tarefa(
        titulo=titulo, 
        descricao=descricao, 
        prazo=prazo, 
        empregado_id=empregado_id,
        concluida=False
    )
    try:
        session.add(nova_tarefa)
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        print(f"Erro ao adicionar tarefa: {e}")
        return False
    finally:
        session.close()

def listar_tarefas():
    session = get_session()
    tarefas = session.query(
        Tarefa.id,
        Tarefa.titulo,
        Tarefa.descricao,
        Tarefa.prazo,
        Tarefa.concluida,
        Empregado.nome.label('empregado_nome'),
        Tarefa.empregado_id
    ).outerjoin(Empregado).all()
    session.close()
    return tarefas

def buscar_tarefa_por_id(tarefa_id):
    session = get_session()
    tarefa = session.query(Tarefa).filter_by(id=tarefa_id).first()
    session.close()
    return tarefa

def atualizar_tarefa(tarefa_id, titulo, descricao, prazo, empregado_id, concluida):
    session = get_session()
    tarefa = session.query(Tarefa).filter_by(id=tarefa_id).first()

    if tarefa:
        try:
            tarefa.titulo = titulo
            tarefa.descricao = descricao
            tarefa.prazo = prazo
            tarefa.empregado_id = empregado_id if empregado_id else None
            tarefa.concluida = concluida
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Erro ao atualizar tarefa {tarefa_id}: {e}")
            return False
        finally:
            session.close()
    else:
        return False

def deletar_tarefa(tarefa_id):
    session = get_session()
    tarefa = session.query(Tarefa).filter_by(id=tarefa_id).first()

    if tarefa:
        try:
            session.delete(tarefa)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Erro ao deletar tarefa {tarefa_id}: {e}")
            return False
        finally:
            session.close()
    else:
        return False

def listar_proximas_tarefas():
    """Retorna as 5 tarefas mais urgentes (pendentes e por prazo) para o Dashboard."""
    session = get_session()

    tarefas = session.query(
        Tarefa.titulo,
        Tarefa.prazo,
        Empregado.nome.label('empregado_nome')
    ).outerjoin(Empregado).filter(
        Tarefa.concluida == False
    ).order_by(
        Tarefa.prazo.asc()
    ).limit(5).all()

    session.close()
    return tarefas
