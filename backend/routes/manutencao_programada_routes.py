"""
Rotas de manutenção programada (agendamentos por km e/ou data limite).
"""
from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
import models

router = APIRouter(prefix="/manutencao-programada", tags=["manutencao-programada"])


# ----- Schemas -----

class ManutencaoProgramadaCreate(BaseModel):
    id_veiculo: int
    tipo_manutencao: str
    quilometragem_limite: Optional[int] = None
    data_limite: Optional[date] = None


class ManutencaoProgramadaUpdate(BaseModel):
    tipo_manutencao: Optional[str] = None
    quilometragem_limite: Optional[int] = None
    data_limite: Optional[date] = None
    ativa: Optional[bool] = None


class ManutencaoProgramadaResponse(BaseModel):
    id: int
    id_veiculo: int
    tipo_manutencao: str
    quilometragem_limite: Optional[int] = None
    data_limite: Optional[date] = None
    ativa: bool
    data_cadastro: Optional[str] = None
    data_atualizacao: Optional[str] = None

    class Config:
        from_attributes = True


# ----- CRUD -----

@router.get("/", response_model=List[ManutencaoProgramadaResponse])
def listar_manutencoes_programadas(
    id_veiculo: Optional[int] = None,
    ativa: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    """Lista manutenções programadas. Filtros opcionais: id_veiculo, ativa."""
    query = db.query(models.ManutencaoProgramada).order_by(
        models.ManutencaoProgramada.data_limite.asc().nulls_last(),
        models.ManutencaoProgramada.id.asc(),
    )
    if id_veiculo is not None:
        query = query.filter(models.ManutencaoProgramada.id_veiculo == id_veiculo)
    if ativa is not None:
        query = query.filter(models.ManutencaoProgramada.ativa == ativa)
    rows = query.all()
    return [
        ManutencaoProgramadaResponse(
            id=r.id,
            id_veiculo=r.id_veiculo,
            tipo_manutencao=r.tipo_manutencao,
            quilometragem_limite=r.quilometragem_limite,
            data_limite=r.data_limite,
            ativa=bool(r.ativa),
            data_cadastro=r.data_cadastro.isoformat() if r.data_cadastro else None,
            data_atualizacao=r.data_atualizacao.isoformat() if r.data_atualizacao else None,
        )
        for r in rows
    ]


@router.get("/proximas", response_model=List[dict])
def listar_proximas(db: Session = Depends(get_db)):
    """Lista manutenções programadas ativas com dados do veículo (quilometragem atual) para alertas."""
    rows = (
        db.query(models.ManutencaoProgramada, models.Veiculo.placa, models.Veiculo.quilometragem)
        .join(models.Veiculo, models.ManutencaoProgramada.id_veiculo == models.Veiculo.id)
        .filter(models.ManutencaoProgramada.ativa == True)
        .order_by(models.ManutencaoProgramada.data_limite.asc().nulls_last())
        .all()
    )
    return [
        {
            "id": mp.id,
            "id_veiculo": mp.id_veiculo,
            "tipo_manutencao": mp.tipo_manutencao,
            "quilometragem_limite": mp.quilometragem_limite,
            "data_limite": mp.data_limite.isoformat() if mp.data_limite else None,
            "veiculo_placa": placa,
            "veiculo_quilometragem": float(km) if km is not None else None,
        }
        for mp, placa, km in rows
    ]


@router.get("/{programada_id}", response_model=ManutencaoProgramadaResponse)
def obter_manutencao_programada(programada_id: int, db: Session = Depends(get_db)):
    r = db.query(models.ManutencaoProgramada).filter(models.ManutencaoProgramada.id == programada_id).first()
    if not r:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Manutenção programada não encontrada")
    return ManutencaoProgramadaResponse(
        id=r.id,
        id_veiculo=r.id_veiculo,
        tipo_manutencao=r.tipo_manutencao,
        quilometragem_limite=r.quilometragem_limite,
        data_limite=r.data_limite,
        ativa=bool(r.ativa),
        data_cadastro=r.data_cadastro.isoformat() if r.data_cadastro else None,
        data_atualizacao=r.data_atualizacao.isoformat() if r.data_atualizacao else None,
    )


@router.post("/", response_model=ManutencaoProgramadaResponse, status_code=status.HTTP_201_CREATED)
def criar_manutencao_programada(dados: ManutencaoProgramadaCreate, db: Session = Depends(get_db)):
    if dados.quilometragem_limite is None and dados.data_limite is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Informe quilometragem_limite e/ou data_limite.",
        )
    veiculo = db.query(models.Veiculo).filter(models.Veiculo.id == dados.id_veiculo).first()
    if not veiculo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Veículo não encontrado")
    nova = models.ManutencaoProgramada(
        id_veiculo=dados.id_veiculo,
        tipo_manutencao=dados.tipo_manutencao.strip(),
        quilometragem_limite=dados.quilometragem_limite,
        data_limite=dados.data_limite,
    )
    db.add(nova)
    db.commit()
    db.refresh(nova)
    return ManutencaoProgramadaResponse(
        id=nova.id,
        id_veiculo=nova.id_veiculo,
        tipo_manutencao=nova.tipo_manutencao,
        quilometragem_limite=nova.quilometragem_limite,
        data_limite=nova.data_limite,
        ativa=bool(nova.ativa),
        data_cadastro=nova.data_cadastro.isoformat() if nova.data_cadastro else None,
        data_atualizacao=nova.data_atualizacao.isoformat() if nova.data_atualizacao else None,
    )


@router.put("/{programada_id}", response_model=ManutencaoProgramadaResponse)
def atualizar_manutencao_programada(
    programada_id: int, dados: ManutencaoProgramadaUpdate, db: Session = Depends(get_db)
):
    r = db.query(models.ManutencaoProgramada).filter(models.ManutencaoProgramada.id == programada_id).first()
    if not r:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Manutenção programada não encontrada")
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(r, campo, valor)
    # Garantir que após update ainda exista pelo menos um limite
    if r.quilometragem_limite is None and r.data_limite is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="É necessário manter quilometragem_limite e/ou data_limite.",
        )
    db.commit()
    db.refresh(r)
    return ManutencaoProgramadaResponse(
        id=r.id,
        id_veiculo=r.id_veiculo,
        tipo_manutencao=r.tipo_manutencao,
        quilometragem_limite=r.quilometragem_limite,
        data_limite=r.data_limite,
        ativa=bool(r.ativa),
        data_cadastro=r.data_cadastro.isoformat() if r.data_cadastro else None,
        data_atualizacao=r.data_atualizacao.isoformat() if r.data_atualizacao else None,
    )


@router.delete("/{programada_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_manutencao_programada(programada_id: int, db: Session = Depends(get_db)):
    r = db.query(models.ManutencaoProgramada).filter(models.ManutencaoProgramada.id == programada_id).first()
    if not r:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Manutenção programada não encontrada")
    db.delete(r)
    db.commit()
