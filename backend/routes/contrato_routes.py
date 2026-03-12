"""
Rotas: contratos de locação (vinculados opcionalmente a reserva).
Criação com valor_total = valor_diaria * dias.
"""
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

from database import get_db
import models
from services.pdf_utils import gera_pdf_contrato


def criar_contrato(
    db: Session,
    cliente_id: int,
    veiculo_id: int,
    valor_diaria: float,
    dias: int,
    empresa_id: Optional[int] = None,
    reserva_id: Optional[int] = None,
):
    """Persiste contrato com valor_total = valor_diaria * dias."""
    valor_total = float(valor_diaria) * int(dias)
    contrato = models.Contrato(
        empresa_id=empresa_id,
        reserva_id=reserva_id,
        cliente_id=cliente_id,
        veiculo_id=veiculo_id,
        valor_diaria=Decimal(str(valor_diaria)),
        valor_total=Decimal(str(valor_total)),
        status="ativo",
    )
    db.add(contrato)
    db.commit()
    db.refresh(contrato)
    return contrato


router = APIRouter(prefix="/contratos", tags=["contratos"])


# ----- Schemas -----


class ContratoCreate(BaseModel):
    empresa_id: Optional[int] = None
    reserva_id: Optional[int] = None
    cliente_id: int
    veiculo_id: int
    valor_diaria: float
    dias: int


class ContratoResponse(BaseModel):
    id: int
    empresa_id: Optional[int]
    reserva_id: Optional[int]
    cliente_id: int
    veiculo_id: int
    valor_diaria: Optional[float]
    valor_total: Optional[float]
    status: str
    data_contrato: datetime

    class Config:
        from_attributes = True


# ----- Endpoints -----


@router.post("/", response_model=ContratoResponse, status_code=status.HTTP_201_CREATED)
def criar_contrato_endpoint(body: ContratoCreate, db: Session = Depends(get_db)):
    """Cria um contrato (valor_total = valor_diaria * dias). Valida reserva, cliente e veículo."""
    if body.dias <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="dias deve ser maior que zero",
        )
    if body.valor_diaria < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="valor_diaria não pode ser negativo",
        )
    if body.reserva_id is not None:
        r = db.query(models.Reserva).filter(models.Reserva.id == body.reserva_id).first()
        if not r:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reserva não encontrada",
            )
    cliente = db.query(models.Cliente).filter(models.Cliente.id == body.cliente_id).first()
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado",
        )
    veiculo = db.query(models.Veiculo).filter(models.Veiculo.id == body.veiculo_id).first()
    if not veiculo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Veículo não encontrado",
        )
    return criar_contrato(
        db,
        cliente_id=body.cliente_id,
        veiculo_id=body.veiculo_id,
        valor_diaria=body.valor_diaria,
        dias=body.dias,
        empresa_id=body.empresa_id,
        reserva_id=body.reserva_id,
    )


@router.get("/", response_model=List[ContratoResponse])
def listar_contratos(
    reserva_id: Optional[int] = Query(None),
    cliente_id: Optional[int] = Query(None),
    veiculo_id: Optional[int] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
):
    """Lista contratos com filtros opcionais."""
    query = db.query(models.Contrato)
    if reserva_id is not None:
        query = query.filter(models.Contrato.reserva_id == reserva_id)
    if cliente_id is not None:
        query = query.filter(models.Contrato.cliente_id == cliente_id)
    if veiculo_id is not None:
        query = query.filter(models.Contrato.veiculo_id == veiculo_id)
    if status_filter is not None:
        query = query.filter(models.Contrato.status == status_filter)
    return query.order_by(models.Contrato.data_contrato.desc()).all()


@router.get("/faturamento")
def faturamento_contratos(
    empresa_id: Optional[int] = Query(None, description="Filtrar por empresa; se omitido, soma todos os contratos"),
    db: Session = Depends(get_db),
):
    """Retorna a soma de valor_total da tabela contratos (faturamento por contratos), opcionalmente filtrada por empresa_id."""
    query = db.query(func.coalesce(func.sum(models.Contrato.valor_total), 0).label("faturamento"))
    if empresa_id is not None:
        query = query.filter(models.Contrato.empresa_id == empresa_id)
    total = query.scalar()
    fat = float(total) if total is not None else 0.0
    result = {"faturamento": round(fat, 2)}
    if empresa_id is not None:
        result["empresa_id"] = empresa_id
    return result


@router.get("/{contrato_id}/pdf", response_class=Response)
def obter_contrato_pdf(contrato_id: int, db: Session = Depends(get_db)):
    """Gera e retorna o PDF do contrato (tabela contratos)."""
    contrato = (
        db.query(models.Contrato)
        .options(
            joinedload(models.Contrato.cliente),
            joinedload(models.Contrato.veiculo),
        )
        .filter(models.Contrato.id == contrato_id)
        .first()
    )
    if not contrato:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contrato não encontrado",
        )
    pdf_bytes = gera_pdf_contrato(contrato)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=contrato_{contrato_id}.pdf"},
    )


@router.get("/{contrato_id}", response_model=ContratoResponse)
def obter_contrato(contrato_id: int, db: Session = Depends(get_db)):
    """Obtém um contrato pelo ID."""
    c = db.query(models.Contrato).filter(models.Contrato.id == contrato_id).first()
    if not c:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contrato não encontrado",
        )
    return c


# ----- Alias para clientes legados: POST /api/contratos e GET /api/contrato_pdf/{id} -----
router_contratos_api = APIRouter(prefix="/api", tags=["contratos"])


@router_contratos_api.post("/contratos", response_model=ContratoResponse, status_code=status.HTTP_201_CREATED)
def criar_contrato_api(body: ContratoCreate, db: Session = Depends(get_db)):
    """Alias POST /api/contratos para clientes legados. Mesmo body e retorno que POST /contratos/."""
    return criar_contrato_endpoint(body, db)


@router_contratos_api.get("/contrato_pdf/{contrato_id}", response_class=Response)
def obter_contrato_pdf_api(contrato_id: int, db: Session = Depends(get_db)):
    """Alias GET /api/contrato_pdf/{id} para clientes legados. Mesmo PDF que GET /contratos/{id}/pdf."""
    return obter_contrato_pdf(contrato_id, db)
