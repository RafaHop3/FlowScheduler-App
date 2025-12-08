# init_db.py - Script para criar as tabelas no PostgreSQL
from database import engine
from models import Base
from sqlalchemy import text
import sys

try:
    print("Iniciando a criação das tabelas no banco de dados...")
    Base.metadata.create_all(engine)
    print("✅ Tabelas criadas com sucesso! O banco de dados está pronto.")

except Exception as e:
    print(f"❌ Erro ao criar as tabelas no banco de dados: {e}")
    sys.exit(1)
