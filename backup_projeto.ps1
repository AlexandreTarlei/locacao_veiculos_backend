# Backup do projeto: banco de dados, API e frontend
# Execute: .\backup_projeto.ps1
# Use apos atualizacoes para manter tudo salvo.

$ErrorActionPreference = "Stop"
$projetoDir = $PSScriptRoot
$backupBase = Join-Path $projetoDir "backups"
$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$backupDir = Join-Path $backupBase $timestamp

if (-not (Test-Path $backupBase)) { New-Item -ItemType Directory -Path $backupBase -Force | Out-Null }
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null

Write-Host "Backup em: $backupDir" -ForegroundColor Cyan

# 1) Backup do banco de dados (mysqldump)
$mysqldump = $null
foreach ($p in @("mysqldump", "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump.exe", "C:\Program Files\MariaDB 10.*\bin\mysqldump.exe")) {
    if ($p -like "*\*") {
        if (Test-Path $p) { $mysqldump = $p; break }
        $dirs = Get-ChildItem -Path "C:\Program Files" -Filter "MariaDB*" -Directory -ErrorAction SilentlyContinue
        foreach ($d in $dirs) {
            $exe = Join-Path $d.FullName "bin\mysqldump.exe"
            if (Test-Path $exe) { $mysqldump = $exe; break }
        }
        if ($mysqldump) { break }
    } else {
        $exe = Get-Command $p -ErrorAction SilentlyContinue
        if ($exe) { $mysqldump = $exe.Source; break }
    }
}
if ($mysqldump) {
    $sqlFile = Join-Path $backupDir "locacao_veiculos.sql"
    try {
        $params = @("-h", "localhost", "-P", "3306", "-u", "root", "locacao_veiculos")
        & $mysqldump @params 2>$null | Out-File -FilePath $sqlFile -Encoding utf8
        if (Test-Path $sqlFile -and (Get-Item $sqlFile).Length -gt 0) { Write-Host "  Banco: locacao_veiculos.sql" -ForegroundColor Green }
        else { Write-Host "  Banco: mysqldump nao retornou dados (verifique se o MySQL esta rodando na porta 3306)" -ForegroundColor Yellow }
    } catch { Write-Host "  Banco: mysqldump falhou (servico pode estar parado)" -ForegroundColor Yellow }
} else {
    Write-Host "  Banco: mysqldump nao encontrado (copie o backup manualmente se precisar)" -ForegroundColor Yellow
}

# 2) Copiar arquivos da API e frontend
$arquivos = @(
    "api.py",
    "database.py",
    "models.py",
    "requirements.txt",
    "locacao_veiculos.html",
    "setup_banco.py",
    "verificar_conexao_banco.py",
    "iniciar_api.ps1",
    "COMO_SUBIR_MARIADB.md"
)
foreach ($f in $arquivos) {
    $origem = Join-Path $projetoDir $f
    if (Test-Path $origem) {
        Copy-Item -Path $origem -Destination $backupDir -Force
        Write-Host "  Copiado: $f" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "Backup concluido: $backupDir" -ForegroundColor Green
