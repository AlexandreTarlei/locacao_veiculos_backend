"""
Rotas de notificações por usuário. Exige autenticação JWT; cada usuário acessa apenas suas notificações.
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from auth.jwt_auth import get_current_user
from auth import verificar_empresa_ativa
import models

router = APIRouter(prefix="/notificacoes", tags=["notificacoes"])

STATUS_PERMITIDOS = ("nao_lida", "lida", "arquivada")


def _id_usuario_from_token(payload: dict) -> int:
    """Extrai id do usuário do payload JWT. Levanta 401 se não for usuário numérico."""
    sub = payload.get("sub")
    if sub is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        return int(sub)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso às notificações apenas para usuários cadastrados",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ----- Schemas -----


class NotificacaoCreate(BaseModel):
    titulo: str
    mensagem: Optional[str] = None
    status: str = "nao_lida"


class NotificacaoUpdate(BaseModel):
    status: Optional[str] = None


class NotificacaoResponse(BaseModel):
    id: int
    id_usuario: int
    titulo: str
    mensagem: Optional[str] = None
    status: str
    data_notificacao: Optional[str] = None

    class Config:
        from_attributes = True


# ----- CRUD (escopo: usuário autenticado) -----


@router.get("/", response_model=List[NotificacaoResponse])
def listar_notificacoes(
    status_filtro: Optional[str] = None,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_current_user),
    _=Depends(verificar_empresa_ativa),
):
    """Lista notificações do usuário autenticado. Opcional: ?status_filtro=nao_lida|lida|arquivada."""
    id_usuario = _id_usuario_from_token(payload)
    query = (
        db.query(models.Notificacao)
        .filter(models.Notificacao.id_usuario == id_usuario)
        .order_by(models.Notificacao.data_notificacao.desc())
    )
    if status_filtro is not None:
        if status_filtro not in STATUS_PERMITIDOS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"status deve ser um de: {STATUS_PERMITIDOS}",
            )
        query = query.filter(models.Notificacao.status == status_filtro)
    rows = query.all()
    return [
        NotificacaoResponse(
            id=r.id,
            id_usuario=r.id_usuario,
            titulo=r.titulo,
            mensagem=r.mensagem,
            status=r.status,
            data_notificacao=r.data_notificacao.isoformat() if r.data_notificacao else None,
        )
        for r in rows
    ]


@router.get("/{notificacao_id}", response_model=NotificacaoResponse)
def obter_notificacao(
    notificacao_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_current_user),
    _=Depends(verificar_empresa_ativa),
):
    """Retorna uma notificação pelo id, somente se pertencer ao usuário autenticado."""
    id_usuario = _id_usuario_from_token(payload)
    r = (
        db.query(models.Notificacao)
        .filter(
            models.Notificacao.id == notificacao_id,
            models.Notificacao.id_usuario == id_usuario,
        )
        .first()
    )
    if not r:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificação não encontrada",
        )
    return NotificacaoResponse(
        id=r.id,
        id_usuario=r.id_usuario,
        titulo=r.titulo,
        mensagem=r.mensagem,
        status=r.status,
        data_notificacao=r.data_notificacao.isoformat() if r.data_notificacao else None,
    )


@router.post("/", response_model=NotificacaoResponse, status_code=status.HTTP_201_CREATED)
def criar_notificacao(
    dados: NotificacaoCreate,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_current_user),
    _=Depends(verificar_empresa_ativa),
):
    """Cria notificação para o próprio usuário autenticado."""
    id_usuario = _id_usuario_from_token(payload)
    if dados.status not in STATUS_PERMITIDOS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"status deve ser um de: {STATUS_PERMITIDOS}",
        )
    nova = models.Notificacao(
        id_usuario=id_usuario,
        titulo=dados.titulo,
        mensagem=dados.mensagem,
        status=dados.status,
    )
    db.add(nova)
    db.commit()
    db.refresh(nova)
    return NotificacaoResponse(
        id=nova.id,
        id_usuario=nova.id_usuario,
        titulo=nova.titulo,
        mensagem=nova.mensagem,
        status=nova.status,
        data_notificacao=nova.data_notificacao.isoformat() if nova.data_notificacao else None,
    )


@router.patch("/{notificacao_id}", response_model=NotificacaoResponse)
def atualizar_notificacao(
    notificacao_id: int,
    dados: NotificacaoUpdate,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_current_user),
    _=Depends(verificar_empresa_ativa),
):
    """Atualiza notificação (ex.: marcar como lida), somente se for do usuário autenticado."""
    id_usuario = _id_usuario_from_token(payload)
    r = (
        db.query(models.Notificacao)
        .filter(
            models.Notificacao.id == notificacao_id,
            models.Notificacao.id_usuario == id_usuario,
        )
        .first()
    )
    if not r:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificação não encontrada",
        )
    if dados.status is not None:
        if dados.status not in STATUS_PERMITIDOS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"status deve ser um de: {STATUS_PERMITIDOS}",
            )
        r.status = dados.status
    db.commit()
    db.refresh(r)
    return NotificacaoResponse(
        id=r.id,
        id_usuario=r.id_usuario,
        titulo=r.titulo,
        mensagem=r.mensagem,
        status=r.status,
        data_notificacao=r.data_notificacao.isoformat() if r.data_notificacao else None,
    )


@router.delete("/{notificacao_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_notificacao(
    notificacao_id: int,
    db: Session = Depends(get_db),
    payload: dict = Depends(get_current_user),
    _=Depends(verificar_empresa_ativa),
):
    """Remove notificação, somente se pertencer ao usuário autenticado."""
    id_usuario = _id_usuario_from_token(payload)
    r = (
        db.query(models.Notificacao)
        .filter(
            models.Notificacao.id == notificacao_id,
            models.Notificacao.id_usuario == id_usuario,
        )
        .first()
    )
    if not r:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notificação não encontrada",
        )
    db.delete(r)
    db.commit()
