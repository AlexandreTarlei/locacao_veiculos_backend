"""Modelo Reserva - período reservado antes da locação efetiva."""
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Index
from sqlalchemy.orm import relationship
from database import Base


class Reserva(Base):
    __tablename__ = "reservas"
    __table_args__ = (
        Index("idx_reservas_veiculo_status", "veiculo_id", "status"),
        Index("idx_reservas_datas", "data_inicio", "data_fim"),
    )
    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, nullable=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False, index=True)
    veiculo_id = Column(Integer, ForeignKey("veiculos.id"), nullable=False, index=True)
    data_inicio = Column(Date, nullable=False)
    data_fim = Column(Date, nullable=False)
    status = Column(String(20), default="reservado", nullable=False)

    cliente = relationship("Cliente", back_populates="reservas")
    veiculo = relationship("Veiculo", back_populates="reservas")
    contratos = relationship("Contrato", back_populates="reserva")
