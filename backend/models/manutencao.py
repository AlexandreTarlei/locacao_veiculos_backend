"""Modelo Manutencao (registros de manutenção/gastos por veículo)."""
from datetime import date, datetime
from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base


class Manutencao(Base):
    __tablename__ = "manutencoes"

    id = Column(Integer, primary_key=True, index=True)
    id_veiculo = Column(Integer, ForeignKey("veiculos.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False, index=True)
    descricao = Column(String(255), nullable=True)
    valor = Column(Numeric(10, 2), nullable=False, default=0)
    data_manutencao = Column(Date, nullable=False)
    data_cadastro = Column(DateTime, nullable=False, server_default=func.now())

    veiculo = relationship("Veiculo", backref="manutencoes")
