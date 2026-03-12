"""
API FastAPI para Sistema de Locação de Veículos
Endpoints para gerenciar veículos, clientes, locações e pagamentos
"""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

try:
    from dotenv import load_dotenv  # pyright: ignore[reportMissingImports]
    load_dotenv(BASE_DIR / ".env")
except ImportError:
    pass

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, FileResponse, RedirectResponse, JSONResponse
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, text, extract, func
from datetime import datetime, timedelta, date
from typing import List, Optional
import json

from pydantic import BaseModel

from database import engine, Base, SessionLocal, get_db  # pyright: ignore[reportMissingImports]
import models  # pyright: ignore[reportMissingImports]
from pdf_utils import gera_pdf_vencidas, gera_pdf_mensal, gera_pdf_sistema
from backend.routes.veiculo_routes import router as veiculo_router, VeiculoResponse
from backend.routes.manutencao_routes import router as manutencao_router
from backend.routes.reserva_routes import router as reserva_router  # pyright: ignore[reportMissingImports]
from backend.routes.contrato_routes import router as contrato_router  # pyright: ignore[reportMissingImports]

# Formas de pagamento padrão (seed) — as mais utilizadas hoje; inseridas no banco se ainda não existirem
FORMAS_PAGAMENTO_PADRAO = [
    {"nome": "PIX", "descricao": "Pagamento instantâneo via PIX", "ativa": True},
    {"nome": "Cartão de crédito", "descricao": "Cartão de crédito à vista ou parcelado", "ativa": True},
    {"nome": "Cartão de débito", "descricao": "Cartão de débito", "ativa": True},
    {"nome": "Dinheiro", "descricao": "Pagamento em espécie", "ativa": True},
    {"nome": "Boleto bancário", "descricao": "Boleto bancário", "ativa": True},
    {"nome": "Transferência bancária", "descricao": "Transferência TED/DOC", "ativa": True},
    {"nome": "Carteira digital", "descricao": "Mercado Pago, PicPay, PayPal etc.", "ativa": True},
    {"nome": "Débito em conta", "descricao": "Débito automático em conta corrente", "ativa": True},
    {"nome": "Vale-refeição", "descricao": "VR, Alelo, Sodexo, Ticket etc.", "ativa": True},
    {"nome": "Link de pagamento", "descricao": "Link enviado por e-mail ou mensagem", "ativa": True},
    {"nome": "Cheque", "descricao": "Pagamento com cheque", "ativa": True},
    {"nome": "Vale/cupom", "descricao": "Vale ou cupom de desconto", "ativa": True},
]


def seed_formas_pagamento():
    """Garante que todas as formas de pagamento padrão existam no banco. Insere apenas as que ainda não existem (por nome, case-insensitive)."""
    db = SessionLocal()
    try:
        for fp in FORMAS_PAGAMENTO_PADRAO:
            nome_norm = fp["nome"].strip().lower()
            existe = db.query(models.FormaPagamento).filter(
                func.lower(models.FormaPagamento.nome) == nome_norm
            ).first()
            if not existe:
                db.add(models.FormaPagamento(**fp))
        db.commit()
    finally:
        db.close()


# Configurar aplicação FastAPI
app = FastAPI(
    title="API Locação de Veículos",
    description="Sistema de gerenciamento de locação de veículos com MariaDB",
    version="1.0.0"
)


def seed_plano_contas():
    """Insere contas padrão do plano de contas se a tabela estiver vazia."""
    db = SessionLocal()
    try:
        if db.query(models.PlanoConta).count() == 0:
            for nome in ["Receitas", "Despesas", "Vendas", "Combustível", "Manutenção", "Outros"]:
                db.add(models.PlanoConta(nome=nome))
            db.commit()
    finally:
        db.close()


def _startup_db():
    """Executa criação de tabelas e seeds em background para não bloquear o servidor."""
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"[AVISO] Banco não disponível: {e}. Conecte o MySQL e reinicie para dados completos.")
    try:
        seed_formas_pagamento()
    except Exception as e:
        print(f"[AVISO] Seed formas de pagamento: {e}")
    try:
        seed_plano_contas()
    except Exception as e:
        print(f"[AVISO] Seed plano de contas: {e}")


@app.on_event("startup")
def on_startup():
    """Inicia a API e agenda inicialização do banco em thread para o frontend abrir logo."""
    import threading
    threading.Thread(target=_startup_db, daemon=True).start()


# Configurar CORS para permitir requisições de qualquer origem
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(veiculo_router)
app.include_router(manutencao_router)
app.include_router(reserva_router)
app.include_router(contrato_router)

# ===== SCHEMAS (Pydantic Models) =====

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

class FormaPagamentoCreate(BaseModel):
    nome: str
    descricao: Optional[str] = None
    ativa: bool = True

class FormaPagamentoUpdate(BaseModel):
    nome: Optional[str] = None
    descricao: Optional[str] = None
    ativa: Optional[bool] = None

class FormaPagamentoResponse(BaseModel):
    id: int
    nome: str
    descricao: Optional[str] = None
    ativa: bool
    
    class Config:
        from_attributes = True

class PagamentoCreate(BaseModel):
    id_forma_pagamento: int
    valor_pagamento: float
    numero_comprovante: Optional[str] = None
    observacoes: Optional[str] = None

class PagamentoResponse(BaseModel):
    id: int
    id_locacao: int
    id_forma_pagamento: int
    valor_pagamento: float
    data_pagamento: datetime
    numero_comprovante: Optional[str] = None
    observacoes: Optional[str] = None
    
    class Config:
        from_attributes = True

class LocacaoCreate(BaseModel):
    id_cliente: int
    id_veiculo: int
    dias: int
    observacoes: Optional[str] = None

class LocacaoUpdate(BaseModel):
    observacoes: Optional[str] = None

class LocacaoResponse(BaseModel):
    id: int
    id_cliente: int
    id_veiculo: int
    data_inicio: datetime
    data_fim: datetime
    dias: int
    valor_total: float
    multa_atraso: float
    ativa: bool
    observacoes: Optional[str] = None
    
    class Config:
        from_attributes = True

class LocacaoDetalhladaResponse(LocacaoResponse):
    cliente: ClienteResponse
    veiculo: VeiculoResponse
    pagamentos: List[PagamentoResponse] = []


# ===== SCHEMAS LANÇAMENTOS (contábeis) =====

class LancamentoCreate(BaseModel):
    descricao: str
    valor: float
    data_lancamento: date
    tipo: str  # receita | despesa
    plano_conta_id: int
    forma_pagamento_id: int
    pago: bool = False

class LancamentoUpdate(BaseModel):
    descricao: Optional[str] = None
    valor: Optional[float] = None
    data_lancamento: Optional[date] = None
    tipo: Optional[str] = None
    plano_conta_id: Optional[int] = None
    forma_pagamento_id: Optional[int] = None
    pago: Optional[bool] = None

class LancamentoResponse(BaseModel):
    id: int
    descricao: str
    valor: float
    data_lancamento: date
    tipo: str
    plano_conta_id: int
    forma_pagamento_id: int
    pago: bool

    class Config:
        from_attributes = True


class LancamentoListResponse(LancamentoResponse):
    """Resposta da listagem com nomes de plano_conta e forma_pagamento (JOIN)."""
    plano_conta: Optional[str] = None
    forma_pagamento: Optional[str] = None


class PlanoContaResponse(BaseModel):
    id: int
    nome: str

    class Config:
        from_attributes = True


class PlanoContaCreate(BaseModel):
    nome: str


# ===== ENDPOINTS FINANCEIRO =====

@app.get("/plano-contas/", response_model=List[PlanoContaResponse])
def listar_plano_contas(db: Session = Depends(get_db)):
    """Lista todos os planos de conta (para selects no frontend)."""
    return db.query(models.PlanoConta).order_by(models.PlanoConta.nome).all()


@app.post("/plano-contas/", response_model=PlanoContaResponse, status_code=status.HTTP_201_CREATED)
def criar_plano_conta(plano: PlanoContaCreate, db: Session = Depends(get_db)):
    """Cria um novo plano de conta."""
    nome = plano.nome.strip()
    if not nome:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nome do plano de conta é obrigatório"
        )
    existente = db.query(models.PlanoConta).filter(models.PlanoConta.nome == nome).first()
    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Plano de conta '{nome}' já existe"
        )
    novo = models.PlanoConta(nome=nome)
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo


@app.post("/financeiro", response_model=LancamentoResponse, status_code=status.HTTP_201_CREATED)
def criar_lancamento(lancamento: LancamentoCreate, db: Session = Depends(get_db)):
    """Cria um novo lançamento financeiro."""
    # Verificar se forma de pagamento existe
    forma = db.query(models.FormaPagamento).filter(models.FormaPagamento.id == lancamento.forma_pagamento_id).first()
    if not forma:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Forma de pagamento não encontrada"
        )
    novo = models.LancamentoFinanceiro(
        descricao=lancamento.descricao,
        valor=lancamento.valor,
        data_lancamento=lancamento.data_lancamento,
        tipo=lancamento.tipo,
        id_plano_conta=lancamento.plano_conta_id,
        id_forma_pagamento=lancamento.forma_pagamento_id,
        pago=lancamento.pago,
    )
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return LancamentoResponse(
        id=novo.id,
        descricao=novo.descricao,
        valor=novo.valor,
        data_lancamento=novo.data_lancamento,
        tipo=novo.tipo,
        plano_conta_id=novo.id_plano_conta,
        forma_pagamento_id=novo.id_forma_pagamento,
        pago=novo.pago,
    )


@app.get("/financeiro", response_model=List[LancamentoListResponse])
def listar_lancamentos(
    tipo: Optional[str] = None,
    plano_conta_id: Optional[int] = None,
    forma_pagamento_id: Optional[int] = None,
    pago: Optional[bool] = None,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Lista lançamentos financeiros com filtros. Inclui nomes de plano_conta e forma_pagamento (JOIN)."""
    query = (
        db.query(models.LancamentoFinanceiro)
        .options(joinedload(models.LancamentoFinanceiro.forma_pagamento))
    )
    if tipo is not None:
        query = query.filter(models.LancamentoFinanceiro.tipo == tipo)
    if plano_conta_id is not None:
        query = query.filter(models.LancamentoFinanceiro.id_plano_conta == plano_conta_id)
    if forma_pagamento_id is not None:
        query = query.filter(models.LancamentoFinanceiro.id_forma_pagamento == forma_pagamento_id)
    if pago is not None:
        query = query.filter(models.LancamentoFinanceiro.pago == pago)
    if data_inicio is not None:
        query = query.filter(models.LancamentoFinanceiro.data_lancamento >= data_inicio)
    if data_fim is not None:
        query = query.filter(models.LancamentoFinanceiro.data_lancamento <= data_fim)
    query = query.order_by(models.LancamentoFinanceiro.data_lancamento.desc())
    rows = query.limit(limit).all()

    # Buscar nomes de plano_contas (tabela pode não ter FK no lancamento)
    plano_ids = {r.id_plano_conta for r in rows}
    plano_nomes = {}
    if plano_ids:
        planos = db.query(models.PlanoConta).filter(models.PlanoConta.id.in_(plano_ids)).all()
        plano_nomes = {p.id: p.nome for p in planos}

    return [
        LancamentoListResponse(
            id=r.id,
            descricao=r.descricao,
            valor=r.valor,
            data_lancamento=r.data_lancamento,
            tipo=r.tipo,
            plano_conta_id=r.id_plano_conta,
            forma_pagamento_id=r.id_forma_pagamento,
            pago=r.pago,
            plano_conta=plano_nomes.get(r.id_plano_conta),
            forma_pagamento=r.forma_pagamento.nome if r.forma_pagamento else None,
        )
        for r in rows
    ]


@app.get("/financeiro/{lancamento_id}", response_model=LancamentoListResponse)
def obter_lancamento(lancamento_id: int, db: Session = Depends(get_db)):
    """Obtém um lançamento financeiro pelo ID (com nomes de plano_conta e forma_pagamento)."""
    lancamento = (
        db.query(models.LancamentoFinanceiro)
        .options(joinedload(models.LancamentoFinanceiro.forma_pagamento))
        .filter(models.LancamentoFinanceiro.id == lancamento_id)
        .first()
    )
    if not lancamento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lançamento não encontrado"
        )
    plano_nome = None
    if lancamento.id_plano_conta:
        pc = db.query(models.PlanoConta).filter(models.PlanoConta.id == lancamento.id_plano_conta).first()
        plano_nome = pc.nome if pc else None
    return LancamentoListResponse(
        id=lancamento.id,
        descricao=lancamento.descricao,
        valor=lancamento.valor,
        data_lancamento=lancamento.data_lancamento,
        tipo=lancamento.tipo,
        plano_conta_id=lancamento.id_plano_conta,
        forma_pagamento_id=lancamento.id_forma_pagamento,
        pago=lancamento.pago,
        plano_conta=plano_nome,
        forma_pagamento=lancamento.forma_pagamento.nome if lancamento.forma_pagamento else None,
    )


@app.put("/financeiro/{lancamento_id}", response_model=LancamentoListResponse)
def atualizar_lancamento(lancamento_id: int, body: LancamentoUpdate, db: Session = Depends(get_db)):
    """Atualiza um lançamento financeiro."""
    lancamento = db.query(models.LancamentoFinanceiro).filter(models.LancamentoFinanceiro.id == lancamento_id).first()
    if not lancamento:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lançamento não encontrado")
    d = body.model_dump(exclude_unset=True)
    if "plano_conta_id" in d:
        d["id_plano_conta"] = d.pop("plano_conta_id")
    if "forma_pagamento_id" in d:
        d["id_forma_pagamento"] = d.pop("forma_pagamento_id")
    for k, v in d.items():
        setattr(lancamento, k, v)
    db.commit()
    db.refresh(lancamento)
    plano_nome = None
    if lancamento.id_plano_conta:
        pc = db.query(models.PlanoConta).filter(models.PlanoConta.id == lancamento.id_plano_conta).first()
        plano_nome = pc.nome if pc else None
    return LancamentoListResponse(
        id=lancamento.id, descricao=lancamento.descricao, valor=lancamento.valor,
        data_lancamento=lancamento.data_lancamento, tipo=lancamento.tipo,
        plano_conta_id=lancamento.id_plano_conta, forma_pagamento_id=lancamento.id_forma_pagamento,
        pago=lancamento.pago, plano_conta=plano_nome,
        forma_pagamento=lancamento.forma_pagamento.nome if lancamento.forma_pagamento else None,
    )


@app.delete("/financeiro/{lancamento_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_lancamento(lancamento_id: int, db: Session = Depends(get_db)):
    """Exclui um lançamento financeiro."""
    lancamento = db.query(models.LancamentoFinanceiro).filter(models.LancamentoFinanceiro.id == lancamento_id).first()
    if not lancamento:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lançamento não encontrado")
    db.delete(lancamento)
    db.commit()


@app.get("/financeiro/dashboard/saldo")
def dashboard_financeiro(db: Session = Depends(get_db)):
    """Retorna saldo (receitas - despesas) considerando apenas lançamentos marcados como pagos."""
    from datetime import date
    hoje = date.today()
    ano_atual = hoje.year
    lancamentos_pagos = db.query(models.LancamentoFinanceiro).filter(models.LancamentoFinanceiro.pago == True).all()
    saldo = sum((l.valor if l.tipo == "receita" else -l.valor) for l in lancamentos_pagos)
    lancamentos_ano = db.query(models.LancamentoFinanceiro).filter(
        models.LancamentoFinanceiro.data_lancamento >= date(ano_atual, 1, 1),
        models.LancamentoFinanceiro.data_lancamento <= date(ano_atual, 12, 31),
    ).all()
    por_mes = {m: 0.0 for m in range(1, 13)}
    for l in lancamentos_ano:
        por_mes[l.data_lancamento.month] += l.valor if l.tipo == "receita" else -l.valor
    mensal = [{"mes": m, "total": round(por_mes[m], 2)} for m in range(1, 13)]
    return {"saldo": round(saldo, 2), "mensal": mensal}


@app.get("/financeiro/dashboard/faturamento-mensal")
def faturamento_mensal(ano: Optional[int] = None, db: Session = Depends(get_db)):
    """Retorna faturamento (pagamentos) e receitas (lançamentos tipo receita) por mês para o ano informado (default: ano atual)."""
    from datetime import date
    hoje = date.today()
    ano_usar = ano if ano is not None else hoje.year
    por_mes_fat = {m: 0.0 for m in range(1, 13)}
    por_mes_rec = {m: 0.0 for m in range(1, 13)}
    # Faturamento: soma de pagamentos por mês
    pagamentos_ano = (
        db.query(models.Pagamento)
        .filter(
            extract("year", models.Pagamento.data_pagamento) == ano_usar,
            extract("month", models.Pagamento.data_pagamento) >= 1,
            extract("month", models.Pagamento.data_pagamento) <= 12,
        )
        .all()
    )
    for p in pagamentos_ano:
        por_mes_fat[p.data_pagamento.month] += float(p.valor_pagamento)
    # Receitas: lançamentos tipo receita por mês
    lancamentos_ano = (
        db.query(models.LancamentoFinanceiro)
        .filter(
            models.LancamentoFinanceiro.data_lancamento >= date(ano_usar, 1, 1),
            models.LancamentoFinanceiro.data_lancamento <= date(ano_usar, 12, 31),
            models.LancamentoFinanceiro.tipo == "receita",
        )
        .all()
    )
    for l in lancamentos_ano:
        por_mes_rec[l.data_lancamento.month] += float(l.valor)
    mensal = [
        {"mes": m, "faturamento": round(por_mes_fat[m], 2), "receitas": round(por_mes_rec[m], 2)}
        for m in range(1, 13)
    ]
    return {"ano": ano_usar, "mensal": mensal}


# ===== ENDPOINTS CLIENTES =====

@app.post("/clientes/", response_model=ClienteResponse, status_code=status.HTTP_201_CREATED)
def criar_cliente(cliente: ClienteCreate, db: Session = Depends(get_db)):
    """Cria um novo cliente"""
    # Verificar se CPF já existe
    db_cliente = db.query(models.Cliente).filter(models.Cliente.cpf == cliente.cpf).first()
    if db_cliente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cliente com CPF {cliente.cpf} já existe"
        )
    
    # Converter data de nascimento se fornecida
    data_nascimento = None
    if cliente.data_nascimento:
        try:
            data_nascimento = datetime.strptime(cliente.data_nascimento, "%d/%m/%Y")
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Data de nascimento deve estar no formato dd/mm/yyyy"
            )
    
    novo_cliente = models.Cliente(
        nome=cliente.nome,
        cpf=cliente.cpf,
        telefone=cliente.telefone,
        email=cliente.email,
        cep=cliente.cep,
        endereco=cliente.endereco,
        data_nascimento=data_nascimento
    )
    db.add(novo_cliente)
    db.commit()
    db.refresh(novo_cliente)
    return novo_cliente

@app.get("/clientes/", response_model=List[ClienteResponse])
def listar_clientes(db: Session = Depends(get_db)):
    """Lista todos os clientes"""
    return db.query(models.Cliente).all()

@app.get("/clientes/{cliente_id}", response_model=ClienteResponse)
def obter_cliente(cliente_id: int, db: Session = Depends(get_db)):
    """Obtém um cliente específico"""
    cliente = db.query(models.Cliente).filter(models.Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )
    return cliente

@app.put("/clientes/{cliente_id}", response_model=ClienteResponse)
def atualizar_cliente(cliente_id: int, cliente_update: ClienteUpdate, db: Session = Depends(get_db)):
    """Atualiza dados de um cliente"""
    cliente = db.query(models.Cliente).filter(models.Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )
    
    dados_atualizacao = cliente_update.model_dump(exclude_unset=True)
    for campo, valor in dados_atualizacao.items():
        setattr(cliente, campo, valor)
    
    db.commit()
    db.refresh(cliente)
    return cliente

@app.delete("/clientes/{cliente_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_cliente(cliente_id: int, db: Session = Depends(get_db)):
    """Deleta um cliente"""
    cliente = db.query(models.Cliente).filter(models.Cliente.id == cliente_id).first()
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )
    
    # Verificar se tem locações
    locacoes = db.query(models.Locacao).filter(models.Locacao.id_cliente == cliente_id).first()
    if locacoes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível deletar um cliente com locações"
        )
    
    db.delete(cliente)
    db.commit()

# ===== ENDPOINTS FORMAS DE PAGAMENTO =====

@app.post("/formas-pagamento/", response_model=FormaPagamentoResponse, status_code=status.HTTP_201_CREATED)
def criar_forma_pagamento(forma: FormaPagamentoCreate, db: Session = Depends(get_db)):
    """Cria uma nova forma de pagamento"""
    # Verificar se nome já existe
    db_forma = db.query(models.FormaPagamento).filter(models.FormaPagamento.nome == forma.nome).first()
    if db_forma:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Forma de pagamento '{forma.nome}' já existe"
        )
    
    nova_forma = models.FormaPagamento(**forma.model_dump())
    db.add(nova_forma)
    db.commit()
    db.refresh(nova_forma)
    return nova_forma

@app.get("/formas-pagamento/", response_model=List[FormaPagamentoResponse])
def listar_formas_pagamento(apenas_ativas: bool = False, db: Session = Depends(get_db)):
    """Lista todas as formas de pagamento"""
    query = db.query(models.FormaPagamento)
    if apenas_ativas:
        query = query.filter(models.FormaPagamento.ativa == True)
    return query.all()

@app.get("/formas-pagamento/{forma_id}", response_model=FormaPagamentoResponse)
def obter_forma_pagamento(forma_id: int, db: Session = Depends(get_db)):
    """Obtém uma forma de pagamento específica"""
    forma = db.query(models.FormaPagamento).filter(models.FormaPagamento.id == forma_id).first()
    if not forma:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Forma de pagamento não encontrada"
        )
    return forma

@app.put("/formas-pagamento/{forma_id}", response_model=FormaPagamentoResponse)
def atualizar_forma_pagamento(forma_id: int, forma_update: FormaPagamentoUpdate, db: Session = Depends(get_db)):
    """Atualiza uma forma de pagamento"""
    forma = db.query(models.FormaPagamento).filter(models.FormaPagamento.id == forma_id).first()
    if not forma:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Forma de pagamento não encontrada"
        )
    
    dados_atualizacao = forma_update.model_dump(exclude_unset=True)
    for campo, valor in dados_atualizacao.items():
        setattr(forma, campo, valor)
    
    db.commit()
    db.refresh(forma)
    return forma

@app.delete("/formas-pagamento/{forma_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_forma_pagamento(forma_id: int, db: Session = Depends(get_db)):
    """Deleta uma forma de pagamento"""
    forma = db.query(models.FormaPagamento).filter(models.FormaPagamento.id == forma_id).first()
    if not forma:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Forma de pagamento não encontrada"
        )
    
    # Verificar se tem pagamentos
    pagamentos = db.query(models.Pagamento).filter(models.Pagamento.id_forma_pagamento == forma_id).first()
    if pagamentos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível deletar uma forma de pagamento com pagamentos registrados"
        )
    
    db.delete(forma)
    db.commit()

# ===== ENDPOINTS LOCAÇÕES =====

@app.post("/locacoes/", response_model=LocacaoResponse, status_code=status.HTTP_201_CREATED)
def criar_locacao(locacao: LocacaoCreate, db: Session = Depends(get_db)):
    """Cria uma nova locação"""
    # Verificar se cliente existe
    cliente = db.query(models.Cliente).filter(models.Cliente.id == locacao.id_cliente).first()
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )
    
    # Verificar se veículo existe e está disponível
    veiculo = db.query(models.Veiculo).filter(models.Veiculo.id == locacao.id_veiculo).first()
    if not veiculo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Veículo não encontrado"
        )
    
    if not veiculo.disponivel:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Veículo não está disponível"
        )
    
    # Validar dias
    if locacao.dias <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Número de dias deve ser maior que zero"
        )
    
    # Criar locação
    data_inicio = datetime.now()
    data_fim = data_inicio + timedelta(days=locacao.dias)
    valor_total = locacao.dias * veiculo.valor_diaria
    
    nova_locacao = models.Locacao(
        id_cliente=locacao.id_cliente,
        id_veiculo=locacao.id_veiculo,
        data_inicio=data_inicio,
        data_fim=data_fim,
        dias=locacao.dias,
        valor_total=valor_total,
        observacoes=locacao.observacoes
    )
    
    # Marcar veículo como indisponível
    veiculo.disponivel = False
    
    db.add(nova_locacao)
    db.commit()
    db.refresh(nova_locacao)
    return nova_locacao

@app.get("/locacoes/", response_model=List[LocacaoDetalhladaResponse])
def listar_locacoes(apenas_ativas: bool = False, db: Session = Depends(get_db)):
    """Lista todas as locações (com cliente, veículo com marca/modelo e pagamentos)."""
    query = (
        db.query(models.Locacao)
        .options(
            joinedload(models.Locacao.cliente),
            joinedload(models.Locacao.veiculo).joinedload(models.Veiculo.modelo_ref).joinedload(models.ModeloVeiculo.marca),
            joinedload(models.Locacao.pagamentos),
        )
    )
    if apenas_ativas:
        query = query.filter(models.Locacao.ativa == True)
    return query.all()

@app.get("/locacoes/{locacao_id}", response_model=LocacaoDetalhladaResponse)
def obter_locacao(locacao_id: int, db: Session = Depends(get_db)):
    """Obtém uma locação específica (com cliente, veículo com marca/modelo e pagamentos)."""
    locacao = (
        db.query(models.Locacao)
        .options(
            joinedload(models.Locacao.cliente),
            joinedload(models.Locacao.veiculo).joinedload(models.Veiculo.modelo_ref).joinedload(models.ModeloVeiculo.marca),
            joinedload(models.Locacao.pagamentos),
        )
        .filter(models.Locacao.id == locacao_id)
        .first()
    )
    if not locacao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Locação não encontrada"
        )
    return locacao

@app.put("/locacoes/{locacao_id}", response_model=LocacaoResponse)
def atualizar_locacao(locacao_id: int, locacao_update: LocacaoUpdate, db: Session = Depends(get_db)):
    """Atualiza uma locação"""
    locacao = db.query(models.Locacao).filter(models.Locacao.id == locacao_id).first()
    if not locacao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Locação não encontrada"
        )
    
    dados_atualizacao = locacao_update.model_dump(exclude_unset=True)
    for campo, valor in dados_atualizacao.items():
        setattr(locacao, campo, valor)
    
    db.commit()
    db.refresh(locacao)
    return locacao

@app.post("/locacoes/{locacao_id}/finalizar", status_code=status.HTTP_200_OK)
def finalizar_locacao(locacao_id: int, db: Session = Depends(get_db)):
    """Finaliza uma locação"""
    locacao = db.query(models.Locacao).filter(models.Locacao.id == locacao_id).first()
    if not locacao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Locação não encontrada"
        )
    
    if not locacao.ativa:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Locação já foi finalizada"
        )
    
    # Calcular multa de atraso (50% do valor da diária por dia)
    data_devolucao = datetime.now()
    if data_devolucao > locacao.data_fim:
        dias_atraso = (data_devolucao - locacao.data_fim).days
        multa = dias_atraso * (locacao.valor_total / locacao.dias * 0.5)
        locacao.multa_atraso = multa
        locacao.valor_total += multa
    
    # Marcar como finalizada
    locacao.ativa = False
    
    # Marcar veículo como disponível
    veiculo = db.query(models.Veiculo).filter(models.Veiculo.id == locacao.id_veiculo).first()
    if veiculo:
        veiculo.disponivel = True
    
    db.commit()
    db.refresh(locacao)
    
    return {
        "id": locacao.id,
        "status": "Finalizada",
        "valor_total": locacao.valor_total,
        "multa_atraso": locacao.multa_atraso,
        "mensagem": f"Locação finalizada com sucesso. Multa de atraso: R$ {locacao.multa_atraso:.2f}"
    }

# ===== ENDPOINTS PAGAMENTOS =====

@app.post("/locacoes/{locacao_id}/pagamentos/", response_model=PagamentoResponse, status_code=status.HTTP_201_CREATED)
def registrar_pagamento(locacao_id: int, pagamento: PagamentoCreate, db: Session = Depends(get_db)):
    """Registra um pagamento para uma locação"""
    # Verificar se locação existe
    locacao = db.query(models.Locacao).filter(models.Locacao.id == locacao_id).first()
    if not locacao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Locação não encontrada"
        )
    
    # Verificar se forma de pagamento existe
    forma = db.query(models.FormaPagamento).filter(models.FormaPagamento.id == pagamento.id_forma_pagamento).first()
    if not forma:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Forma de pagamento não encontrada"
        )
    
    # Validar valor
    if pagamento.valor_pagamento <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Valor de pagamento deve ser maior que zero"
        )
    
    # Calcular saldo pendente
    total_pagado = sum(p.valor_pagamento for p in locacao.pagamentos)
    saldo_pendente = locacao.valor_total - total_pagado
    
    if pagamento.valor_pagamento > saldo_pendente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Valor do pagamento (R$ {pagamento.valor_pagamento:.2f}) excede o saldo pendente (R$ {saldo_pendente:.2f})"
        )
    
    # Registrar pagamento
    novo_pagamento = models.Pagamento(
        id_locacao=locacao_id,
        id_forma_pagamento=pagamento.id_forma_pagamento,
        valor_pagamento=pagamento.valor_pagamento,
        numero_comprovante=pagamento.numero_comprovante,
        observacoes=pagamento.observacoes
    )
    
    db.add(novo_pagamento)
    db.commit()
    db.refresh(novo_pagamento)
    return novo_pagamento

@app.get("/locacoes/{locacao_id}/pagamentos/", response_model=List[PagamentoResponse])
def listar_pagamentos(locacao_id: int, db: Session = Depends(get_db)):
    """Lista todos os pagamentos de uma locação"""
    locacao = db.query(models.Locacao).filter(models.Locacao.id == locacao_id).first()
    if not locacao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Locação não encontrada"
        )
    return locacao.pagamentos

@app.get("/locacoes/{locacao_id}/resumo/")
def obter_resumo_locacao(locacao_id: int, db: Session = Depends(get_db)):
    """Obtém um resumo da locação com saldo pendente"""
    locacao = (
        db.query(models.Locacao)
        .options(
            joinedload(models.Locacao.veiculo).joinedload(models.Veiculo.modelo_ref).joinedload(models.ModeloVeiculo.marca),
        )
        .filter(models.Locacao.id == locacao_id)
        .first()
    )
    if not locacao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Locação não encontrada"
        )
    
    total_pagado = sum(p.valor_pagamento for p in locacao.pagamentos)
    saldo_pendente = locacao.valor_total - total_pagado
    
    return {
        "id": locacao.id,
        "cliente": locacao.cliente.nome,
        "veiculo": f"{locacao.veiculo.marca_nome} {locacao.veiculo.modelo_nome}",
        "valor_total": locacao.valor_total,
        "multa_atraso": locacao.multa_atraso,
        "total_pagado": total_pagado,
        "saldo_pendente": saldo_pendente,
        "quitada": saldo_pendente <= 0,
        "ativa": locacao.ativa
    }

# ===== FRONTEND E HEALTH CHECK =====

@app.get("/locacao_veiculos.html", include_in_schema=False)
def serve_frontend():
    """Serve a interface web (mesma origem que a API: banco + API + frontend conectados)."""
    path = BASE_DIR / "locacao_veiculos.html"
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Frontend não encontrado")
    return FileResponse(path, media_type="text/html")

@app.get("/")
def root():
    """Redireciona para a interface web."""
    return RedirectResponse(url="/locacao_veiculos.html", status_code=302)

HEALTH_NO_CACHE = {"Cache-Control": "no-store"}


@app.get("/health")
def health():
    """Verifica saúde da API e conexão com o banco de dados."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return JSONResponse(
            content={"status": "ok", "database": "conectado"},
            headers=HEALTH_NO_CACHE,
        )
    except Exception as e:
        return JSONResponse(
            content={
                "status": "ok",
                "database": "erro",
                "detalhe": str(e),
                "dica": "Verifique se o MySQL/MariaDB está rodando (ex.: localhost:3307 no XAMPP) e se o banco 'locacao_veiculos' existe.",
            },
            headers=HEALTH_NO_CACHE,
        )

# ===== RELATÓRIOS PDF =====

@app.get("/relatorios/pdf/vencidas", response_class=Response)
def pdf_contas_vencidas(db: Session = Depends(get_db)):
    """Gera PDF com contas vencidas (não pagas com vencimento anterior a hoje)."""
    try:
        hoje = date.today()
        query = (
            db.query(models.LancamentoFinanceiro)
            .options(joinedload(models.LancamentoFinanceiro.forma_pagamento))
            .filter(
                models.LancamentoFinanceiro.pago == False,
                models.LancamentoFinanceiro.data_vencimento.isnot(None),
                models.LancamentoFinanceiro.data_vencimento < hoje,
            )
            .order_by(models.LancamentoFinanceiro.data_vencimento.asc())
        )
        rows = query.all()
        plano_ids = {r.id_plano_conta for r in rows if r.id_plano_conta}
        plano_nomes = {}
        if plano_ids:
            planos = db.query(models.PlanoConta).filter(models.PlanoConta.id.in_(plano_ids)).all()
            plano_nomes = {p.id: p.nome for p in planos}
        registros = [
            {
                "descricao": r.descricao,
                "valor": r.valor,
                "data_vencimento": r.data_vencimento,
                "plano_conta": plano_nomes.get(r.id_plano_conta),
                "forma_pagamento": r.forma_pagamento.nome if r.forma_pagamento else None,
            }
            for r in rows
        ]
        pdf_bytes = gera_pdf_vencidas(registros)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=contas_vencidas.pdf"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao gerar PDF de contas vencidas: {str(e)}",
        )


@app.get("/relatorios/pdf/mensal", response_class=Response)
def pdf_relatorio_mensal(db: Session = Depends(get_db)):
    """Gera PDF com todos os lançamentos financeiros do mês atual (tabela com tipo e totais)."""
    try:
        hoje = date.today()
        query = (
            db.query(models.LancamentoFinanceiro)
            .options(joinedload(models.LancamentoFinanceiro.forma_pagamento))
            .filter(
                extract("month", models.LancamentoFinanceiro.data_lancamento) == hoje.month,
                extract("year", models.LancamentoFinanceiro.data_lancamento) == hoje.year,
            )
            .order_by(models.LancamentoFinanceiro.data_lancamento.asc())
        )
        rows = query.all()
        registros = [
            {
                "data_lancamento": r.data_lancamento,
                "descricao": r.descricao,
                "valor": r.valor,
                "tipo": r.tipo,
                "forma_pagamento": r.forma_pagamento.nome if r.forma_pagamento else None,
            }
            for r in rows
        ]
        pdf_bytes = gera_pdf_mensal(registros)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=relatorio_mensal.pdf"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao gerar PDF do relatório mensal: {str(e)}",
        )


@app.get("/relatorios/pdf/sistema", response_class=Response)
def pdf_relatorio_sistema(db: Session = Depends(get_db)):
    """Gera PDF do relatório geral do sistema (estatísticas + resumo financeiro)."""
    try:
        stats = obter_estatisticas(db)
        dash = dashboard_financeiro(db)
        pdf_bytes = gera_pdf_sistema(
            stats,
            saldo_financeiro=dash["saldo"],
            mensal=dash.get("mensal", []),
        )
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=relatorio_sistema.pdf"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao gerar PDF do relatório do sistema: {str(e)}",
        )


# ===== ESTATÍSTICAS =====

@app.get("/estatisticas/")
def obter_estatisticas(db: Session = Depends(get_db)):
    """Obtém estatísticas do sistema"""
    hoje = date.today()
    total_veiculos = db.query(models.Veiculo).count()
    veiculos_disponiveis = db.query(models.Veiculo).filter(models.Veiculo.disponivel == True).count()
    veiculos_alugados = total_veiculos - veiculos_disponiveis

    total_clientes = db.query(models.Cliente).count()

    total_locacoes = db.query(models.Locacao).count()
    locacoes_ativas = db.query(models.Locacao).filter(models.Locacao.ativa == True).count()

    total_formas = db.query(models.FormaPagamento).count()

    total_pagamentos = db.query(models.Pagamento).count()
    valor_total_pagado = db.query(models.Pagamento).with_entities(
        models.Pagamento.valor_pagamento
    ).all()
    valor_pagado = sum(p[0] for p in valor_total_pagado) if valor_total_pagado else 0.0

    # Receita do mês: soma de pagamentos com data_pagamento no mês/ano atual (Opção A)
    pagamentos_mes = (
        db.query(models.Pagamento)
        .filter(
            extract("month", models.Pagamento.data_pagamento) == hoje.month,
            extract("year", models.Pagamento.data_pagamento) == hoje.year,
        )
        .with_entities(models.Pagamento.valor_pagamento)
        .all()
    )
    receita_mes = sum(p[0] for p in pagamentos_mes) if pagamentos_mes else 0.0

    return {
        "veiculos": {
            "total": total_veiculos,
            "disponivel": veiculos_disponiveis,
            "em_uso": veiculos_alugados,
            "alugados": veiculos_alugados,
        },
        "clientes": {
            "total": total_clientes
        },
        "locacoes": {
            "total": total_locacoes,
            "ativas": locacoes_ativas,
            "finalizadas": total_locacoes - locacoes_ativas
        },
        "formas_pagamento": {
            "total": total_formas
        },
        "pagamentos": {
            "total_registros": total_pagamentos,
            "valor_total_pago": valor_pagado
        },
        "receita_mes": round(receita_mes, 2),
    }
