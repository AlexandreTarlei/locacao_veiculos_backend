"""Modelo Pagamento."""
from datetime import datetime
from sqlalchemy import Column, Integer, Numeric, DateTime, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Pagamento(Base):
    __tablename__ = "pagamentos"
    id = Column(Integer, primary_key=True, index=True)
    id_locacao = Column(Integer, ForeignKey("locacoes.id"), nullable=False)
    id_forma_pagamento = Column(Integer, ForeignKey("formas_pagamento.id"), nullable=False)
    valor_pagamento = Column(Numeric(10, 2), nullable=False)
    data_pagamento = Column(DateTime, default=datetime.now, nullable=False)
    numero_comprovante = Column(String(50), nullable=True)
    observacoes = Column(Text, nullable=True)
    data_cadastro = Column(DateTime, nullable=False, server_default=func.now())
    data_atualizacao = Column(DateTime, nullable=True, onupdate=func.now())
    locacao = relationship("Locacao", back_populates="pagamentos")
    forma_pagamento = relationship("FormaPagamento", back_populates="pagamentos")
