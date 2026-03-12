"""
Rotas para tipos de usuário (lista para dropdowns, etc.).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from database import get_db
import models

router = APIRouter(prefix="/tipo-usuario", tags=["tipo-usuario"])


class TipoUsuarioResponse(BaseModel):
    id: int
    codigo: str
    nome: str

    class Config:
        from_attributes = True


@router.get("/", response_model=List[TipoUsuarioResponse])
def listar_tipos_usuario(db: Session = Depends(get_db)):
    """Lista todos os tipos de usuário (para selects, exibir nome do tipo, etc.)."""
    return db.query(models.TipoUsuario).order_by(models.TipoUsuario.id).all()


@router.get("/{id}", response_model=TipoUsuarioResponse)
def obter_tipo_usuario(id: int, db: Session = Depends(get_db)):
    """Retorna um tipo de usuário pelo id."""
    tipo = db.query(models.TipoUsuario).filter(models.TipoUsuario.id == id).first()
    if not tipo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tipo de usuário não encontrado")
    return tipo
