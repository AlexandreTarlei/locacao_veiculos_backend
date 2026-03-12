# Conexão: Banco de Dados, API e Frontend

## Esquema

```
MySQL/MariaDB (porta 3307)  <--->  API FastAPI (porta 8000)  <--->  Frontend (navegador)
     locacao_veiculos               api.py + database.py              locacao_veiculos.html
     (tabelas: veiculos,            Serve / e /locacao_veiculos.html   Abre em http://127.0.0.1:8000/
      clientes, locacoes, ...)      Endpoints: /health, /veiculos/,     Chama API (mesma origem)
                                    /clientes/, /locacoes/, etc.
```

## Como subir e abrir o frontend

1. **Banco**: Inicie o MySQL/MariaDB (ex.: XAMPP, porta 3307). Banco: `locacao_veiculos`.

2. **Liberar a porta 8000** (se aparecer "porta já em uso"): feche outras janelas do PowerShell que estejam rodando a API, ou no PowerShell:
   ```powershell
   netstat -ano | findstr :8000
   taskkill /PID <numero_do_PID> /F
   ```

3. **API**: No PowerShell, na pasta do projeto:
   ```powershell
   cd C:\Users\Usuario\Desktop\codigos
   .\iniciar_api_simples.ps1
   ```
   Se a porta 8000 estiver em uso: `.\iniciar_api.ps1 -Port 8001` e abra depois **http://127.0.0.1:8001/**.

4. **Frontend**: No navegador, abra (use a mesma porta em que a API subiu):
   - **http://127.0.0.1:8000/**  
   ou  
   - **http://127.0.0.1:8000/locacao_veiculos.html**

Não abra o arquivo `.html` pelo disco (file://). Só funciona quando a página é servida pela API (mesma origem).

## Verificar conexões

- **API no ar**: http://127.0.0.1:8000/health  
  - Resposta com `"database": "conectado"` = banco OK.  
  - `"database": "erro"` = conferir MySQL (porta 3307, usuário/senha, banco `locacao_veiculos`).
- **Documentação da API**: http://127.0.0.1:8000/docs

## Configuração do banco (porta 3307)

- `database.py` usa por padrão a porta **3307** (e variáveis de ambiente MYSQL_*).
- Para outra porta ou host: crie um arquivo `.env` na pasta do projeto com, por exemplo:
  `MYSQL_PORT=3306` e `MYSQL_HOST=localhost`.
