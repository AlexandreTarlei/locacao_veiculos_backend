"""Modelo Cliente."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from database import Base


class Cliente(Base):
    __tablename__ = "clientes"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
    cpf = Column(String(14), unique=True, nullable=False, index=True)
    telefone = Column(String(20), nullable=False)
    email = Column(String(100), nullable=False)
    cep = Column(String(10), nullable=False)
    endereco = Column(String(200), nullable=False)
    data_nascimento = Column(DateTime, nullable=True)
    data_cadastro = Column(DateTime, default=datetime.now, nullable=False)
    locacoes = relationship("Locacao", back_populates="cliente")
    reservas = relationship("Reserva", back_populates="cliente")
    contratos = relationship("Contrato", back_populates="cliente")
