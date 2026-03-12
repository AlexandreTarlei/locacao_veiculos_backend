"""
API FastAPI - Locação de Veículos e Controle Financeiro.
Entrypoint: uvicorn app:app --reload --host 0.0.0.0 --port 8000 (rodar de dentro da pasta backend)
"""
import pathlib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config import DATABASE_URL
from database import engine, Base, SessionLocal, get_db
import models
from auth import router as router_auth, router_api, hash_senha
from routes import router_clientes, router_veiculos, router_locacoes, router_reservas, router_reservas_api, router_contratos, router_contratos_api, router_financeiro, router_relatorios, router_dashboard, router_dashboard_api, router_tipo_usuario, router_usuarios, router_manutencoes, router_manutencao_programada, router_notificacoes, router_configuracoes

# Criar tabelas (não impede a API de subir se o MySQL estiver offline)
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"[AVISO] Banco não disponível na subida: {e}. Conecte o MySQL e reinicie para dados completos.")

TIPOS_USUARIO_PADRAO = [
    {"codigo": "ADMIN", "nome": "Administrador"},
    {"codigo": "GERENTE", "nome": "Gerente"},
    {"codigo": "OPERACIONAL", "nome": "Operador"},
]

FORMAS_PAGAMENTO_PADRAO = [
    {"nome": "PIX", "descricao": "Pagamento instantâneo via PIX", "ativa": True},
    {"nome": "Cartão de crédito", "descricao": "Cartão de crédito à vista ou parcelado", "ativa": True},
    {"nome": "Cartão de débito", "descricao": "Cartão de débito", "ativa": True},
    {"nome": "Dinheiro", "descricao": "Pagamento em espécie", "ativa": True},
    {"nome": "Boleto bancário", "descricao": "Boleto bancário", "ativa": True},
    {"nome": "Transferência bancária", "descricao": "Transferência TED/DOC", "ativa": True},
    {"nome": "Cheque", "descricao": "Pagamento com cheque", "ativa": True},
    {"nome": "Vale/cupom", "descricao": "Vale ou cupom de desconto", "ativa": True},
]


def seed_tipos_usuario():
    db = SessionLocal()
    try:
        if db.query(models.TipoUsuario).count() == 0:
            for tu in TIPOS_USUARIO_PADRAO:
                db.add(models.TipoUsuario(**tu))
            db.commit()
    finally:
        db.close()


def seed_formas_pagamento():
    db = SessionLocal()
    try:
        if db.query(models.FormaPagamento).count() == 0:
            for fp in FORMAS_PAGAMENTO_PADRAO:
                db.add(models.FormaPagamento(**fp))
            db.commit()
    finally:
        db.close()


def seed_usuarios():
    db = SessionLocal()
    try:
        # Garante que tipos de usuário existam
        if db.query(models.TipoUsuario).count() == 0:
            for tu in TIPOS_USUARIO_PADRAO:
                db.add(models.TipoUsuario(**tu))
            db.commit()
        if db.query(models.Usuario).count() == 0:
            tipo_admin = db.query(models.TipoUsuario).filter(models.TipoUsuario.codigo == "ADMIN").first()
            admin = models.Usuario(
                nome="Administrador",
                email="admin@admin.com",
                senha=hash_senha("admin"),
                id_tipo_usuario=tipo_admin.id if tipo_admin else None,
                nivel="ADMIN",
                ativo=True,
            )
            db.add(admin)
            db.commit()
    finally:
        db.close()


def seed_empresa():
    """Garante que exista empresa id=1 com status ativo para o login não retornar 403."""
    db = SessionLocal()
    try:
        empresa = db.query(models.Empresa).filter(models.Empresa.id == 1).first()
        if not empresa:
            db.add(models.Empresa(id=1, status="ativo"))
            db.commit()
        elif getattr(empresa, "status", None) != "ativo":
            empresa.status = "ativo"
            db.commit()
    except Exception as e:
        print(f"[AVISO] Seed empresa: {e}")
    finally:
        db.close()


app = FastAPI(
    title="API Locação de Veículos e Controle Financeiro",
    description="Sistema integrado: locações, clientes, veículos e módulo financeiro",
    version="1.0.0",
)


@app.on_event("startup")
def on_startup():
    try:
        seed_tipos_usuario()
        seed_formas_pagamento()
        seed_empresa()
        seed_usuarios()
    except Exception as e:
        print(f"[AVISO] Seeds na subida (banco indisponível?): {e}. API no ar; conecte o MySQL para dados completos.")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def _include(maybe_router):
    if maybe_router is not None:
        app.include_router(maybe_router)

_include(router_auth)
_include(router_api)
_include(router_dashboard)
_include(router_dashboard_api)
_include(router_tipo_usuario)
_include(router_usuarios)
_include(router_financeiro)
_include(router_locacoes)
_include(router_reservas)
_include(router_reservas_api)
_include(router_contratos)
_include(router_contratos_api)
_include(router_clientes)
_include(router_veiculos)
_include(router_manutencoes)
_include(router_manutencao_programada)
_include(router_notificacoes)
_include(router_configuracoes)
_include(router_relatorios)

# Servir frontend em /app (abrir http://localhost:8000/app/login.html)
_frontend = pathlib.Path(__file__).resolve().parent.parent / "frontend"
if _frontend.exists():
    app.mount("/app", StaticFiles(directory=str(_frontend), html=True), name="frontend")
