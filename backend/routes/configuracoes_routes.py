"""
Rotas de configurações: dados da empresa (menu Configurações).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from database import get_db
import models

router = APIRouter(prefix="/configuracoes", tags=["configuracoes"])


class EmpresaResponse(BaseModel):
    id: int
    nome_fantasia: Optional[str] = None
    razao_social: Optional[str] = None
    cnpj: Optional[str] = None
    endereco: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    status: Optional[str] = None

    class Config:
        from_attributes = True


class EmpresaUpdate(BaseModel):
    nome_fantasia: Optional[str] = None
    razao_social: Optional[str] = None
    cnpj: Optional[str] = None
    endereco: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    status: Optional[str] = None


def _get_or_create_empresa(db: Session) -> models.Empresa:
    """Retorna o registro único de empresa (id=1), criando com valores vazios se não existir."""
    empresa = db.query(models.Empresa).filter(models.Empresa.id == 1).first()
    if not empresa:
        empresa = models.Empresa(
            id=1,
            nome_fantasia="",
            razao_social="",
            cnpj="",
            endereco="",
            telefone="",
            email="",
            status="ativo",
        )
        db.add(empresa)
        db.commit()
        db.refresh(empresa)
    return empresa


@router.get("/empresa", response_model=EmpresaResponse)
def get_empresa(db: Session = Depends(get_db)):
    """Retorna os dados da empresa (configurações). Cria registro padrão se não existir."""
    empresa = _get_or_create_empresa(db)
    return empresa


@router.put("/empresa", response_model=EmpresaResponse)
def atualizar_empresa(payload: EmpresaUpdate, db: Session = Depends(get_db)):
    """Atualiza os dados da empresa. Cria o registro se não existir."""
    empresa = _get_or_create_empresa(db)
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(empresa, key, value)
    db.commit()
    db.refresh(empresa)
    return empresa
