# Como usar o sistema de locação de veículos

## Visão geral

- **locacao_veiculos.py** – Aplicativo de console (CLI) que usa o banco diretamente (módulo `conexao_bd.py`).
- **api.py** – API FastAPI que usa o mesmo banco (SQLAlchemy em `database.py`).
- **locacao_veiculos.html** – Interface web que consome a API em `http://127.0.0.1:8000`.

Todos compartilham o mesmo banco **locacao_veiculos** (MySQL/MariaDB).

---

## 1. Banco de dados

- Tenha MySQL ou MariaDB rodando (ex.: `localhost:3306`).
- Crie o banco e as tabelas de uma destas formas:
  - **Opção A:** A API cria as tabelas na primeira execução (`Base.metadata.create_all`).
  - **Opção B:** Execute `python setup_banco.py` (se existir na pasta) para criar o banco e tabelas manualmente.

Variáveis de ambiente (opcional): `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE`.

---

## 2. Usar a interface web (HTML + API)

1. **Iniciar a API** (na pasta do projeto, ex.: `Desktop\codigos`):
   ```powershell
   .\iniciar_api.ps1
   ```
   Ou manualmente:
   ```powershell
   python -m uvicorn api:app --reload --host 127.0.0.1 --port 8000
   ```

2. **Abrir o HTML no navegador:**
   - Abra o arquivo: `file:///C:/Users/Usuario/Desktop/codigos/locacao_veiculos.html`
   - Ou sirva a pasta e acesse pelo navegador:
     ```powershell
     python -m http.server 8080
     ```
     Depois acesse: `http://localhost:8080/locacao_veiculos.html`

O HTML usa a API em **http://127.0.0.1:8000**. O indicador “Backend conectado” confirma que a API está acessível.

---

## 3. Usar o aplicativo de console (locacao_veiculos.py)

1. Instale dependências (inclui `mysql-connector-python`):
   ```powershell
   pip install -r requirements.txt
   ```

2. Execute:
   ```powershell
   python locacao_veiculos.py
   ```

O script usa o módulo **conexao_bd.py** para conectar ao mesmo banco que a API. Dados cadastrados pelo console ou pela API aparecem nos dois.

---

## Resumo rápido

| O que fazer        | Comando / Ação |
|--------------------|----------------|
| Subir a API        | `.\iniciar_api.ps1` ou `uvicorn api:app --reload --host 127.0.0.1 --port 8000` |
| Abrir o sistema web| Abrir `locacao_veiculos.html` (file:// ou via `python -m http.server 8080`) |
| Usar o console     | `python locacao_veiculos.py` |

Documentação da API: **http://127.0.0.1:8000/docs** (com a API rodando).
