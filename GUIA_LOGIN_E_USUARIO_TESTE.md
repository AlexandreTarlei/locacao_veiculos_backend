# Guia: Login e usuário de teste

## Onde está o login

### API (backend)
- **Arquivo:** [backend/auth/login.py](backend/auth/login.py)
- **Rota:** `POST /auth/login`
- **Corpo (JSON):** `{ "email": "seu@email.com", "password": "sua_senha" }`
- **Resposta:** `{ "access_token": "...", "token_type": "bearer", "usuario": { "id", "nome", "email", "nivel", "tipo_nome" } }`
- As senhas são armazenadas com **bcrypt** (não SHA256); verificação em [backend/auth/jwt_auth.py](backend/auth/jwt_auth.py) (`verificar_senha`).

### Frontend (tela de login)
- **Arquivo:** [frontend/login.html](frontend/login.html)
- **URL:** servida em **http://localhost:8000/app/login.html** quando você sobe a **API do backend** (não a API da raiz).

---

## Qual API usar

O projeto tem duas entradas:

| Entrada | Pasta | Comando | Uso |
|--------|--------|--------|-----|
| **API raiz** (locação) | `codigos` | `.\iniciar_api_simples.ps1` ou `uvicorn api:app --port 8000` | Frontend `locacao_veiculos.html` em http://127.0.0.1:8000/ — **sem login**. |
| **API backend** (com auth) | `codigos\backend` | `uvicorn app:app --host 0.0.0.0 --port 8000` | Login em `/auth/login`, frontend em `/app/login.html` e `/app/dashboard.html`. |

Para usar **login e usuários**, é preciso subir a **API do backend** (segunda linha).

---

## Como subir a API com login

1. Abra o PowerShell e vá para a pasta **backend**:
   ```powershell
   cd C:\Users\Usuario\Desktop\codigos\backend
   ```
2. Suba a API (MySQL na porta 3307 e banco `locacao_veiculos` devem estar ativos):
   ```powershell
   python -m uvicorn app:app --host 127.0.0.1 --port 8000
   ```
   Se a porta 8000 já estiver em uso, use outra (ex.: 8002):
   ```powershell
   python -m uvicorn app:app --host 127.0.0.1 --port 8002
   ```
   Nesse caso, abra **http://127.0.0.1:8002/app/login.html** (e ajuste a variável `API_BASE` em `frontend/login.html` se necessário).

3. Abra no navegador:
   - **http://127.0.0.1:8000/app/login.html** (ou 8002 se usou outra porta).

---

## Usuário de teste

Quando a API do backend sobe, o `seed_usuarios()` em [backend/app.py](backend/app.py) cria um usuário **se a tabela `usuarios` estiver vazia**:

- **E-mail:** `admin@admin.com`
- **Senha:** `admin`

Use esses dados na tela de login.

**Observação:** O seed só roda se existirem as tabelas `tipo_usuario` e `usuarios` (e se `usuarios` estiver vazia). Se você usa só a API da raiz (`api.py`), essas tabelas podem não existir; nesse caso, suba uma vez a API do backend para criar tabelas e o usuário admin.

---

## Criar outro usuário de teste (pelo banco)

Se a API do backend estiver no ar e você tiver um usuário admin logado, pode criar usuários pela API:

- **POST /usuarios** (com header `Authorization: Bearer <token>`), corpo por exemplo:
  ```json
  { "nome": "Teste", "email": "teste@teste.com", "senha": "teste123" }
  ```
  A senha será armazenada em bcrypt pela API.

Para criar direto no MySQL (senha em bcrypt), use um hash bcrypt gerado por um script ou pela própria API (ex.: fazer um POST em /usuarios com uma senha e depois consultar o valor gravado em `usuarios.senha` para reutilizar em outro insert, ou usar um gerador bcrypt online e inserir na tabela `usuarios`).

---

## Resumo

- **Rota de login:** `POST /auth/login` (em [backend/auth/login.py](backend/auth/login.py)).
- **Tela de login:** [frontend/login.html](frontend/login.html), acessada em **http://127.0.0.1:8000/app/login.html** com a API do backend rodando.
- **Usuário de teste:** `admin@admin.com` / `admin`, criado automaticamente pelo seed ao subir a API do backend (se a tabela `usuarios` estiver vazia).
