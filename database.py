# database.py

def adicionar_tarefa(titulo, descricao, prazo, empregado_id=None):
    """Cria e salva uma nova tarefa, opcionalmente atribuindo um empregado."""
    session = get_session()
    nova_tarefa = Tarefa(
        titulo=titulo, 
        descricao=descricao, 
        prazo=prazo, 
        empregado_id=empregado_id, # <--- VERIFIQUE ESTE PARÂMETRO
        concluida=False
    )
    try:
        session.add(nova_tarefa)
        session.commit() # <--- O commit deve estar aqui
        return True
    except Exception as e:
        session.rollback()
        # CRÍTICO: Imprima o erro para ver o que está acontecendo
        print(f"Erro ao adicionar tarefa: {e}") 
        return False
    finally:
        session.close()
