"""
Modelos SQLAlchemy - locação de veículos e controle financeiro.
Exporta todos os modelos para manter compatibilidade com "import models".
"""
from database import Base
from .marca_modelo import MarcaVeiculo, ModeloVeiculo
from .tipo_usuario import TipoUsuario
from .usuario import Usuario
from .veiculo import Veiculo
from .cliente import Cliente
from .forma_pagamento import FormaPagamento
from .plano_conta import PlanoConta
from .locacao import Locacao
from .pagamento import Pagamento
from .lancamento_financeiro import LancamentoFinanceiro
from .manutencao import Manutencao
from .manutencao_programada import ManutencaoProgramada
from .notificacao import Notificacao
from .empresa import Empresa
from .reserva import Reserva
from .contrato import Contrato

__all__ = [
    "Base",
    "MarcaVeiculo",
    "ModeloVeiculo",
    "TipoUsuario",
    "Usuario",
    "Veiculo",
    "Cliente",
    "FormaPagamento",
    "PlanoConta",
    "Locacao",
    "Pagamento",
    "LancamentoFinanceiro",
    "Manutencao",
    "ManutencaoProgramada",
    "Notificacao",
    "Empresa",
    "Reserva",
    "Contrato",
]
