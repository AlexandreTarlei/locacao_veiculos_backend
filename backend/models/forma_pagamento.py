"""Modelo FormaPagamento."""
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from database import Base


class FormaPagamento(Base):
    __tablename__ = "formas_pagamento"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(50), nullable=False, unique=True, index=True)
    descricao = Column(String(200), nullable=True)
    ativa = Column(Boolean, default=True, nullable=False)
    pagamentos = relationship("Pagamento", back_populates="forma_pagamento")
