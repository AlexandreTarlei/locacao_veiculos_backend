"""
Configuração de conexão com banco de dados MySQL/MariaDB usando SQLAlchemy
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Senha do banco: use variável de ambiente MYSQL_PASSWORD ou deixe vazia
_db_password = os.environ.get("MYSQL_PASSWORD", "")
_user = os.environ.get("MYSQL_USER", "root")
_host = os.environ.get("MYSQL_HOST", "localhost")
_port = os.environ.get("MYSQL_PORT", "3307")
_database = os.environ.get("MYSQL_DATABASE", "locacao_veiculos")
DATABASE_URL = f"mysql+pymysql://{_user}:{_db_password}@{_host}:{_port}/{_database}"

# Criar engine da SQLAlchemy (connect_timeout evita travar se o MySQL estiver inacessível)
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Mude para True para ver as queries SQL
    pool_size=10,
    max_overflow=20,
    connect_args={"connect_timeout": 10},
)

# Criar session local
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para os modelos
Base = declarative_base()

def get_db():
    """Dependência para obter sessão do banco de dados"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
