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

## Opção B – Porta 3307 no MariaDB

Se o MariaDB estiver instalado mas na porta padrão **3306**, você pode:

- **Mudar a configuração** do MariaDB para escutar também na 3307, ou  
- **Alterar o projeto** para usar 3306: em `database.py` e em `setup_banco.py` / `migrate_pagamentos.py` troque `3307` por `3306`.

## Opção C – XAMPP / WAMP / Laragon

- Abra o painel e inicie **MySQL**.
- Veja em qual porta está (geralmente 3306). Se for 3306, use a alteração acima (3306 no código).

## Depois de subir o banco

1. Criar banco e tabelas: `python setup_banco.py`
2. Testar conexão: `python verificar_conexao_banco.py`
3. Subir a API: `.\iniciar_api.ps1` e acessar `http://localhost:8000/health`
