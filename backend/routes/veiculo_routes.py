"""
Rotas de marcas, modelos e veículos.
"""
import json
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, model_validator
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_

from database import get_db
import models

router = APIRouter(tags=["marcas", "modelos", "veiculos"])


# ----- Schemas -----

class MarcaVeiculoResponse(BaseModel):
    id: int
    nome: str

    class Config:
        from_attributes = True


class MarcaVeiculoCreate(BaseModel):
    nome: str


class ModeloVeiculoResponse(BaseModel):
    id: int
    id_marca: int
    nome: str
    marca_nome: Optional[str] = None

    class Config:
        from_attributes = True


class ModeloVeiculoCreate(BaseModel):
    id_marca: int
    nome: str


class VeiculoCreate(BaseModel):
    placa: str
    id_modelo: int
    ano: int
    cor: str
    quilometragem: float = 0
    valor_diaria: float
    fotos: Optional[List[str]] = None


class VeiculoUpdate(BaseModel):
    id_modelo: Optional[int] = None
    valor_diaria: Optional[float] = None
    quilometragem: Optional[float] = None
    disponivel: Optional[bool] = None
    fotos: Optional[List[str]] = None


class VeiculoResponse(BaseModel):
    id: int
    placa: str
    id_modelo: int
    marca: str = ""
    modelo: str = ""
    ano: int
    cor: str
    quilometragem: float
    valor_diaria: float
    disponivel: bool
    fotos: List[str] = []

    class Config:
        from_attributes = True

    @model_validator(mode="before")
    @classmethod
    def orm_marca_modelo(cls, data):
        if hasattr(data, "marca_nome") and hasattr(data, "modelo_nome"):
            return {
                "id": data.id,
                "placa": data.placa,
                "id_modelo": data.id_modelo or 0,
                "marca": data.marca_nome or "",
                "modelo": data.modelo_nome or "",
                "ano": data.ano,
                "cor": data.cor,
                "quilometragem": data.quilometragem,
                "valor_diaria": data.valor_diaria,
                "disponivel": data.disponivel,
                "fotos": getattr(data, "fotos", []) or [],
            }
        return data

    @classmethod
    def from_veiculo_orm(cls, v):
        return cls(
            id=v.id,
            placa=v.placa,
            id_modelo=v.id_modelo or 0,
            marca=v.marca_nome,
            modelo=v.modelo_nome,
            ano=v.ano,
            cor=v.cor,
            quilometragem=v.quilometragem,
            valor_diaria=v.valor_diaria,
            disponivel=v.disponivel,
            fotos=v.fotos if hasattr(v, "fotos") else [],
        )


def _query_veiculos_com_marca_modelo(db: Session):
    return db.query(models.Veiculo).options(
        joinedload(models.Veiculo.modelo_ref).joinedload(models.ModeloVeiculo.marca),
    )


# ----- Marcas -----

@router.get("/marcas/", response_model=List[MarcaVeiculoResponse])
def listar_marcas(db: Session = Depends(get_db)):
    """Lista todas as marcas de veículos."""
    return db.query(models.MarcaVeiculo).order_by(models.MarcaVeiculo.nome).all()


@router.post("/marcas/", response_model=MarcaVeiculoResponse, status_code=status.HTTP_201_CREATED)
def criar_marca(marca: MarcaVeiculoCreate, db: Session = Depends(get_db)):
    """Cria uma nova marca de veículo."""
    existente = db.query(models.MarcaVeiculo).filter(models.MarcaVeiculo.nome == marca.nome.strip()).first()
    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Marca '{marca.nome}' já existe",
        )
    nova = models.MarcaVeiculo(nome=marca.nome.strip())
    db.add(nova)
    db.commit()
    db.refresh(nova)
    return nova


# ----- Modelos -----

@router.get("/modelos/", response_model=List[ModeloVeiculoResponse])
def listar_modelos(id_marca: Optional[int] = None, db: Session = Depends(get_db)):
    """Lista modelos de veículos. Use id_marca para filtrar por marca."""
    query = db.query(models.ModeloVeiculo).options(joinedload(models.ModeloVeiculo.marca))
    if id_marca is not None:
        query = query.filter(models.ModeloVeiculo.id_marca == id_marca)
    query = query.order_by(models.ModeloVeiculo.nome)
    rows = query.all()
    return [
        ModeloVeiculoResponse(
            id=m.id,
            id_marca=m.id_marca,
            nome=m.nome,
            marca_nome=m.marca.nome if m.marca else None,
        )
        for m in rows
    ]


@router.post("/modelos/", response_model=ModeloVeiculoResponse, status_code=status.HTTP_201_CREATED)
def criar_modelo(modelo: ModeloVeiculoCreate, db: Session = Depends(get_db)):
    """Cria um novo modelo (vinculado a uma marca)."""
    marca = db.query(models.MarcaVeiculo).filter(models.MarcaVeiculo.id == modelo.id_marca).first()
    if not marca:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Marca não encontrada",
        )
    existente = db.query(models.ModeloVeiculo).filter(
        models.ModeloVeiculo.id_marca == modelo.id_marca,
        models.ModeloVeiculo.nome == modelo.nome.strip(),
    ).first()
    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Modelo '{modelo.nome}' já existe para esta marca",
        )
    novo = models.ModeloVeiculo(id_marca=modelo.id_marca, nome=modelo.nome.strip())
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return ModeloVeiculoResponse(
        id=novo.id,
        id_marca=novo.id_marca,
        nome=novo.nome,
        marca_nome=marca.nome,
    )


# ----- Veículos -----

@router.post("/veiculos/", response_model=VeiculoResponse, status_code=status.HTTP_201_CREATED)
def criar_veiculo(veiculo: VeiculoCreate, db: Session = Depends(get_db)):
    """Cria um novo veículo (id_modelo obrigatório)."""
    db_veiculo = db.query(models.Veiculo).filter(models.Veiculo.placa == veiculo.placa).first()
    if db_veiculo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Veículo com placa {veiculo.placa} já existe",
        )
    data = veiculo.model_dump() if hasattr(veiculo, "model_dump") else veiculo.dict()
    fotos = data.pop("fotos", None)
    novo_veiculo = models.Veiculo(**data)
    if fotos is not None:
        novo_veiculo.fotos_json = json.dumps(fotos[:6]) if fotos else None
    db.add(novo_veiculo)
    db.commit()
    db.refresh(novo_veiculo)
    v = _query_veiculos_com_marca_modelo(db).filter(models.Veiculo.id == novo_veiculo.id).first()
    return VeiculoResponse.from_veiculo_orm(v) if v else VeiculoResponse(
        id=novo_veiculo.id,
        placa=novo_veiculo.placa,
        id_modelo=novo_veiculo.id_modelo or 0,
        marca="",
        modelo="",
        ano=novo_veiculo.ano,
        cor=novo_veiculo.cor,
        quilometragem=novo_veiculo.quilometragem,
        valor_diaria=novo_veiculo.valor_diaria,
        disponivel=novo_veiculo.disponivel,
        fotos=novo_veiculo.fotos,
    )


@router.get("/veiculos/", response_model=List[VeiculoResponse])
def listar_veiculos(apenas_disponiveis: bool = False, db: Session = Depends(get_db)):
    """Lista todos os veículos ou apenas os disponíveis."""
    query = _query_veiculos_com_marca_modelo(db)
    if apenas_disponiveis:
        query = query.filter(models.Veiculo.disponivel == True)
    rows = query.all()
    return [VeiculoResponse.from_veiculo_orm(v) for v in rows]


@router.get("/veiculos/{veiculo_id}", response_model=VeiculoResponse)
def obter_veiculo(veiculo_id: int, db: Session = Depends(get_db)):
    """Obtém um veículo (com marca e modelo)."""
    veiculo = _query_veiculos_com_marca_modelo(db).filter(models.Veiculo.id == veiculo_id).first()
    if not veiculo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Veículo não encontrado",
        )
    return VeiculoResponse.from_veiculo_orm(veiculo)


@router.put("/veiculos/{veiculo_id}", response_model=VeiculoResponse)
def atualizar_veiculo(veiculo_id: int, veiculo_update: VeiculoUpdate, db: Session = Depends(get_db)):
    """Atualiza dados de um veículo."""
    veiculo = db.query(models.Veiculo).filter(models.Veiculo.id == veiculo_id).first()
    if not veiculo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Veículo não encontrado",
        )
    dados_atualizacao = (
        veiculo_update.model_dump(exclude_unset=True)
        if hasattr(veiculo_update, "model_dump")
        else veiculo_update.dict(exclude_unset=True)
    )
    fotos = dados_atualizacao.pop("fotos", None)
    for campo, valor in dados_atualizacao.items():
        setattr(veiculo, campo, valor)
    if fotos is not None:
        veiculo.fotos_json = json.dumps(fotos[:6]) if fotos else None
    db.commit()
    db.refresh(veiculo)
    v = _query_veiculos_com_marca_modelo(db).filter(models.Veiculo.id == veiculo_id).first()
    return VeiculoResponse.from_veiculo_orm(v)


@router.delete("/veiculos/{veiculo_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_veiculo(veiculo_id: int, db: Session = Depends(get_db)):
    """Deleta um veículo."""
    veiculo = db.query(models.Veiculo).filter(models.Veiculo.id == veiculo_id).first()
    if not veiculo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Veículo não encontrado",
        )
    locacoes_ativas = db.query(models.Locacao).filter(
        and_(models.Locacao.id_veiculo == veiculo_id, models.Locacao.ativa == True)
    ).first()
    if locacoes_ativas:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível deletar um veículo com locações ativas",
        )
    db.delete(veiculo)
    db.commit()
