# 1. Como subir o MariaDB/MySQL (porta 3307)

A API espera o banco em **localhost:3307**. Escolha uma opção:

## Opção A – Serviço do Windows (se MariaDB/MySQL instalado)

Abra o **PowerShell como Administrador** e tente:

```powershell
# Nomes comuns do serviço:
Start-Service MySQL
# ou
Start-Service MariaDB
# ou
Start-Service "MySQL80"
```

Para ver o nome exato do serviço:

```powershell
Get-Service | Where-Object { $_.Name -like "*mysql*" -or $_.Name -like "*mariadb*" }
```

## Opção B – Configurar MySQL 8 para usar a porta 3307 (Windows)

Se você tem **MySQL 8** rodando na porta 3306 e quer que ele escute na **3307** (para o projeto funcionar sem alterar o código):

1. **Feche** qualquer programa que use o MySQL (incluindo a API deste projeto).

2. **Abra o arquivo de configuração** no Bloco de Notas (ou outro editor). Caminho comum:
   ```
   C:\ProgramData\MySQL\MySQL Server 8.0\my.ini
   ```
   (Se não existir, procure por `my.ini` na pasta do MySQL.)

3. **Altere a porta** em dois lugares no arquivo:
   - Na seção **`[client]`**: mude `port=3306` para `port=3307`
   - Na seção **`[mysqld]`**: mude `port=3306` para `port=3307`  
   (Use Ctrl+F para achar “port=”.)

4. **Salve** o arquivo (pode ser necessário “Executar como administrador” o Bloco de Notas para salvar em ProgramData).

5. **Reinicie o serviço** — abra **PowerShell como Administrador** e execute:
   ```powershell
   Restart-Service MySQL80
   ```

6. **Teste a conexão:** na pasta do projeto:
   ```powershell
   python verificar_conexao_banco.py
   ```

**Observação:** O usuário `root` no MySQL 8 costuma ter senha. Este projeto usa **senha vazia**. Se der “Access denied”, no MySQL faça:
```sql
ALTER USER 'root'@'localhost' IDENTIFIED BY '';
FLUSH PRIVILEGES;
```
(Ou crie outro usuário com senha vazia e use-o em `database.py`.)

## Opção C – XAMPP / WAMP / Laragon

- Abra o painel e inicie **MySQL**.
- Veja em qual porta está (geralmente 3306). Se for 3306, use a alteração acima (3306 no código).

## Depois de subir o banco

1. Criar banco e tabelas: `python setup_banco.py`
2. Testar conexão: `python verificar_conexao_banco.py`
3. Subir a API: `.\iniciar_api.ps1` e acessar `http://localhost:8000/health`
