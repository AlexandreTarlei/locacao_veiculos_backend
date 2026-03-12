"""Dependência que bloqueia acesso quando a empresa não está ativa."""
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
import models


def verificar_empresa_ativa(db: Session = Depends(get_db)) -> None:
    """Se a empresa (id=1) não estiver ativa, retorna 403 Empresa bloqueada."""
    empresa = db.query(models.Empresa).filter(models.Empresa.id == 1).first()
    if not empresa or getattr(empresa, "status", "ativo") != "ativo":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Empresa bloqueada",
        )
