"""Modelo Locacao."""
from sqlalchemy import Column, Integer, Numeric, Boolean, DateTime, ForeignKey, Text, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Locacao(Base):
    __tablename__ = "locacoes"
    __table_args__ = (
        Index("ix_locacoes_ativa", "ativa"),
        Index("ix_locacoes_data_inicio", "data_inicio"),
    )
    id = Column(Integer, primary_key=True, index=True)
    id_cliente = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    id_veiculo = Column(Integer, ForeignKey("veiculos.id"), nullable=False)
    data_inicio = Column(DateTime, nullable=False)
    data_fim = Column(DateTime, nullable=False)
    dias = Column(Integer, nullable=False)
    valor_total = Column(Numeric(10, 2), nullable=False)
    multa_atraso = Column(Numeric(10, 2), default=0, nullable=False)
    ativa = Column(Boolean, default=True, nullable=False)
    observacoes = Column(Text, nullable=True)
    data_cadastro = Column(DateTime, nullable=False, server_default=func.now())
    data_atualizacao = Column(DateTime, nullable=True, onupdate=func.now())
    cliente = relationship("Cliente", back_populates="locacoes")
    veiculo = relationship("Veiculo", back_populates="locacoes")
    pagamentos = relationship("Pagamento", back_populates="locacao")
