"""
Configuração de conexão com banco de dados MariaDB usando SQLAlchemy
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configuração de conexão com MariaDB
# Format: mysql+pymysql://user:password@host:port/database
DATABASE_URL = "mysql+pymysql://root:@localhost:3307/locacao_veiculos"

# Criar engine da SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Mude para True para ver as queries SQL
    pool_size=10,
    max_overflow=20
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
