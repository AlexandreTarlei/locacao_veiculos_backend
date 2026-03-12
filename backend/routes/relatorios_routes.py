"""
Rotas de relatórios e estatísticas.
"""
from datetime import date

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import text, extract

from database import get_db, engine
import models
from services.pdf_utils import gera_pdf_mensal, gera_pdf_vencidas

router = APIRouter(tags=["relatorios"])


@router.get("/")
def root():
    return {
        "message": "API Locação de Veículos e Controle Financeiro",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@router.get("/health")
def health():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ok", "database": "conectado"}
    except Exception as e:
        return {
            "status": "ok",
            "database": "erro",
            "detalhe": str(e),
            "dica": "Verifique se o MySQL/MariaDB está rodando e se o banco 'locacao_veiculos' existe.",
        }


def get_estatisticas(db: Session):
    """Lógica de estatísticas para uso interno (ex.: endpoint /dashboard)."""
    hoje = date.today()
    total_veiculos = db.query(models.Veiculo).count()
    veiculos_disponiveis = db.query(models.Veiculo).filter(models.Veiculo.disponivel == True).count()
    veiculos_alugados = total_veiculos - veiculos_disponiveis
    total_clientes = db.query(models.Cliente).count()
    total_locacoes = db.query(models.Locacao).count()
    locacoes_ativas = db.query(models.Locacao).filter(models.Locacao.ativa == True).count()
    total_formas = db.query(models.FormaPagamento).count()
    total_pagamentos = db.query(models.Pagamento).count()
    valor_total_pagado = db.query(models.Pagamento).with_entities(models.Pagamento.valor_pagamento).all()
    valor_pagado = sum(p[0] for p in valor_total_pagado) if valor_total_pagado else 0.0
    pagamentos_mes = (
        db.query(models.Pagamento)
        .filter(
            extract("month", models.Pagamento.data_pagamento) == hoje.month,
            extract("year", models.Pagamento.data_pagamento) == hoje.year,
        )
        .with_entities(models.Pagamento.valor_pagamento)
        .all()
    )
    receita_mes = sum(p[0] for p in pagamentos_mes) if pagamentos_mes else 0.0
    return {
        "veiculos": {
            "total": total_veiculos,
            "disponivel": veiculos_disponiveis,
            "em_uso": veiculos_alugados,
            "alugados": veiculos_alugados,
        },
        "clientes": {"total": total_clientes},
        "locacoes": {"total": total_locacoes, "ativas": locacoes_ativas, "finalizadas": total_locacoes - locacoes_ativas},
        "formas_pagamento": {"total": total_formas},
        "pagamentos": {"total_registros": total_pagamentos, "valor_total_pago": valor_pagado},
        "receita_mes": round(receita_mes, 2),
    }


@router.get("/estatisticas/")
def obter_estatisticas(db: Session = Depends(get_db)):
    return get_estatisticas(db)


@router.get("/relatorios/pdf/vencidas", response_class=Response)
def pdf_contas_vencidas(db: Session = Depends(get_db)):
    hoje = date.today()
    query = (
        db.query(models.LancamentoFinanceiro)
        .options(joinedload(models.LancamentoFinanceiro.forma_pagamento))
        .filter(
            models.LancamentoFinanceiro.pago == False,
            models.LancamentoFinanceiro.data_vencimento.isnot(None),
            models.LancamentoFinanceiro.data_vencimento < hoje,
        )
        .order_by(models.LancamentoFinanceiro.data_vencimento.asc())
    )
    rows = query.all()
    plano_ids = {r.id_plano_conta for r in rows if r.id_plano_conta}
    plano_nomes = {}
    if plano_ids:
        planos = db.query(models.PlanoConta).filter(models.PlanoConta.id.in_(plano_ids)).all()
        plano_nomes = {p.id: p.nome for p in planos}
    registros = [
        {
            "descricao": r.descricao,
            "valor": r.valor,
            "data_vencimento": r.data_vencimento,
            "plano_conta": plano_nomes.get(r.id_plano_conta),
            "forma_pagamento": r.forma_pagamento.nome if r.forma_pagamento else None,
        }
        for r in rows
    ]
    pdf_bytes = gera_pdf_vencidas(registros)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=contas_vencidas.pdf"},
    )


@router.get("/relatorios/pdf/mensal", response_class=Response)
def pdf_relatorio_mensal(db: Session = Depends(get_db)):
    hoje = date.today()
    query = (
        db.query(models.LancamentoFinanceiro)
        .filter(
            extract("month", models.LancamentoFinanceiro.data_lancamento) == hoje.month,
            extract("year", models.LancamentoFinanceiro.data_lancamento) == hoje.year,
        )
        .order_by(models.LancamentoFinanceiro.data_lancamento.asc())
    )
    rows = query.all()
    registros = [
        {"data_lancamento": r.data_lancamento, "descricao": r.descricao, "valor": r.valor}
        for r in rows
    ]
    pdf_bytes = gera_pdf_mensal(registros)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=relatorio_mensal.pdf"},
    )
