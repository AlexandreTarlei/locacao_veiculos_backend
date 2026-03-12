"""Modelo Veiculo."""
import json
from sqlalchemy import Column, Integer, String, Boolean, Text, Numeric, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Veiculo(Base):
    __tablename__ = "veiculos"
    __table_args__ = (Index("ix_veiculos_disponivel", "disponivel"),)

    id = Column(Integer, primary_key=True, index=True)
    placa = Column(String(10), unique=True, nullable=False, index=True)
    id_modelo = Column(Integer, ForeignKey("modelos_veiculos.id"), nullable=True, index=True)
    ano = Column(Integer, nullable=False)
    cor = Column(String(30), nullable=False)
    quilometragem = Column(Numeric(10, 2), nullable=False, default=0)
    valor_diaria = Column(Numeric(10, 2), nullable=False)
    disponivel = Column(Boolean, default=True, nullable=False)
    fotos_json = Column(Text, nullable=True)
    data_cadastro = Column(DateTime, nullable=False, server_default=func.now())
    data_atualizacao = Column(DateTime, nullable=True, onupdate=func.now())

    # Colunas legadas para migração (nullable)
    marca = Column(String(50), nullable=True)
    modelo = Column(String(50), nullable=True)

    modelo_ref = relationship("ModeloVeiculo", back_populates="veiculos")
    locacoes = relationship("Locacao", back_populates="veiculo")
    reservas = relationship("Reserva", back_populates="veiculo")
    contratos = relationship("Contrato", back_populates="veiculo")

    @property
    def fotos(self):
        if not self.fotos_json:
            return []
        try:
            return json.loads(self.fotos_json)
        except Exception:
            return []

    @property
    def marca_nome(self):
        """Nome da marca (via modelo_ref ou coluna legada)."""
        if self.modelo_ref and self.modelo_ref.marca:
            return self.modelo_ref.marca.nome
        return self.marca or ""

    @property
    def modelo_nome(self):
        """Nome do modelo (via modelo_ref ou coluna legada)."""
        if self.modelo_ref:
            return self.modelo_ref.nome
        return self.modelo or ""
