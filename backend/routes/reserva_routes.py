"""
Rotas: reservas por período.
Disponibilidade por datas (reservas + locações ativas) e criação de reserva.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel

from database import get_db
import models


def veiculo_disponivel(
    db: Session,
    veiculo_id: int,
    data_inicio: date,
    data_fim: date,
    excluir_reserva_id: Optional[int] = None,
) -> bool:
    """
    Verifica se o veículo está disponível no período (sem overlap com reservas
    reservado/confirmado nem com locações ativas).
    """
    # Overlap: período existente cruza com [data_inicio, data_fim] quando
    # existente.data_inicio <= data_fim AND existente.data_fim >= data_inicio

    # Reservas que bloqueiam: status reservado ou confirmado
    q_reservas = db.query(models.Reserva.id).filter(
        models.Reserva.veiculo_id == veiculo_id,
        models.Reserva.status.in_(["reservado", "confirmado"]),
        models.Reserva.data_inicio <= data_fim,
        models.Reserva.data_fim >= data_inicio,
    )
    if excluir_reserva_id is not None:
        q_reservas = q_reservas.filter(models.Reserva.id != excluir_reserva_id)
    if q_reservas.first() is not None:
        return False

    # Locações ativas no período (converter datetime para date na comparação)
    q_loc = db.query(models.Locacao.id).filter(
        models.Locacao.id_veiculo == veiculo_id,
        models.Locacao.ativa == True,
        models.Locacao.data_inicio <= datetime.combine(data_fim, datetime.max.time()),
        models.Locacao.data_fim >= datetime.combine(data_inicio, datetime.min.time()),
    )
    if q_loc.first() is not None:
        return False

    return True


router = APIRouter(prefix="/reservas", tags=["reservas"])


# ----- Schemas -----


class ReservaCreate(BaseModel):
    empresa_id: Optional[int] = None
    cliente_id: int
    veiculo_id: int
    data_inicio: date
    data_fim: date


class ReservaUpdate(BaseModel):
    data_inicio: Optional[date] = None
    data_fim: Optional[date] = None
    status: Optional[str] = None


class ReservaResponse(BaseModel):
    id: int
    empresa_id: Optional[int]
    cliente_id: int
    veiculo_id: int
    data_inicio: date
    data_fim: date
    status: str

    class Config:
        from_attributes = True


class DisponibilidadeResponse(BaseModel):
    disponivel: bool


# ----- Endpoints -----


@router.get("/disponibilidade", response_model=DisponibilidadeResponse)
def checar_disponibilidade(
    veiculo_id: int = Query(..., description="ID do veículo"),
    data_inicio: date = Query(..., description="Data início do período"),
    data_fim: date = Query(..., description="Data fim do período"),
    db: Session = Depends(get_db),
):
    """Verifica se o veículo está disponível no período (sem reservas/locações sobrepostas)."""
    if data_fim < data_inicio:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="data_fim deve ser >= data_inicio",
        )
    veiculo = db.query(models.Veiculo).filter(models.Veiculo.id == veiculo_id).first()
    if not veiculo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Veículo não encontrado",
        )
    disp = veiculo_disponivel(db, veiculo_id, data_inicio, data_fim)
    return DisponibilidadeResponse(disponivel=disp)


@router.post("/", response_model=ReservaResponse, status_code=status.HTTP_201_CREATED)
def criar_reserva(body: ReservaCreate, db: Session = Depends(get_db)):
    """Cria uma reserva após validar disponibilidade no período."""
    if body.data_fim < body.data_inicio:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="data_fim deve ser >= data_inicio",
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
    if not veiculo_disponivel(db, body.veiculo_id, body.data_inicio, body.data_fim):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Veículo já reservado ou locado neste período",
        )
    nova = models.Reserva(
        empresa_id=body.empresa_id,
        cliente_id=body.cliente_id,
        veiculo_id=body.veiculo_id,
        data_inicio=body.data_inicio,
        data_fim=body.data_fim,
        status="reservado",
    )
    db.add(nova)
    db.commit()
    db.refresh(nova)
    return nova


@router.get("/", response_model=List[ReservaResponse])
def listar_reservas(
    veiculo_id: Optional[int] = Query(None),
    cliente_id: Optional[int] = Query(None),
    data_inicio: Optional[date] = Query(None),
    data_fim: Optional[date] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
):
    """Lista reservas com filtros opcionais."""
    query = db.query(models.Reserva)
    if veiculo_id is not None:
        query = query.filter(models.Reserva.veiculo_id == veiculo_id)
    if cliente_id is not None:
        query = query.filter(models.Reserva.cliente_id == cliente_id)
    if data_inicio is not None:
        query = query.filter(models.Reserva.data_fim >= data_inicio)
    if data_fim is not None:
        query = query.filter(models.Reserva.data_inicio <= data_fim)
    if status_filter is not None:
        query = query.filter(models.Reserva.status == status_filter)
    return query.order_by(models.Reserva.data_inicio.desc()).all()


@router.get("/{reserva_id}", response_model=ReservaResponse)
def obter_reserva(reserva_id: int, db: Session = Depends(get_db)):
    """Obtém uma reserva pelo ID."""
    r = db.query(models.Reserva).filter(models.Reserva.id == reserva_id).first()
    if not r:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reserva não encontrada",
        )
    return r


@router.put("/{reserva_id}", response_model=ReservaResponse)
def atualizar_reserva(
    reserva_id: int,
    body: ReservaUpdate,
    db: Session = Depends(get_db),
):
    """Atualiza dados da reserva. Ao alterar datas, valida disponibilidade."""
    r = db.query(models.Reserva).filter(models.Reserva.id == reserva_id).first()
    if not r:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reserva não encontrada",
        )
    data_inicio = body.data_inicio if body.data_inicio is not None else r.data_inicio
    data_fim = body.data_fim if body.data_fim is not None else r.data_fim
    if data_fim < data_inicio:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="data_fim deve ser >= data_inicio",
        )
    if (body.data_inicio is not None or body.data_fim is not None) and not veiculo_disponivel(
        db, r.veiculo_id, data_inicio, data_fim, excluir_reserva_id=r.id
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Veículo já reservado ou locado no novo período",
        )
    if body.data_inicio is not None:
        r.data_inicio = body.data_inicio
    if body.data_fim is not None:
        r.data_fim = body.data_fim
    if body.status is not None:
        r.status = body.status
    db.commit()
    db.refresh(r)
    return r


@router.delete("/{reserva_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_reserva(reserva_id: int, db: Session = Depends(get_db)):
    """Remove uma reserva."""
    r = db.query(models.Reserva).filter(models.Reserva.id == reserva_id).first()
    if not r:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reserva não encontrada",
        )
    db.delete(r)
    db.commit()


# ----- Alias para clientes legados: GET/POST /api/reservas -----
router_reservas_api = APIRouter(prefix="/api", tags=["reservas"])


@router_reservas_api.get("/reservas", response_model=List[ReservaResponse])
def listar_reservas_api(
    veiculo_id: Optional[int] = Query(None),
    cliente_id: Optional[int] = Query(None),
    data_inicio: Optional[date] = Query(None),
    data_fim: Optional[date] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
):
    """Alias GET /api/reservas para clientes legados. Mesmo retorno que GET /reservas/."""
    return listar_reservas(
        veiculo_id=veiculo_id,
        cliente_id=cliente_id,
        data_inicio=data_inicio,
        data_fim=data_fim,
        status_filter=status_filter,
        db=db,
    )


@router_reservas_api.post("/reservas", response_model=ReservaResponse, status_code=status.HTTP_201_CREATED)
def criar_reserva_api(body: ReservaCreate, db: Session = Depends(get_db)):
    """Alias POST /api/reservas para clientes legados. Mesmo body e retorno que POST /reservas/."""
    return criar_reserva(body, db)
