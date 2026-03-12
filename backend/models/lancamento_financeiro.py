"""Modelo LancamentoFinanceiro."""
from sqlalchemy import Column, Integer, String, Float, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class LancamentoFinanceiro(Base):
    __tablename__ = "lancamentos_financeiros"
    id = Column(Integer, primary_key=True, index=True)
    descricao = Column(String(255), nullable=False)
    valor = Column(Float, nullable=False)
    data_lancamento = Column(Date, nullable=False)
    data_vencimento = Column(Date, nullable=True)
    data_pagamento = Column(Date, nullable=True)
    tipo = Column(String(20), nullable=False)
    id_plano_conta = Column(Integer, ForeignKey("plano_contas.id"), nullable=False)
    id_forma_pagamento = Column(Integer, ForeignKey("formas_pagamento.id"), nullable=False)
    id_locacao = Column(Integer, ForeignKey("locacoes.id"), nullable=True)
    id_pagamento = Column(Integer, ForeignKey("pagamentos.id"), nullable=True)
    pago = Column(Boolean, default=False, nullable=False)
    plano_conta = relationship("PlanoConta", backref="lancamentos")
    forma_pagamento = relationship("FormaPagamento", backref="lancamentos_financeiros")
    locacao = relationship("Locacao", backref="lancamentos_financeiros", foreign_keys=[id_locacao])
    pagamento = relationship("Pagamento", backref="lancamentos_financeiros", foreign_keys=[id_pagamento])
