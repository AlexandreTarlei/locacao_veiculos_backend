"""Modelo PlanoConta."""
from sqlalchemy import Column, Integer, String
from database import Base


class PlanoConta(Base):
    __tablename__ = "plano_contas"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False)
