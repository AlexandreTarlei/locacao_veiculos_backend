"""
Testes para a API FastAPI (api.py).
Usa SQLite em memória para não depender do MySQL na hora dos testes.
"""
import os
import sys
from datetime import datetime, date, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Garante o diretório do projeto no path
_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _root)
# Backend no path (no final) para imports "from services.xxx" dentro de backend.routes
sys.path.append(os.path.join(_root, "backend"))

# Antes de importar api, trocar o engine do database por SQLite
# (arquivo único para todas as conexões verem as mesmas tabelas)
_test_db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_api.db")
if os.path.exists(_test_db_path):
    try:
        os.remove(_test_db_path)
    except Exception:
        pass
import database
_test_engine = create_engine(
    f"sqlite:///{_test_db_path}",
    connect_args={"check_same_thread": False},
)
database.engine = _test_engine
database.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_test_engine)

# Agora importar api (vai criar tabelas no SQLite)
from database import Base, get_db
import models
from api import app

# Criar tabelas no SQLite (api.py já chama create_all com engine, que agora é SQLite)
Base.metadata.create_all(bind=_test_engine)


def _get_test_db():
    """Sessão para os testes (usa o mesmo engine SQLite)."""
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client():
    """Client usando SQLite em memória (sem depender de MySQL)."""
    return TestClient(app)


@pytest.fixture
def client_sqlite():
    """Client com SQLite em memória e seed de formas de pagamento."""
    db = database.SessionLocal()
    try:
        if db.query(models.FormaPagamento).count() == 0:
            db.add(models.FormaPagamento(nome="PIX", descricao="PIX", ativa=True))
            db.add(models.FormaPagamento(nome="Dinheiro", descricao="Dinheiro", ativa=True))
            db.commit()
    finally:
        db.close()
    yield TestClient(app)


# ===== Endpoints que não dependem de dados no BD (ou só leitura) =====
class TestRootAndHealth:
    def test_root(self, client):
        r = client.get("/")
        assert r.status_code == 200
        data = r.json()
        assert "message" in data
        assert "API" in data["message"] or "Locação" in data["message"]
        assert "version" in data

    def test_health_retorna_status(self, client):
        r = client.get("/health")
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "ok"
        assert "database" in data


def _criar_marca_modelo(client, marca_nome="Toyota", modelo_nome="Corolla"):
    """Obtém ou cria uma marca e um modelo e retorna id_modelo."""
    marcas = client.get("/marcas/").json()
    marca = next((m for m in marcas if m["nome"] == marca_nome), None)
    if not marca:
        mr = client.post("/marcas/", json={"nome": marca_nome})
        mr.raise_for_status()
        marca = mr.json()
    modelos = client.get("/modelos/", params={"id_marca": marca["id"]}).json()
    mod = next((m for m in modelos if m["nome"] == modelo_nome), None)
    if not mod:
        modr = client.post("/modelos/", json={"id_marca": marca["id"], "nome": modelo_nome})
        modr.raise_for_status()
        mod = modr.json()
    return mod["id"] if isinstance(mod, dict) else mod.get("id")


# ===== Testes com SQLite em memória =====
class TestMarcasModelosAPI:
    def test_listar_marcas(self, client_sqlite):
        r = client_sqlite.get("/marcas/")
        assert r.status_code == 200
        assert r.json() == []

    def test_criar_marca_e_modelo(self, client_sqlite):
        r = client_sqlite.post("/marcas/", json={"nome": "Toyota"})
        assert r.status_code == 201
        marca = r.json()
        assert marca["nome"] == "Toyota"
        r2 = client_sqlite.post("/modelos/", json={"id_marca": marca["id"], "nome": "Corolla"})
        assert r2.status_code == 201
        assert r2.json()["nome"] == "Corolla"

    def test_listar_modelos_por_marca(self, client_sqlite):
        mr = client_sqlite.post("/marcas/", json={"nome": "Fiat"})
        mr.raise_for_status()
        id_marca = mr.json()["id"]
        client_sqlite.post("/modelos/", json={"id_marca": id_marca, "nome": "Uno"}).raise_for_status()
        r = client_sqlite.get("/modelos/", params={"id_marca": id_marca})
        assert r.status_code == 200
        assert len(r.json()) >= 1


class TestVeiculosAPI:
    def test_listar_veiculos_vazio(self, client_sqlite):
        r = client_sqlite.get("/veiculos/")
        assert r.status_code == 200
        assert r.json() == []

    def test_criar_veiculo(self, client_sqlite):
        id_modelo = _criar_marca_modelo(client_sqlite, "Toyota", "Corolla")
        payload = {
            "placa": "ABC1234",
            "id_modelo": id_modelo,
            "ano": 2023,
            "cor": "Prata",
            "quilometragem": 10000.0,
            "valor_diaria": 150.0,
        }
        r = client_sqlite.post("/veiculos/", json=payload)
        assert r.status_code == 201
        data = r.json()
        assert data["placa"] == "ABC1234"
        assert data["marca"] == "Toyota"
        assert data["modelo"] == "Corolla"
        assert data["disponivel"] is True
        assert "id" in data

    def test_criar_veiculo_placa_duplicada_falha(self, client_sqlite):
        id_modelo = _criar_marca_modelo(client_sqlite, "Honda", "Civic")
        payload = {
            "placa": "XYZ9999",
            "id_modelo": id_modelo,
            "ano": 2022,
            "cor": "Preto",
            "quilometragem": 5000.0,
            "valor_diaria": 180.0,
        }
        client_sqlite.post("/veiculos/", json=payload)
        r = client_sqlite.post("/veiculos/", json=payload)
        assert r.status_code == 400

    def test_obter_veiculo_inexistente(self, client_sqlite):
        r = client_sqlite.get("/veiculos/99999")
        assert r.status_code == 404


class TestClientesAPI:
    def test_listar_clientes_vazio(self, client_sqlite):
        r = client_sqlite.get("/clientes/")
        assert r.status_code == 200
        assert r.json() == []

    def test_criar_cliente(self, client_sqlite):
        payload = {
            "nome": "João Silva",
            "cpf": "12345678900",
            "telefone": "11987654321",
            "email": "joao@email.com",
            "cep": "01311100",
            "endereco": "Av. Paulista, 1000",
            "data_nascimento": "15/05/1990",
        }
        r = client_sqlite.post("/clientes/", json=payload)
        assert r.status_code == 201
        data = r.json()
        assert data["nome"] == "João Silva"
        assert data["cpf"] == "12345678900"
        assert "id" in data

    def test_criar_cliente_cpf_duplicado_falha(self, client_sqlite):
        payload = {
            "nome": "João",
            "cpf": "11122233344",
            "telefone": "11999999999",
            "email": "j@j.com",
            "cep": "01311100",
            "endereco": "Rua X",
        }
        client_sqlite.post("/clientes/", json=payload)
        r = client_sqlite.post("/clientes/", json=payload)
        assert r.status_code == 400


class TestFormasPagamentoAPI:
    def test_listar_formas_pagamento(self, client_sqlite):
        r = client_sqlite.get("/formas-pagamento/")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
        # Seed tem pelo menos PIX e Dinheiro
        assert len(data) >= 2

    def test_criar_forma_pagamento(self, client_sqlite):
        payload = {"nome": "Cartão de Crédito", "descricao": "Cartão", "ativa": True}
        r = client_sqlite.post("/formas-pagamento/", json=payload)
        assert r.status_code == 201
        assert r.json()["nome"] == "Cartão de Crédito"


class TestLocacoesAPI:
    def test_criar_locacao_fluxo_completo(self, client_sqlite):
        id_modelo = _criar_marca_modelo(client_sqlite, "Fiat", "Uno")
        cliente = client_sqlite.post("/clientes/", json={
            "nome": "Maria",
            "cpf": "98765432100",
            "telefone": "11988887777",
            "email": "maria@email.com",
            "cep": "01311100",
            "endereco": "Rua Y, 200",
        }).json()
        veiculo = client_sqlite.post("/veiculos/", json={
            "placa": "LOC2025",
            "id_modelo": id_modelo,
            "ano": 2020,
            "cor": "Branco",
            "quilometragem": 30000.0,
            "valor_diaria": 80.0,
        }).json()

        # Criar locação
        r = client_sqlite.post("/locacoes/", json={
            "id_cliente": cliente["id"],
            "id_veiculo": veiculo["id"],
            "dias": 5,
        })
        assert r.status_code == 201
        loc = r.json()
        assert loc["dias"] == 5
        assert loc["ativa"] is True
        assert loc["valor_total"] == 5 * 80.0  # 400.0

        # Listar locações
        r2 = client_sqlite.get("/locacoes/")
        assert r2.status_code == 200
        assert len(r2.json()) >= 1

        # Resumo da locação
        r3 = client_sqlite.get(f"/locacoes/{loc['id']}/resumo/")
        assert r3.status_code == 200
        resumo = r3.json()
        assert resumo["valor_total"] == 400.0
        assert resumo["saldo_pendente"] == 400.0
        assert resumo["quitada"] is False

    def test_criar_locacao_cliente_inexistente(self, client_sqlite):
        id_modelo = _criar_marca_modelo(client_sqlite, "X", "Y")
        veiculo = client_sqlite.post("/veiculos/", json={
            "placa": "V1",
            "id_modelo": id_modelo,
            "ano": 2020,
            "cor": "Azul",
            "quilometragem": 0,
            "valor_diaria": 100.0,
        }).json()
        r = client_sqlite.post("/locacoes/", json={
            "id_cliente": 99999,
            "id_veiculo": veiculo["id"],
            "dias": 3,
        })
        assert r.status_code == 404

    def test_criar_locacao_dias_invalidos(self, client_sqlite):
        id_modelo = _criar_marca_modelo(client_sqlite, "MarcaZ", "ModeloW")
        cliente = client_sqlite.post("/clientes/", json={
            "nome": "A", "cpf": "11111111111", "telefone": "11999999999",
            "email": "a@a.com", "cep": "01311100", "endereco": "Rua A",
        }).json()
        veiculo = client_sqlite.post("/veiculos/", json={
            "placa": "V2", "id_modelo": id_modelo, "ano": 2020,
            "cor": "Azul", "quilometragem": 0, "valor_diaria": 100.0,
        }).json()
        r = client_sqlite.post("/locacoes/", json={
            "id_cliente": cliente["id"],
            "id_veiculo": veiculo["id"],
            "dias": 0,
        })
        assert r.status_code == 400


class TestEstatisticasAPI:
    def test_estatisticas(self, client_sqlite):
        r = client_sqlite.get("/estatisticas/")
        assert r.status_code == 200
        data = r.json()
        assert "veiculos" in data
        assert "clientes" in data
        assert "locacoes" in data
        assert data["veiculos"]["total"] >= 0
        assert data["clientes"]["total"] >= 0
