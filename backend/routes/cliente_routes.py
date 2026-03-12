"""
Rotas do módulo clientes.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

from database import get_db
import models

router = APIRouter(prefix="/clientes", tags=["clientes"])


class ClienteCreate(BaseModel):
    nome: str
    cpf: str
    telefone: str
    email: str
    cep: str
    endereco: str
    data_nascimento: Optional[str] = None


class ClienteUpdate(BaseModel):
    nome: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    endereco: Optional[str] = None


class ClienteResponse(BaseModel):
    id: int
    nome: str
    cpf: str
    telefone: str
    email: str
    cep: str
    endereco: str
    data_nascimento: Optional[datetime] = None
    data_cadastro: datetime

    class Config:
        from_attributes = True


@router.post("/", response_model=ClienteResponse, status_code=status.HTTP_201_CREATED)
def criar_cliente(cliente: ClienteCreate, db: Session = Depends(get_db)):
    db_cliente = db.query(models.Cliente).filter(models.Cliente.cpf == cliente.cpf).first()
    if db_cliente:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Cliente com CPF {cliente.cpf} já existe")
    data_nascimento = None
    if cliente.data_nascimento:
        try:
            data_nascimento = datetime.strptime(cliente.data_nascimento, "%d/%m/%Y")
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Data de nascimento deve estar no formato dd/mm/yyyy")
    novo = models.Cliente(
        nome=cliente.nome,
        cpf=cliente.cpf,
        telefone=cliente.telefone,
        email=cliente.email,
        cep=cliente.cep,
        endereco=cliente.endereco,
        data_nascimento=data_nascimento,
    )
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo


@router.get("/", response_model=List[ClienteResponse])
def listar_clientes(db: Session = Depends(get_db)):
    return db.query(models.Cliente).all()


@router.get("/{cliente_id}", response_model=ClienteResponse)
def obter_cliente(cliente_id: int, db: Session = Depends(get_db)):
    cliente = db.query(models.Cliente).filter(models.Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado")
    return cliente


@router.put("/{cliente_id}", response_model=ClienteResponse)
def atualizar_cliente(cliente_id: int, cliente_update: ClienteUpdate, db: Session = Depends(get_db)):
    cliente = db.query(models.Cliente).filter(models.Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado")
    for campo, valor in cliente_update.dict(exclude_unset=True).items():
        setattr(cliente, campo, valor)
    db.commit()
    db.refresh(cliente)
    return cliente


@router.delete("/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_cliente(cliente_id: int, db: Session = Depends(get_db)):
    cliente = db.query(models.Cliente).filter(models.Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado")
    if db.query(models.Locacao).filter(models.Locacao.id_cliente == cliente_id).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Não é possível deletar um cliente com locações")
    db.delete(cliente)
    db.commit()
