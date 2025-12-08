# init_db.py
from database import engine
from models import Base
import sys

try:
    print("Iniciando a criação das tabelas no banco de dados...")
    # Base.metadata.create_all lê todos os modelos definidos em models.py e cria as tabelas no DB
    Base.metadata.create_all(engine) 
    print("✅ Tabelas criadas com sucesso! O banco de dados está pronto.")

except Exception as e:
    # Se a conexão falhar ou as tabelas não puderem ser criadas (por exemplo, erro de credencial), 
    # o processo para aqui para evitar que a API suba sem DB.
    print(f"❌ Erro crítico ao criar as tabelas no banco de dados: {e}")
    sys.exit(1)
