"""
Rotas do módulo financeiro (lançamentos e plano de contas).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from datetime import date
from typing import List, Optional
from pydantic import BaseModel

from database import get_db
import models

router = APIRouter(tags=["financeiro"])


class LancamentoCreate(BaseModel):
    descricao: str
    valor: float
    data_lancamento: date
    data_vencimento: Optional[date] = None
    data_pagamento: Optional[date] = None
    tipo: str
    plano_conta_id: int
    forma_pagamento_id: int
    pago: bool = False


class LancamentoUpdate(BaseModel):
    descricao: Optional[str] = None
    valor: Optional[float] = None
    data_lancamento: Optional[date] = None
    data_vencimento: Optional[date] = None
    data_pagamento: Optional[date] = None
    tipo: Optional[str] = None
    plano_conta_id: Optional[int] = None
    forma_pagamento_id: Optional[int] = None
    pago: Optional[bool] = None


class LancamentoResponse(BaseModel):
    id: int
    descricao: str
    valor: float
    data_lancamento: date
    data_vencimento: Optional[date] = None
    data_pagamento: Optional[date] = None
    tipo: str
    plano_conta_id: int
    forma_pagamento_id: int
    pago: bool

    class Config:
        from_attributes = True


class LancamentoListResponse(LancamentoResponse):
    plano_conta: Optional[str] = None
    forma_pagamento: Optional[str] = None


class PlanoContaResponse(BaseModel):
    id: int
    nome: str

    class Config:
        from_attributes = True


class PlanoContaCreate(BaseModel):
    nome: str


@router.get("/plano-contas/", response_model=List[PlanoContaResponse])
def listar_plano_contas(db: Session = Depends(get_db)):
    return db.query(models.PlanoConta).order_by(models.PlanoConta.nome).all()


@router.post("/plano-contas/", response_model=PlanoContaResponse, status_code=status.HTTP_201_CREATED)
def criar_plano_conta(plano: PlanoContaCreate, db: Session = Depends(get_db)):
    nome = plano.nome.strip()
    if not nome:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nome do plano de conta é obrigatório")
    existente = db.query(models.PlanoConta).filter(models.PlanoConta.nome == nome).first()
    if existente:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Plano de conta '{nome}' já existe")
    novo = models.PlanoConta(nome=nome)
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo


@router.post("/financeiro", response_model=LancamentoResponse, status_code=status.HTTP_201_CREATED)
def criar_lancamento(lancamento: LancamentoCreate, db: Session = Depends(get_db)):
    forma = db.query(models.FormaPagamento).filter(models.FormaPagamento.id == lancamento.forma_pagamento_id).first()
    if not forma:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Forma de pagamento não encontrada")
    novo = models.LancamentoFinanceiro(
        descricao=lancamento.descricao,
        valor=lancamento.valor,
        data_lancamento=lancamento.data_lancamento,
        data_vencimento=lancamento.data_vencimento,
        data_pagamento=lancamento.data_pagamento,
        tipo=lancamento.tipo,
        id_plano_conta=lancamento.plano_conta_id,
        id_forma_pagamento=lancamento.forma_pagamento_id,
        pago=lancamento.pago,
    )
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return LancamentoResponse(
        id=novo.id,
        descricao=novo.descricao,
        valor=novo.valor,
        data_lancamento=novo.data_lancamento,
        data_vencimento=novo.data_vencimento,
        data_pagamento=novo.data_pagamento,
        tipo=novo.tipo,
        plano_conta_id=novo.id_plano_conta,
        forma_pagamento_id=novo.id_forma_pagamento,
        pago=novo.pago,
    )


@router.get("/financeiro", response_model=List[LancamentoListResponse])
def listar_lancamentos(
    tipo: Optional[str] = None,
    plano_conta_id: Optional[int] = None,
    forma_pagamento_id: Optional[int] = None,
    pago: Optional[bool] = None,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    query = (
        db.query(models.LancamentoFinanceiro)
        .options(joinedload(models.LancamentoFinanceiro.forma_pagamento))
    )
    if tipo is not None:
        query = query.filter(models.LancamentoFinanceiro.tipo == tipo)
    if plano_conta_id is not None:
        query = query.filter(models.LancamentoFinanceiro.id_plano_conta == plano_conta_id)
    if forma_pagamento_id is not None:
        query = query.filter(models.LancamentoFinanceiro.id_forma_pagamento == forma_pagamento_id)
    if pago is not None:
        query = query.filter(models.LancamentoFinanceiro.pago == pago)
    if data_inicio is not None:
        query = query.filter(models.LancamentoFinanceiro.data_lancamento >= data_inicio)
    if data_fim is not None:
        query = query.filter(models.LancamentoFinanceiro.data_lancamento <= data_fim)
    query = query.order_by(models.LancamentoFinanceiro.data_lancamento.desc())
    rows = query.limit(limit).all()

    plano_ids = {r.id_plano_conta for r in rows}
    plano_nomes = {}
    if plano_ids:
        planos = db.query(models.PlanoConta).filter(models.PlanoConta.id.in_(plano_ids)).all()
        plano_nomes = {p.id: p.nome for p in planos}

    return [
        LancamentoListResponse(
            id=r.id,
            descricao=r.descricao,
            valor=r.valor,
            data_lancamento=r.data_lancamento,
            data_vencimento=r.data_vencimento,
            data_pagamento=r.data_pagamento,
            tipo=r.tipo,
            plano_conta_id=r.id_plano_conta,
            forma_pagamento_id=r.id_forma_pagamento,
            pago=r.pago,
            plano_conta=plano_nomes.get(r.id_plano_conta),
            forma_pagamento=r.forma_pagamento.nome if r.forma_pagamento else None,
        )
        for r in rows
    ]


@router.get("/financeiro/vencidas", response_model=List[LancamentoListResponse])
def contas_vencidas(db: Session = Depends(get_db)):
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
    plano_ids = {r.id_plano_conta for r in rows}
    plano_nomes = {}
    if plano_ids:
        planos = db.query(models.PlanoConta).filter(models.PlanoConta.id.in_(plano_ids)).all()
        plano_nomes = {p.id: p.nome for p in planos}
    return [
        LancamentoListResponse(
            id=r.id,
            descricao=r.descricao,
            valor=r.valor,
            data_lancamento=r.data_lancamento,
            data_vencimento=r.data_vencimento,
            data_pagamento=r.data_pagamento,
            tipo=r.tipo,
            plano_conta_id=r.id_plano_conta,
            forma_pagamento_id=r.id_forma_pagamento,
            pago=r.pago,
            plano_conta=plano_nomes.get(r.id_plano_conta),
            forma_pagamento=r.forma_pagamento.nome if r.forma_pagamento else None,
        )
        for r in rows
    ]


@router.get("/financeiro/{lancamento_id}", response_model=LancamentoListResponse)
def obter_lancamento(lancamento_id: int, db: Session = Depends(get_db)):
    lancamento = (
        db.query(models.LancamentoFinanceiro)
        .options(joinedload(models.LancamentoFinanceiro.forma_pagamento))
        .filter(models.LancamentoFinanceiro.id == lancamento_id)
        .first()
    )
    if not lancamento:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lançamento não encontrado")
    plano_nome = None
    if lancamento.id_plano_conta:
        pc = db.query(models.PlanoConta).filter(models.PlanoConta.id == lancamento.id_plano_conta).first()
        plano_nome = pc.nome if pc else None
    return LancamentoListResponse(
        id=lancamento.id,
        descricao=lancamento.descricao,
        valor=lancamento.valor,
        data_lancamento=lancamento.data_lancamento,
        data_vencimento=lancamento.data_vencimento,
        data_pagamento=lancamento.data_pagamento,
        tipo=lancamento.tipo,
        plano_conta_id=lancamento.id_plano_conta,
        forma_pagamento_id=lancamento.id_forma_pagamento,
        pago=lancamento.pago,
        plano_conta=plano_nome,
        forma_pagamento=lancamento.forma_pagamento.nome if lancamento.forma_pagamento else None,
    )


@router.put("/financeiro/{lancamento_id}", response_model=LancamentoListResponse)
def atualizar_lancamento(lancamento_id: int, payload: LancamentoUpdate, db: Session = Depends(get_db)):
    """Atualiza um lançamento financeiro."""
    lancamento = (
        db.query(models.LancamentoFinanceiro)
        .options(joinedload(models.LancamentoFinanceiro.forma_pagamento))
        .filter(models.LancamentoFinanceiro.id == lancamento_id)
        .first()
    )
    if not lancamento:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lançamento não encontrado")
    data = payload.model_dump(exclude_unset=True)
    if "plano_conta_id" in data:
        pid = data.pop("plano_conta_id")
        if db.query(models.PlanoConta).filter(models.PlanoConta.id == pid).first() is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plano de conta não encontrado")
        data["id_plano_conta"] = pid
    if "forma_pagamento_id" in data:
        fid = data.pop("forma_pagamento_id")
        if db.query(models.FormaPagamento).filter(models.FormaPagamento.id == fid).first() is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Forma de pagamento não encontrada")
        data["id_forma_pagamento"] = fid
    for key, value in data.items():
        setattr(lancamento, key, value)
    db.commit()
    db.refresh(lancamento)
    plano_nome = None
    if lancamento.id_plano_conta:
        pc = db.query(models.PlanoConta).filter(models.PlanoConta.id == lancamento.id_plano_conta).first()
        plano_nome = pc.nome if pc else None
    return LancamentoListResponse(
        id=lancamento.id,
        descricao=lancamento.descricao,
        valor=lancamento.valor,
        data_lancamento=lancamento.data_lancamento,
        data_vencimento=lancamento.data_vencimento,
        data_pagamento=lancamento.data_pagamento,
        tipo=lancamento.tipo,
        plano_conta_id=lancamento.id_plano_conta,
        forma_pagamento_id=lancamento.id_forma_pagamento,
        pago=lancamento.pago,
        plano_conta=plano_nome,
        forma_pagamento=lancamento.forma_pagamento.nome if lancamento.forma_pagamento else None,
    )


@router.delete("/financeiro/{lancamento_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_lancamento(lancamento_id: int, db: Session = Depends(get_db)):
    """Exclui um lançamento financeiro."""
    lancamento = db.query(models.LancamentoFinanceiro).filter(models.LancamentoFinanceiro.id == lancamento_id).first()
    if not lancamento:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lançamento não encontrado")
    db.delete(lancamento)
    db.commit()


def get_dashboard_financeiro(db: Session):
    """Lógica do dashboard financeiro para uso interno (ex.: endpoint /dashboard)."""
    hoje = date.today()
    ano_atual = hoje.year
    lancamentos_pagos = (
        db.query(models.LancamentoFinanceiro)
        .filter(models.LancamentoFinanceiro.pago == True)
        .all()
    )
    saldo = sum(
        (l.valor if l.tipo == "receita" else -l.valor)
        for l in lancamentos_pagos
    )
    lancamentos_ano = (
        db.query(models.LancamentoFinanceiro)
        .filter(
            models.LancamentoFinanceiro.data_lancamento >= date(ano_atual, 1, 1),
            models.LancamentoFinanceiro.data_lancamento <= date(ano_atual, 12, 31),
        )
        .all()
    )
    por_mes = {mes: 0.0 for mes in range(1, 13)}
    for l in lancamentos_ano:
        m = l.data_lancamento.month
        por_mes[m] += l.valor if l.tipo == "receita" else -l.valor
    mensal = [{"mes": m, "total": round(por_mes[m], 2)} for m in range(1, 13)]
    return {"saldo": round(saldo, 2), "mensal": mensal}


@router.get("/financeiro/dashboard")
def dashboard_financeiro(db: Session = Depends(get_db)):
    return get_dashboard_financeiro(db)
