# 🆘 Troubleshooting - Resolvendo Problemas

## ❌ Erro: ModuleNotFoundError: No module named 'fastapi'

**Causa**: Dependências não instaladas

**Solução**:
```bash
pip install -r requirements.txt
```

Ou instale manualmente:
```bash
pip install fastapi uvicorn sqlalchemy pymysql
```

---

## ❌ Erro: Connection refused (MariaDB)

**Causa**: MariaDB não está rodando ou credenciais erradas

**Solução**:

1. Verificar se MariaDB está rodando:
```bash
mysql -u root -h localhost -P 3307
```

2. Se não conectar, inicie MariaDB:
   - Windows: procure "MariaDB" no Iniciar e execute
   - Linux: `sudo service mariadb start`
   - Mac: `brew services start mariadb`

3. Verificar credenciais em `database.py`:
```python
DATABASE_URL = "mysql+pymysql://root:@localhost:3307/locacao_veiculos"
#                             ↑    ↑                ↑              ↑
#                           user  pass             host            db
```

---

## ❌ Erro: Port 8000 is already in use

**Causa**: Outra aplicação já está usando porta 8000

**Solução 1**: Usar outra porta
```bash
uvicorn api:app --reload --port 8001
```

**Solução 2**: Matar processo que usa porta 8000

Windows (PowerShell Admin):
```powershell
Get-Process | Where-Object {$_.Port -eq 8000}
Kill-Process -Name "processo_name"
```

Windows (CMD):
```cmd
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

Linux/Mac:
```bash
lsof -i :8000
kill -9 <PID>
```

---

## ❌ Erro: 'cannot import name database'

**Causa**: O arquivo `database.py` está em outro diretório

**Solução**:
1. Certifique-se que `database.py` está no mesmo diretório que `api.py`
2. Se estiver em subpasta, importe corretamente:
```python
from subpasta.database import Base, SessionLocal
```

---

## ❌ Erro: SQLAlchemy - (pymysql.err.OperationalError)

**Causa**: Erro na conexão com MariaDB

**Solução**:
1. Verifique `database.py` - URL de conexão
2. Verifique credenciais (user, password, host, port)
3. Verifique que MariaDB está rodando
4. Verifique que banco de dados existe:
```sql
SHOW DATABASES;
```

---

## ❌ Erro ao executar iniciar_api.ps1 (PowerShell)

**Causa**: Política de execução do PowerShell

**Solução**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Ou execute como admin e tente novamente.

---

## ❌ API inicia mas não conecta ao banco

**Causa**: Provável that the database doesn't exist

**Solução**:
1. Crie o banco manualmente:
```sql
CREATE DATABASE locacao_veiculos;
USE locacao_veiculos;
```

2. Ou rode o script de setup:
```bash
python setup_banco.py
```

3. API criará as tabelas automaticamente ao iniciar

---

## ❌ Erro: "relation 'veiculos' does not exist"

**Causa**: Tabelas não foram criadas

**Solução**:
1. Deletar banco:
```sql
DROP DATABASE locacao_veiculos;
```

2. Recriar:
```sql
CREATE DATABASE locacao_veiculos;
```

3. Reiniciar API:
```bash
python iniciar_api.py
```

---

## ❌ Erro: 404 Not Found em todos endpoints

**Causa**: API não iniciou corretamente ou arquivo está errado

**Solução**:
1. Verifique barra de erro no terminal
2. Certifique-se que `api.py` está no diretório correto
3. Tente: `python -m uvicorn api:app --reload`
4. Verifique se http://localhost:8000/ retorna algo

---

## ❌ Erro: "client did not request chunked encoding"

**Causa**: Problema com Python/Uvicorn versão

**Solução**:
```bash
pip install --upgrade uvicorn
```

---

## ✅ API iniciou mas Swagger não abre

**Solução**:
1. A API iniciou normalmente (procure por "Uvicorn running")
2. Abra manualmente: http://localhost:8000/docs
3. Se não abrir, tente: http://127.0.0.1:8000/docs

---

## ❌ Erro: "json.decoder.JSONDecodeError"

**Causa**: Requisição POST com JSON inválido

**Solução**:
1. Verifique que Content-Type está correto:
```
Content-Type: application/json
```

2. Valide o JSON (use http://jsonlint.com)

3. Exemplo correto:
```json
{
  "placa": "ABC-1234",
  "marca": "Toyota"
}
```

---

## ❌ Erro ao deletar recurso: "has foreign key references"

**Causa**: O recurso tem relacionamentos (e.g., veículo em uma locação)

**Solução**:
1. Não é possível deletar se tiver dependências
2. Exemplo: não pode deletar cliente com locações ativas
3. Solução: Finalize ou mude as locações primeiro

---

## ❌ Erro: "ValueError: invalid literal for int()"

**Causa**: ID passado não é um número inteiro

**Solução**:
- Verifique que IDs são números: `/veiculos/1` (correto)
- Não: `/veiculos/abc` (errado)

---

## ✅ "Funcionou! Como agora?"

### Parar a API:
Pressione `CTRL+C` no terminal

### Reiniciar a API:
```bash
python iniciar_api.py
```

### Resetar banco de dados:
```sql
DROP DATABASE locacao_veiculos;
CREATE DATABASE locacao_veiculos;
```
Então reinicie a API.

### Backup dos dados:
```bash
mysqldump -u root -h localhost -P 3307 locacao_veiculos > backup.sql
```

---

## 🆘 Ainda tem problemas?

1. **Leia**: [API_FASTAPI.md](API_FASTAPI.md)
2. **Consulte**: [EXEMPLOS_HTTP.md](EXEMPLOS_HTTP.md)
3. **Visite**: https://fastapi.tiangolo.com/
4. **Pesquise**: Stack Overflow com a mensagem de erro

---

## ✅ Checklist de Áreas Para Verificar

- [ ] Python está instalado? `python --version`
- [ ] Dependências instaladas? `pip list | grep fastapi`
- [ ] MariaDB rodando? `mysql -u root -h localhost -P 3307`
- [ ] Arquivo `api.py` existe? `ls api.py`
- [ ] Arquivo `database.py` existe? `ls database.py`
- [ ] Arquivo `models.py` existe? `ls models.py`
- [ ] Credenciais corretas em `database.py`?
- [ ] Porta 8000 livre?
- [ ] Terminal mostra "Uvicorn running"?
- [ ] http://localhost:8000 responde?

---

## 💡 Dicas

- Sempre verifique o **terminal** para mensagens de erro
- Use **CTRL+C** para parar em qualquer momento
- Documentação interativa em `/docs` é sua melhor amiga
- Erros JSON aparecem em vermelho - leia com atenção
- Teste endpoints em Swagger antes de usar em código

---

**OK, agora está tudo sobre controle! 💪**
