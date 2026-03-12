"""
Configuração de conexão com banco de dados MariaDB usando SQLAlchemy.
Variáveis de ambiente via config.py.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config import DATABASE_URL

# Re-export para compatibilidade
__all__ = ["engine", "Base", "SessionLocal", "get_db", "DATABASE_URL"]

engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_size=10,
    max_overflow=20
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependência para obter sessão do banco de dados"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
