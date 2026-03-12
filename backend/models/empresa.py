"""Modelo Empresa (dados da empresa para Configurações)."""
from sqlalchemy import Column, Integer, String, DateTime
from database import Base


class Empresa(Base):
    __tablename__ = "empresa"
    id = Column(Integer, primary_key=True, index=True)
    nome_fantasia = Column(String(150), nullable=True)
    razao_social = Column(String(200), nullable=True)
    cnpj = Column(String(18), nullable=True)
    endereco = Column(String(300), nullable=True)
    telefone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    status = Column(String(20), default="ativo", nullable=False)
    data_atualizacao = Column(DateTime, nullable=True, onupdate=True)
