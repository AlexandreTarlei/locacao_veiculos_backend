"""
Rotas de manutenções (gastos por veículo) para dashboard e relatórios.
"""
from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db
import models

router = APIRouter(prefix="/manutencoes", tags=["manutencoes"])


# ----- Schemas -----

class ManutencaoCreate(BaseModel):
    id_veiculo: int
    descricao: Optional[str] = None
    valor: float = 0
    data_manutencao: date


class ManutencaoUpdate(BaseModel):
    descricao: Optional[str] = None
    valor: Optional[float] = None
    data_manutencao: Optional[date] = None


class ManutencaoResponse(BaseModel):
    id: int
    id_veiculo: int
    descricao: Optional[str] = None
    valor: float
    data_manutencao: date
    data_cadastro: Optional[str] = None

    class Config:
        from_attributes = True


# ----- CRUD -----

@router.get("/", response_model=List[ManutencaoResponse])
def listar_manutencoes(
    id_veiculo: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """Lista manutenções. Use id_veiculo para filtrar por veículo."""
    query = db.query(models.Manutencao).order_by(models.Manutencao.data_manutencao.desc())
    if id_veiculo is not None:
        query = query.filter(models.Manutencao.id_veiculo == id_veiculo)
    rows = query.all()
    return [
        ManutencaoResponse(
            id=r.id,
            id_veiculo=r.id_veiculo,
            descricao=r.descricao,
            valor=float(r.valor),
            data_manutencao=r.data_manutencao,
            data_cadastro=r.data_cadastro.isoformat() if r.data_cadastro else None,
        )
        for r in rows
    ]


@router.get("/resumo")
def resumo_por_veiculo(db: Session = Depends(get_db)):
    """Retorna totais de gasto por veículo (para gráfico de manutenção no dashboard)."""
    rows = (
        db.query(models.Manutencao.id_veiculo, func.sum(models.Manutencao.valor).label("total"))
        .group_by(models.Manutencao.id_veiculo)
        .all()
    )
    return [{"id_veiculo": r.id_veiculo, "valor": float(r.total)} for r in rows]


@router.get("/{manutencao_id}", response_model=ManutencaoResponse)
def obter_manutencao(manutencao_id: int, db: Session = Depends(get_db)):
    r = db.query(models.Manutencao).filter(models.Manutencao.id == manutencao_id).first()
    if not r:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Manutenção não encontrada")
    return ManutencaoResponse(
        id=r.id,
        id_veiculo=r.id_veiculo,
        descricao=r.descricao,
        valor=float(r.valor),
        data_manutencao=r.data_manutencao,
        data_cadastro=r.data_cadastro.isoformat() if r.data_cadastro else None,
    )


@router.post("/", response_model=ManutencaoResponse, status_code=status.HTTP_201_CREATED)
def criar_manutencao(dados: ManutencaoCreate, db: Session = Depends(get_db)):
    veiculo = db.query(models.Veiculo).filter(models.Veiculo.id == dados.id_veiculo).first()
    if not veiculo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Veículo não encontrado")
    if dados.valor < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Valor não pode ser negativo")
    nova = models.Manutencao(
        id_veiculo=dados.id_veiculo,
        descricao=dados.descricao,
        valor=dados.valor,
        data_manutencao=dados.data_manutencao,
    )
    db.add(nova)
    db.commit()
    db.refresh(nova)
    return ManutencaoResponse(
        id=nova.id,
        id_veiculo=nova.id_veiculo,
        descricao=nova.descricao,
        valor=float(nova.valor),
        data_manutencao=nova.data_manutencao,
        data_cadastro=nova.data_cadastro.isoformat() if nova.data_cadastro else None,
    )


@router.put("/{manutencao_id}", response_model=ManutencaoResponse)
def atualizar_manutencao(manutencao_id: int, dados: ManutencaoUpdate, db: Session = Depends(get_db)):
    r = db.query(models.Manutencao).filter(models.Manutencao.id == manutencao_id).first()
    if not r:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Manutenção não encontrada")
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        if campo == "valor" and valor is not None and valor < 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Valor não pode ser negativo")
        setattr(r, campo, valor)
    db.commit()
    db.refresh(r)
    return ManutencaoResponse(
        id=r.id,
        id_veiculo=r.id_veiculo,
        descricao=r.descricao,
        valor=float(r.valor),
        data_manutencao=r.data_manutencao,
        data_cadastro=r.data_cadastro.isoformat() if r.data_cadastro else None,
    )


@router.delete("/{manutencao_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_manutencao(manutencao_id: int, db: Session = Depends(get_db)):
    r = db.query(models.Manutencao).filter(models.Manutencao.id == manutencao_id).first()
    if not r:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Manutenção não encontrada")
    db.delete(r)
    db.commit()
