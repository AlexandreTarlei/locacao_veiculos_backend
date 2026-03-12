"""Modelo TipoUsuario - tipos/níveis de usuário (ADMIN, OPERACIONAL, etc.)."""
from sqlalchemy import Column, Integer, String
from database import Base


class TipoUsuario(Base):
    __tablename__ = "tipo_usuario"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    codigo = Column(String(20), unique=True, nullable=False, index=True)  # ex: ADMIN, OPERACIONAL
    nome = Column(String(50), nullable=False)  # ex: Administrador, Operacional
