"""Modelo ManutencaoProgramada (agendamentos por km e/ou data limite)."""
from datetime import date, datetime
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base


class ManutencaoProgramada(Base):
    __tablename__ = "manutencao_programada"

    id = Column(Integer, primary_key=True, index=True)
    id_veiculo = Column(Integer, ForeignKey("veiculos.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False, index=True)
    tipo_manutencao = Column(String(100), nullable=False)
    quilometragem_limite = Column(Integer, nullable=True)
    data_limite = Column(Date, nullable=True)
    ativa = Column(Boolean, nullable=False, default=True)
    data_cadastro = Column(DateTime, nullable=False, server_default=func.now())
    data_atualizacao = Column(DateTime, nullable=True, onupdate=func.now())

    veiculo = relationship("Veiculo", backref="manutencoes_programadas")
