# 🎯 GUIA RÁPIDO: API FastAPI de Locação de Veículos

## 🚀 Começar em 3 Passos

### 1️⃣ Instalar Dependências
Abra o terminal no VS Code e execute:
```bash
pip install -r requirements.txt
```

### 2️⃣ Iniciar a API
Escolha uma das opções:

**Opção A: Python (Recomendado)**
```bash
python iniciar_api.py
```

**Opção B: PowerShell (Windows)**
```powershell
.\iniciar_api.ps1
```

**Opção C: Uvicorn Direto**
```bash
uvicorn api:app --reload
```

### 3️⃣ Acessar a API
Abra no navegador:
- 📚 **Documentação**: http://localhost:8000/docs
- 📄 **Alternativa**: http://localhost:8000/redoc
- ❤️ **Health Check**: http://localhost:8000/health

---

## 📋 O que foi criado?

| Arquivo | Descrição |
|---------|-----------|
| `api.py` | 🔧 Endpoints e lógica da API |
| `database.py` | 🗄️ Configuração SQLAlchemy + MariaDB |
| `models.py` | 📊 Modelos de dados (Veículo, Cliente, etc) |
| `requirements.txt` | 📦 Dependências Python |
| `iniciar_api.py` | ▶️ Script Python para iniciar |
| `iniciar_api.ps1` | ▶️ Script PowerShell para iniciar |
| `EXEMPLOS_HTTP.md` | 💡 Exemplos de como usar cada endpoint |
| `API_FASTAPI.md` | 📖 Documentação completa |

---

## 🔌 Endpoints Principais

### Veículos
- ✅ `POST` /veiculos/ - Criar
- 📋 `GET` /veiculos/ - Listar
- 🔍 `GET` /veiculos/{id} - Obter
- ✏️ `PUT` /veiculos/{id} - Atualizar
- ❌ `DELETE` /veiculos/{id} - Deletar

### Clientes
- ✅ `POST` /clientes/ - Criar
- 📋 `GET` /clientes/ - Listar
- 🔍 `GET` /clientes/{id} - Obter
- ✏️ `PUT` /clientes/{id} - Atualizar
- ❌ `DELETE` /clientes/{id} - Deletar

### Locações
- ✅ `POST` /locacoes/ - Criar
- 📋 `GET` /locacoes/ - Listar
- 🔍 `GET` /locacoes/{id} - Obter detalhes
- 📊 `GET` /locacoes/{id}/resumo/ - Ver saldo
- ⏹️ `POST` /locacoes/{id}/finalizar - Finalizar

### Pagamentos
- ✅ `POST` /locacoes/{id}/pagamentos/ - Registrar
- 📋 `GET` /locacoes/{id}/pagamentos/ - Listar

### Formas de Pagamento
- ✅ `POST` /formas-pagamento/ - Criar
- 📋 `GET` /formas-pagamento/ - Listar

### Estatísticas
- 📊 `GET` /estatisticas/ - Ver dados do sistema

---

## 🧪 Teste Rápido (em outro terminal)

Depois de iniciar a API, execute:

```bash
# Health Check
curl http://localhost:8000/health

# Obter estatísticas
curl http://localhost:8000/estatisticas/

# Listar veículos
curl http://localhost:8000/veiculos/
```

---

## ⚙️ Configuração do Banco de Dados

**Verificar conexão com MariaDB:**
```bash
mysql -u root -h localhost -P 3307
```

**Credenciais padrão em `database.py`:**
- Host: localhost
- Port: 3307
- User: root
- Password: (vazio)
- Database: locacao_veiculos

**Se precisar mudar:**
Edite `database.py` linha 7:
```python
DATABASE_URL = "mysql+pymysql://usuario:senha@localhost:3307/banco"
```

---

## 🎓 Próximos Passos

1. **Testar endpoints** no Swagger: http://localhost:8000/docs
2. **Ler documentação** completa em [API_FASTAPI.md](API_FASTAPI.md)
3. **Ver exemplos** em [EXEMPLOS_HTTP.md](EXEMPLOS_HTTP.md)
4. **Usar Postman** para testes mais avançados
5. **Modificar** conforme necessidade do projeto

---

## ❓ Dúvidas Frequentes

**P: Preciso matar a API? Como?**
R: Pressione `CTRL+C` no terminal

**P: A porta 8000 está em uso, como mudar?**
R: Edite o comando:
```bash
uvicorn api:app --reload --port 8001
```

**P: Como adicionar mais funcionalidades?**
R: Edite `api.py` e adicione novos endpoints

**P: Posso usar essa API com aplicativos frontend?**
R: Sim! CORS já está configurado para aceitar requisições de qualquer origem

**P: Como fazer backup dos dados?**
R: Use ferramentas MariaDB ou faça SQL dump

---

## 📚 Recursos

- 📖 [FastAPI Documentation](https://fastapi.tiangolo.com/)
- 🗄️ [SQLAlchemy ORM](https://docs.sqlalchemy.org/en/20/)
- 🐍 [Python 3.11+](https://www.python.org/)
- 🗄️ [MariaDB](https://mariadb.org/)
- 🧪 [Swagger/OpenAPI](https://swagger.io/)

---

## 💡 Dicas Úteis

✅ Use `http://localhost:8000/docs` para explorar melhor os endpoints
✅ A API recarrega automaticamente com `--reload`
✅ Todos os erros estão bem documentados nas respostas
✅ Consulte EXEMPLOS_HTTP.md para caso de uso real

---

**Pronto! Sua API está funcionando! 🎉**
