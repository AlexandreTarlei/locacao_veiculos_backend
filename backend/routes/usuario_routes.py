"""
Rotas CRUD de usuários (cadastro/edição com tipo de usuário). Protegidas por JWT.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, EmailStr

from database import get_db
import models
from auth import hash_senha, get_current_user, verificar_empresa_ativa

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


class UsuarioCreate(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    id_tipo_usuario: Optional[int] = None
    ativo: bool = True


class UsuarioUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    senha: Optional[str] = None
    id_tipo_usuario: Optional[int] = None
    ativo: Optional[bool] = None


class UsuarioResponse(BaseModel):
    id: int
    nome: Optional[str] = None
    email: Optional[str] = None
    id_tipo_usuario: Optional[int] = None
    nivel: Optional[str] = None
    ativo: bool
    tipo_nome: Optional[str] = None

    class Config:
        from_attributes = True


def _usuario_to_response(u: models.Usuario) -> dict:
    return {
        "id": u.id,
        "nome": u.nome,
        "email": u.email,
        "id_tipo_usuario": u.id_tipo_usuario,
        "nivel": u.nivel_ou_codigo,
        "ativo": u.ativo,
        "tipo_nome": u.tipo_usuario.nome if u.tipo_usuario else None,
    }


@router.get("/", response_model=List[UsuarioResponse])
def listar_usuarios(db: Session = Depends(get_db), _user=Depends(get_current_user), _=Depends(verificar_empresa_ativa)):
    """Lista todos os usuários com tipo. Requer autenticação."""
    usuarios = db.query(models.Usuario).all()
    return [_usuario_to_response(u) for u in usuarios]


@router.get("/{usuario_id}", response_model=UsuarioResponse)
def obter_usuario(usuario_id: int, db: Session = Depends(get_db), _user=Depends(get_current_user), _=Depends(verificar_empresa_ativa)):
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    return _usuario_to_response(usuario)


@router.post("/", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def criar_usuario(dados: UsuarioCreate, db: Session = Depends(get_db), _user=Depends(get_current_user), _=Depends(verificar_empresa_ativa)):
    if not dados.senha:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="E-mail e senha são obrigatórios")
    email = dados.email.strip().lower()
    if db.query(models.Usuario).filter(models.Usuario.email == email).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="E-mail já cadastrado")
    tipo = None
    if dados.id_tipo_usuario:
        tipo = db.query(models.TipoUsuario).filter(models.TipoUsuario.id == dados.id_tipo_usuario).first()
        if not tipo:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tipo de usuário inválido")
    novo = models.Usuario(
        nome=dados.nome or None,
        email=email,
        senha=hash_senha(dados.senha),
        id_tipo_usuario=dados.id_tipo_usuario,
        nivel=tipo.codigo if tipo else "OPERACIONAL",
        ativo=dados.ativo,
    )
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return _usuario_to_response(novo)


@router.put("/{usuario_id}", response_model=UsuarioResponse)
def atualizar_usuario(usuario_id: int, dados: UsuarioUpdate, db: Session = Depends(get_db), _user=Depends(get_current_user), _=Depends(verificar_empresa_ativa)):
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    if dados.email is not None:
        email = dados.email.strip().lower()
        outro = db.query(models.Usuario).filter(models.Usuario.email == email, models.Usuario.id != usuario_id).first()
        if outro:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="E-mail já cadastrado")
        usuario.email = email
    if dados.nome is not None:
        usuario.nome = dados.nome
    if dados.senha and dados.senha.strip():
        usuario.senha = hash_senha(dados.senha.strip())
    if dados.id_tipo_usuario is not None:
        if dados.id_tipo_usuario:
            tipo = db.query(models.TipoUsuario).filter(models.TipoUsuario.id == dados.id_tipo_usuario).first()
            if not tipo:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tipo de usuário inválido")
            usuario.id_tipo_usuario = tipo.id
            usuario.nivel = tipo.codigo
        else:
            usuario.id_tipo_usuario = None
            usuario.nivel = "OPERACIONAL"
    if dados.ativo is not None:
        usuario.ativo = dados.ativo
    db.commit()
    db.refresh(usuario)
    return _usuario_to_response(usuario)


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_usuario(usuario_id: int, db: Session = Depends(get_db), _user=Depends(get_current_user), _=Depends(verificar_empresa_ativa)):
    usuario = db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    db.delete(usuario)
    db.commit()
