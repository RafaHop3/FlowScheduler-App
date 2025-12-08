# initial_setup.py (CORRIGIDO)

from database import Base, engine
from models import Empregado, Tarefa # Importa os modelos para garantir que Base os conheça
import os
import subprocess
import time

def create_db_tables():
    """Tenta criar todas as tabelas no banco de dados, esperando o PostgreSQL ficar pronto."""
    print("Iniciando a verificação/criação das tabelas no banco de dados...")
    
    # Tenta a conexão por algumas vezes, dando tempo para o PostgreSQL inicializar.
    max_retries = 5
    for i in range(max_retries):
        try:
            # Tenta criar todas as tabelas definidas em models.py
            Base.metadata.create_all(bind=engine)
            print("Tabelas criadas ou já existentes. Configuração do DB finalizada.")
            return # Sai da função se for bem-sucedido
        except Exception as e:
            if i < max_retries - 1:
                print(f"Tentativa {i+1} falhou ao conectar ao DB. Erro: {e}. Aguardando 5 segundos...")
                time.sleep(5)
            else:
                print(f"ERRO CRÍTICO: Não foi possível conectar ao DB após {max_retries} tentativas.")
                raise e # Falha se todas as tentativas falharem

def start_server():
    """Inicia o servidor Uvicorn após garantir que o DB está pronto."""
    print("Iniciando o servidor FastAPI...")
    
    # CORREÇÃO CRÍTICA: Adicionado "python" e "-m" para rodar 'uvicorn' como módulo.
    command = [
        "python", "-m", "uvicorn", 
        "main:app", 
        "--host", "0.0.0.0", 
        "--port", os.environ.get("PORT", "8000"), # Usa a variável $PORT do Railway
        "--workers", "4"
    ]
    
    # Executa o comando e substitui o processo atual (necessário para o Procfile)
    subprocess.run(command) 

if __name__ == "__main__":
    create_db_tables()
    start_server()