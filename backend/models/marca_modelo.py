"""Modelos Marca e Modelo de veículo."""
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class MarcaVeiculo(Base):
    """Marca de veículo (ex: Toyota, Honda, Fiat)."""
    __tablename__ = "marcas_veiculos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(50), nullable=False, unique=True, index=True)

    modelos = relationship("ModeloVeiculo", back_populates="marca")

    def __str__(self):
        return self.nome


class ModeloVeiculo(Base):
    """Modelo de veículo (ex: Corolla, Civic); pertence a uma marca."""
    __tablename__ = "modelos_veiculos"

    id = Column(Integer, primary_key=True, index=True)
    id_marca = Column(Integer, ForeignKey("marcas_veiculos.id"), nullable=False, index=True)
    nome = Column(String(50), nullable=False, index=True)

    marca = relationship("MarcaVeiculo", back_populates="modelos")
    veiculos = relationship("Veiculo", back_populates="modelo_ref")

    def __str__(self):
        return f"{self.marca.nome} {self.nome}" if self.marca else self.nome
