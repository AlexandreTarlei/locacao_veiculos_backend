"""
Rotas: formas de pagamento, locações e pagamentos.
Veículos: use o router_veiculos (marcas, modelos, CRUD de veículos).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel

from database import get_db
import models
from services.pdf_utils import gera_pdf_contrato_locacao
from .veiculo_routes import VeiculoResponse

router = APIRouter(tags=["locacoes"])

# ----- Schemas -----

class FormaPagamentoCreate(BaseModel):
    nome: str
    descricao: Optional[str] = None
    ativa: bool = True

class FormaPagamentoUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    ativa: Optional[bool] = None

class FormaPagamentoResponse(BaseModel):
    id: int
    nome: str
    descricao: Optional[str] = None
    ativa: bool
    class Config:
        from_attributes = True

class PagamentoCreate(BaseModel):
    id_forma_pagamento: int
    valor_pagamento: float
    numero_comprovante: Optional[str] = None
    observacoes: Optional[str] = None

class PagamentoResponse(BaseModel):
    id: int
    id_locacao: int
    id_forma_pagamento: int
    valor_pagamento: float
    data_pagamento: datetime
    numero_comprovante: Optional[str] = None
    observacoes: Optional[str] = None
    class Config:
        from_attributes = True

class ClienteResponse(BaseModel):
    id: int
    nome: str
    cpf: str
    telefone: str
    email: str
    cep: str
    endereco: str
    data_nascimento: Optional[datetime] = None
    data_cadastro: datetime
    class Config:
        from_attributes = True

class LocacaoCreate(BaseModel):
    id_cliente: int
    id_veiculo: int
    dias: int
    observacoes: Optional[str] = None

class LocacaoUpdate(BaseModel):
    observacoes: Optional[str] = None

class LocacaoResponse(BaseModel):
    id: int
    id_cliente: int
    id_veiculo: int
    data_inicio: datetime
    data_fim: datetime
    dias: int
    valor_total: float
    multa_atraso: float
    ativa: bool
    observacoes: Optional[str] = None
    class Config:
        from_attributes = True

class LocacaoDetalhladaResponse(LocacaoResponse):
    cliente: ClienteResponse
    veiculo: VeiculoResponse
    pagamentos: List[PagamentoResponse] = []


# ----- Formas de pagamento -----

@router.post("/formas-pagamento/", response_model=FormaPagamentoResponse, status_code=status.HTTP_201_CREATED)
def criar_forma_pagamento(forma: FormaPagamentoCreate, db: Session = Depends(get_db)):
    db_forma = db.query(models.FormaPagamento).filter(models.FormaPagamento.nome == forma.nome).first()
    if db_forma:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Forma de pagamento '{forma.nome}' já existe")
    nova_forma = models.FormaPagamento(**forma.model_dump())
    db.add(nova_forma)
    db.commit()
    db.refresh(nova_forma)
    return nova_forma

@router.get("/formas-pagamento/", response_model=List[FormaPagamentoResponse])
def listar_formas_pagamento(apenas_ativas: bool = False, db: Session = Depends(get_db)):
    query = db.query(models.FormaPagamento)
    if apenas_ativas:
        query = query.filter(models.FormaPagamento.ativa == True)
    return query.all()

@router.get("/formas-pagamento/{forma_id}", response_model=FormaPagamentoResponse)
def obter_forma_pagamento(forma_id: int, db: Session = Depends(get_db)):
    forma = db.query(models.FormaPagamento).filter(models.FormaPagamento.id == forma_id).first()
    if not forma:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Forma de pagamento não encontrada")
    return forma

@router.put("/formas-pagamento/{forma_id}", response_model=FormaPagamentoResponse)
def atualizar_forma_pagamento(forma_id: int, forma_update: FormaPagamentoUpdate, db: Session = Depends(get_db)):
    forma = db.query(models.FormaPagamento).filter(models.FormaPagamento.id == forma_id).first()
    if not forma:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Forma de pagamento não encontrada")
    for campo, valor in forma_update.model_dump(exclude_unset=True).items():
        setattr(forma, campo, valor)
    db.commit()
    db.refresh(forma)
    return forma

@router.delete("/formas-pagamento/{forma_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_forma_pagamento(forma_id: int, db: Session = Depends(get_db)):
    forma = db.query(models.FormaPagamento).filter(models.FormaPagamento.id == forma_id).first()
    if not forma:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Forma de pagamento não encontrada")
    if db.query(models.Pagamento).filter(models.Pagamento.id_forma_pagamento == forma_id).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Não é possível deletar uma forma de pagamento com pagamentos registrados")
    db.delete(forma)
    db.commit()


# ----- Locações -----

@router.post("/locacoes/", response_model=LocacaoResponse, status_code=status.HTTP_201_CREATED)
def criar_locacao(locacao: LocacaoCreate, db: Session = Depends(get_db)):
    cliente = db.query(models.Cliente).filter(models.Cliente.id == locacao.id_cliente).first()
    if not cliente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado")
    veiculo = db.query(models.Veiculo).filter(models.Veiculo.id == locacao.id_veiculo).first()
    if not veiculo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Veículo não encontrado")
    if not veiculo.disponivel:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Veículo não está disponível")
    if locacao.dias <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Número de dias deve ser maior que zero")
    data_inicio = datetime.now()
    data_fim = data_inicio + timedelta(days=locacao.dias)
    valor_total = locacao.dias * veiculo.valor_diaria
    nova_locacao = models.Locacao(
        id_cliente=locacao.id_cliente,
        id_veiculo=locacao.id_veiculo,
        data_inicio=data_inicio,
        data_fim=data_fim,
        dias=locacao.dias,
        valor_total=valor_total,
        observacoes=locacao.observacoes,
    )
    veiculo.disponivel = False
    db.add(nova_locacao)
    db.commit()
    db.refresh(nova_locacao)
    return nova_locacao

@router.get("/locacoes/", response_model=List[LocacaoDetalhladaResponse])
def listar_locacoes(apenas_ativas: bool = False, db: Session = Depends(get_db)):
    query = db.query(models.Locacao)
    if apenas_ativas:
        query = query.filter(models.Locacao.ativa == True)
    return query.all()

@router.get("/locacoes/{locacao_id}", response_model=LocacaoDetalhladaResponse)
def obter_locacao(locacao_id: int, db: Session = Depends(get_db)):
    locacao = db.query(models.Locacao).filter(models.Locacao.id == locacao_id).first()
    if not locacao:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Locação não encontrada")
    return locacao

@router.put("/locacoes/{locacao_id}", response_model=LocacaoResponse)
def atualizar_locacao(locacao_id: int, locacao_update: LocacaoUpdate, db: Session = Depends(get_db)):
    locacao = db.query(models.Locacao).filter(models.Locacao.id == locacao_id).first()
    if not locacao:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Locação não encontrada")
    for campo, valor in locacao_update.model_dump(exclude_unset=True).items():
        setattr(locacao, campo, valor)
    db.commit()
    db.refresh(locacao)
    return locacao

@router.post("/locacoes/{locacao_id}/finalizar", status_code=status.HTTP_200_OK)
def finalizar_locacao(locacao_id: int, db: Session = Depends(get_db)):
    locacao = db.query(models.Locacao).filter(models.Locacao.id == locacao_id).first()
    if not locacao:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Locação não encontrada")
    if not locacao.ativa:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Locação já foi finalizada")
    data_devolucao = datetime.now()
    if data_devolucao > locacao.data_fim:
        dias_atraso = (data_devolucao - locacao.data_fim).days
        multa = dias_atraso * (locacao.valor_total / locacao.dias * 0.5)
        locacao.multa_atraso = multa
        locacao.valor_total += multa
    locacao.ativa = False
    veiculo = db.query(models.Veiculo).filter(models.Veiculo.id == locacao.id_veiculo).first()
    if veiculo:
        veiculo.disponivel = True
    db.commit()
    db.refresh(locacao)
    return {"id": locacao.id, "status": "Finalizada", "valor_total": locacao.valor_total, "multa_atraso": locacao.multa_atraso}

@router.post("/locacoes/{locacao_id}/pagamentos/", response_model=PagamentoResponse, status_code=status.HTTP_201_CREATED)
def registrar_pagamento(locacao_id: int, pagamento: PagamentoCreate, db: Session = Depends(get_db)):
    locacao = db.query(models.Locacao).filter(models.Locacao.id == locacao_id).first()
    if not locacao:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Locação não encontrada")
    forma = db.query(models.FormaPagamento).filter(models.FormaPagamento.id == pagamento.id_forma_pagamento).first()
    if not forma:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Forma de pagamento não encontrada")
    if pagamento.valor_pagamento <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Valor de pagamento deve ser maior que zero")
    total_pagado = sum(p.valor_pagamento for p in locacao.pagamentos)
    saldo_pendente = locacao.valor_total - total_pagado
    if pagamento.valor_pagamento > saldo_pendente:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Valor excede saldo pendente (R$ {saldo_pendente:.2f})")
    novo_pagamento = models.Pagamento(
        id_locacao=locacao_id,
        id_forma_pagamento=pagamento.id_forma_pagamento,
        valor_pagamento=pagamento.valor_pagamento,
        numero_comprovante=pagamento.numero_comprovante,
        observacoes=pagamento.observacoes,
    )
    db.add(novo_pagamento)
    db.commit()
    db.refresh(novo_pagamento)
    return novo_pagamento

@router.get("/locacoes/{locacao_id}/pagamentos/", response_model=List[PagamentoResponse])
def listar_pagamentos(locacao_id: int, db: Session = Depends(get_db)):
    locacao = db.query(models.Locacao).filter(models.Locacao.id == locacao_id).first()
    if not locacao:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Locação não encontrada")
    return locacao.pagamentos

@router.get("/locacoes/{locacao_id}/resumo/")
def obter_resumo_locacao(locacao_id: int, db: Session = Depends(get_db)):
    locacao = db.query(models.Locacao).filter(models.Locacao.id == locacao_id).first()
    if not locacao:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Locação não encontrada")
    total_pagado = sum(p.valor_pagamento for p in locacao.pagamentos)
    saldo_pendente = locacao.valor_total - total_pagado
    return {
        "id": locacao.id,
        "cliente": locacao.cliente.nome,
        "veiculo": f"{locacao.veiculo.marca_nome} {locacao.veiculo.modelo_nome}".strip(),
        "valor_total": locacao.valor_total,
        "multa_atraso": locacao.multa_atraso,
        "total_pagado": total_pagado,
        "saldo_pendente": saldo_pendente,
        "quitada": saldo_pendente <= 0,
        "ativa": locacao.ativa,
    }


@router.get("/locacoes/{locacao_id}/contrato", response_class=Response)
def obter_contrato_locacao_pdf(locacao_id: int, db: Session = Depends(get_db)):
    """Gera e retorna o PDF do contrato de locação."""
    locacao = db.query(models.Locacao).filter(models.Locacao.id == locacao_id).first()
    if not locacao:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Locação não encontrada")
    pdf_bytes = gera_pdf_contrato_locacao(locacao)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=contrato_locacao_{locacao_id}.pdf"},
    )
