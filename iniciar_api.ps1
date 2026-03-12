# Script PowerShell para iniciar a API FastAPI - Sistema de Locacao de Veiculos
# Execute: .\iniciar_api.ps1
# Ou de duplo clique em iniciar_api.bat

param(
    [string]$Port = "8000",
    [switch]$Help
)

# Preferir Python 3.12 ou 3.11 (evita erro com Pydantic no 3.14)
$PythonCmd = "python"
if (Get-Command py -ErrorAction SilentlyContinue) {
    foreach ($v in @("3.12", "3.11") ) {
        $null = & py -$v -c "exit(0)" 2>$null
        if ($LASTEXITCODE -eq 0) { $PythonCmd = "py -$v"; break }
    }
}

if ($Help) {
    Write-Host "Uso: .\iniciar_api.ps1 [-Port 8000] [-Help]" -ForegroundColor Green
    Write-Host ""
    Write-Host "Opcoes:" -ForegroundColor Yellow
    Write-Host "  -Port   : Porta (padrao: 8000)" -ForegroundColor Yellow
    Write-Host "  -Help   : Mostra esta mensagem" -ForegroundColor Yellow
    exit 0
}

# Garantir que estamos na pasta do script
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  API FastAPI - Sistema de Locacao de Veiculos" -ForegroundColor Cyan
Write-Host "  Pasta: $ScriptDir" -ForegroundColor Gray
Write-Host "  Porta: $Port" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se requirements.txt existe
if (-not (Test-Path "requirements.txt")) {
    Write-Host "Arquivo requirements.txt nao encontrado!" -ForegroundColor Red
    Write-Host "Certifique-se de estar no diretorio: $ScriptDir" -ForegroundColor Red
    exit 1
}

# Instalar/atualizar dependencias
Write-Host "Verificando dependencias (pip install -r requirements.txt)..." -ForegroundColor Yellow
& $PythonCmd -m pip install -r requirements.txt --quiet 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Aviso: pip install falhou. Tentando iniciar mesmo assim..." -ForegroundColor Yellow
} else {
    Write-Host "Dependencias OK." -ForegroundColor Green
}
Write-Host ""

Write-Host "Iniciando servidor uvicorn..." -ForegroundColor Green
Write-Host ""
Write-Host "  API        : http://127.0.0.1:$Port" -ForegroundColor Green
Write-Host "  Frontend   : http://127.0.0.1:$Port/locacao_veiculos.html" -ForegroundColor Green
Write-Host "  Swagger    : http://127.0.0.1:$Port/docs" -ForegroundColor Green
Write-Host ""
Write-Host "  IMPORTANTE: Abra o frontend por ESTE link (nao abra o arquivo .html pelo disco):" -ForegroundColor Yellow
Write-Host "  http://127.0.0.1:$Port/locacao_veiculos.html" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Pressione CTRL+C para parar o servidor." -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

& $PythonCmd -m uvicorn api:app --reload --host 127.0.0.1 --port $Port

Write-Host ""
Write-Host "Servidor parado." -ForegroundColor Yellow
