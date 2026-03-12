"""Modelo Contrato - contrato de locação (valores, status; pode vincular a reserva)."""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Contrato(Base):
    __tablename__ = "contratos"
    __table_args__ = (
        Index("idx_contratos_reserva", "reserva_id"),
        Index("idx_contratos_status", "status"),
    )
    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, nullable=True, index=True)
    reserva_id = Column(Integer, ForeignKey("reservas.id"), nullable=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False, index=True)
    veiculo_id = Column(Integer, ForeignKey("veiculos.id"), nullable=False, index=True)
    valor_diaria = Column(Numeric(10, 2), nullable=True)
    valor_total = Column(Numeric(10, 2), nullable=True)
    status = Column(String(20), default="ativo", nullable=False)
    data_contrato = Column(DateTime, nullable=False, server_default=func.now())

    reserva = relationship("Reserva", back_populates="contratos")
    cliente = relationship("Cliente", back_populates="contratos")
    veiculo = relationship("Veiculo", back_populates="contratos")
