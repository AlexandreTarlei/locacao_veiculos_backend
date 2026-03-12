"""Rotas de login e logout."""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, model_validator
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
import models
from config import API_USER, API_PASSWORD
from .jwt_auth import criar_token, verificar_senha

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    """Aceita 'email' ou 'username' (compatibilidade). O valor deve ser um e-mail válido."""
    username: Optional[str] = None
    email: Optional[str] = None
    password: str

    @model_validator(mode="after")
    def check_email_or_username(self):
        val = (self.email or self.username or "").strip().lower()
        if not val:
            raise ValueError("E-mail ou usuário é obrigatório")
        if "@" not in val or "." not in val.split("@")[-1]:
            raise ValueError("Formato de e-mail inválido")
        return self


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: Optional[dict] = None


def _empresa_ativa(db: Session) -> None:
    """Levanta 403 se a empresa não estiver ativa (para bloquear login)."""
    empresa = db.query(models.Empresa).filter(models.Empresa.id == 1).first()
    if not empresa or getattr(empresa, "status", "ativo") != "ativo":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Empresa bloqueada",
        )


def _do_login(email: str, password: str, db: Session) -> LoginResponse:
    """Lógica interna de login: valida empresa, usuário/senha ou API_USER/API_PASSWORD. Retorna LoginResponse ou levanta HTTPException."""
    _empresa_ativa(db)

    email_ou_login = (email or "").strip().lower()
    senha = password or ""

    usuario = db.query(models.Usuario).filter(
        models.Usuario.email == email_ou_login,
        models.Usuario.ativo == True,
    ).first()

    if usuario and usuario.senha and verificar_senha(senha, usuario.senha):
        nivel = usuario.nivel_ou_codigo
        tipo_nome = usuario.tipo_usuario.nome if usuario.tipo_usuario else None
        usuario.ultimo_login = datetime.utcnow()
        db.commit()
        token = criar_token({"sub": str(usuario.id), "email": usuario.email, "nivel": nivel})
        return LoginResponse(
            access_token=token,
            usuario={
                "id": usuario.id,
                "nome": usuario.nome,
                "email": usuario.email,
                "nivel": nivel,
                "tipo_nome": tipo_nome,
            },
        )

    if email_ou_login == API_USER and senha == API_PASSWORD:
        _empresa_ativa(db)
        token = criar_token({"sub": "admin", "email": API_USER})
        return LoginResponse(access_token=token)

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Usuário ou senha inválidos",
    )


@router.post("/login", response_model=LoginResponse)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Login por email e senha. Retorna JWT com expiração de 8h. Atualiza ultimo_login."""
    email_ou_login = (login_data.email or login_data.username or "").strip().lower()
    return _do_login(email_ou_login, login_data.password or "", db)


class LoginRequestCompat(BaseModel):
    """Body para POST /api/login: aceita 'senha' (legado) ou 'password'."""
    email: str
    senha: Optional[str] = None
    password: Optional[str] = None

    @model_validator(mode="after")
    def check_email_and_password(self):
        val = (self.email or "").strip().lower()
        if not val:
            raise ValueError("E-mail é obrigatório")
        if "@" not in val or "." not in val.split("@")[-1]:
            raise ValueError("Formato de e-mail inválido")
        pwd = (self.password or self.senha or "").strip()
        if not pwd:
            raise ValueError("Senha é obrigatória")
        return self


router_api = APIRouter(prefix="/api", tags=["auth"])


@router_api.post("/login", response_model=LoginResponse)
def login_api(body: LoginRequestCompat, db: Session = Depends(get_db)):
    """Alias POST /api/login para clientes legados: aceita body com 'email' e 'senha' (ou 'password'). Mesmo retorno que POST /auth/login."""
    email = (body.email or "").strip().lower()
    password = (body.password or body.senha or "").strip()
    return _do_login(email, password, db)


@router.post("/logout")
def logout():
    """Com JWT stateless, o cliente apenas descarta o token."""
    return {"message": "ok"}
