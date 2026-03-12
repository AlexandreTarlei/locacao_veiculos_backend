# Estrutura do projeto – pasta `codigos`

Esquema atualizado da pasta **codigos** (backend, frontend, scripts e banco).

---

## Visão geral da pasta `codigos`

```
codigos/
├── api.py                    # API FastAPI monolítica (raiz)
├── database.py               # Conexão SQLAlchemy (MariaDB) – usada por api.py
├── models.py                 # Modelos da API monolítica (raiz)
├── requirements.txt
│
├── # Scripts na raiz
├── iniciar_api.ps1           # Inicia API: uvicorn api:app (porta 8000)
├── adicionar_boleto_api.py   # Adiciona forma "Pagamento via boleto bancário" via API
├── verificar_conexao_banco.py # Testa conexão com o banco (sem subir a API)
├── setup_banco.py            # Cria banco locacao_veiculos e tabelas (MariaDB)
├── migrate_pagamentos.py     # Migração: adiciona formas_pagamento e pagamentos
├── adicionar_coluna_fotos.py # Migração: coluna fotos em veículos
│
├── locacao_veiculos.py       # Aplicação CLI (locação de veículos)
├── locacao_veiculos.html     # Frontend estático (alternativo)
├── financeiro.html           # Página financeiro (raiz)
│
├── backend/                  # API modular (FastAPI + routers)
├── frontend/                 # Páginas HTML do sistema
│
└── # Documentação
    ├── README_estrutura.md   # Este arquivo (esquema do projeto)
    ├── COMO_SUBIR_MARIADB.md # Como subir MariaDB/MySQL (porta 3307)
    └── (outros .md conforme o projeto)
```

---

## Scripts na raiz (`/codigos`)

| Arquivo | Descrição |
|---------|-----------|
| `iniciar_api.ps1` | Inicia a API FastAPI: `uvicorn api:app --reload` (porta 8000). Execute na pasta codigos. |
| `api.py` | API FastAPI monolítica; seed de formas de pagamento; endpoint `/health` testa conexão com o banco. |
| `database.py` | URL: `mysql+pymysql://root:@localhost:3307/locacao_veiculos`. Engine, SessionLocal, `get_db`. |
| `models.py` | Modelos da API na raiz (quando se usa `api:app`). |
| `adicionar_boleto_api.py` | Adiciona a forma "Pagamento via boleto bancário" via POST. **API deve estar rodando.** |
| `verificar_conexao_banco.py` | Testa conexão com o banco (SELECT 1). Execute: `python verificar_conexao_banco.py`. |
| `reorganizar_ids_formas_pagamento.py` | Reorganiza os IDs da tabela `formas_pagamento` para sequenciais (1, 2, 3, …). Atualiza `pagamentos`. Execute com o banco acessível. |
| `setup_banco.py` | Cria o banco `locacao_veiculos`, tabelas e views. MariaDB em localhost:3307. |
| `migrate_pagamentos.py` | Adiciona tabelas `formas_pagamento` e `pagamentos` em banco existente. |
| `adicionar_coluna_fotos.py` | Adiciona coluna de fotos em veículos (conforme necessidade do projeto). |
| `locacao_veiculos.py` | Aplicação em linha de comando para locação de veículos. |

---

## Backend (`/backend`)

API modular: rode com `cd backend` e `uvicorn main:app --reload`. Base: **http://localhost:8000**.

| Arquivo | Descrição |
|---------|-----------|
| `main.py` | App FastAPI, CORS, seed formas de pagamento e usuários, inclusão dos routers. |
| `database.py` | Conexão SQLAlchemy (MariaDB, mesma URL que na raiz), `get_db`, `engine`. |
| `models.py` | Modelos: Usuario, Veiculo, Cliente, FormaPagamento, Locacao, Pagamento, PlanoConta, LancamentoFinanceiro. |
| `auth.py` | Autenticação (login, JWT); router de auth. |
| `locacoes.py` | Rotas: `/veiculos/`, `/formas-pagamento/`, `/locacoes/`, pagamentos e resumo. |
| `clientes.py` | Rotas: `/clientes/` (CRUD). |
| `financeiro.py` | Rotas: `/plano-contas/`, `/financeiro` (lançamentos). |
| `relatorios.py` | Rotas: `/`, `/health` (com checagem de banco), `/estatisticas/`, PDFs. |
| `pdf_utils.py` | Geração de PDF (relatórios). |
| `migrations/add_data_vencimento_pagamento.sql` | Migração SQL (data vencimento/pagamento). |

---

## Frontend (`/frontend`)

Páginas HTML que consomem a API (configurar `API_BASE` para `http://localhost:8000`).

| Arquivo | Descrição |
|---------|-----------|
| `dashboard.html` | Resumo e estatísticas. |
| `dashboard-financeiro.html` | Dashboard do módulo financeiro. |
| `financeiro.html` | Controle financeiro: lançamentos, plano de contas, formas de pagamento. |
| `locacoes.html` | Listagem e gestão de locações. |
| `clientes.html` | Listagem e gestão de clientes. |
| `relatorios.html` | Relatórios. |
| `login.html` | Tela de login (quando usar backend com auth). |

Servir localmente, por exemplo: `cd frontend` e `python -m http.server 5500` → **http://localhost:5500/dashboard.html**.

---

## Esquema do banco de dados (`locacao_veiculos`)

Conexão: **localhost:3307**, usuário **root**, banco **locacao_veiculos**.

| Tabela | Descrição |
|--------|-----------|
| `usuarios` | Usuários do sistema (backend com auth). |
| `veiculos` | Veículos (placa, marca, modelo, ano, cor, valor_diaria, fotos_json, etc.). |
| `clientes` | Clientes (nome, cpf, telefone, email, cep, endereco, data_nascimento). |
| `formas_pagamento` | Formas de pagamento (nome, descricao, ativa). Seed com PIX, boleto, cartão, etc. |
| `locacoes` | Locações (cliente, veículo, datas, valor_total, multa_atraso, ativa). |
| `pagamentos` | Pagamentos de locações (locação, forma de pagamento, valor, data). |
| `plano_contas` | Plano de contas (módulo financeiro). |
| `lancamentos_financeiros` | Lançamentos financeiros (descrição, valor, datas, tipo, plano_conta, forma_pagamento, pago). |

Views (criadas pelo `setup_banco.py`): `vw_locacoes_ativas`, `vw_historico_locacoes`, `vw_pagamentos_locacoes`.

---

## Verificação de conexão e saúde

- **Sem API:** `python verificar_conexao_banco.py` (na pasta codigos).
- **Com API rodando:** GET **http://localhost:8000/health** → retorna `"database": "conectado"` ou `"erro"` com detalhe.

Se o banco não sobe ou a conexão falha, veja **COMO_SUBIR_MARIADB.md**.

---

## Formas de pagamento e boleto

O seed (api.py e backend/main.py) já inclui **"Pagamento via boleto bancário"**. Se faltar em algum ambiente, com a API rodando:

```bash
python adicionar_boleto_api.py
```

---

## Resumo rápido

| O quê | Comando / Onde |
|-------|-----------------|
| Subir API (raiz) | `.\iniciar_api.ps1` ou `uvicorn api:app --reload` |
| Subir API (backend) | `cd backend` → `uvicorn main:app --reload` |
| Criar banco e tabelas | `python setup_banco.py` |
| Testar conexão | `python verificar_conexao_banco.py` |
| Documentação da API | http://localhost:8000/docs |
| Health (e banco) | http://localhost:8000/health |
