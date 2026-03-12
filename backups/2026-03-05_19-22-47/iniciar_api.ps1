# Script PowerShell para iniciar a API FastAPI
# Execute: .\iniciar_api.ps1

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

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  API FastAPI - Sistema de Locacao de Veiculos" -ForegroundColor Cyan
Write-Host "  Porta: $Port" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Verificar se requirements.txt existe
if (-not (Test-Path "requirements.txt")) {
    Write-Host "Arquivo requirements.txt nao encontrado!" -ForegroundColor Red
    Write-Host "Certifique-se de estar no diretorio correto." -ForegroundColor Red
    exit 1
}

# Instalar dependências
Write-Host "Verificando/Instalando dependencias..." -ForegroundColor Yellow
Write-Host ""

Invoke-Expression "$PythonCmd -m pip install -r requirements.txt --quiet 2>`$null"

if ($LASTEXITCODE -ne 0) {
    Write-Host "Aviso: pip install falhou (ex.: Python 3.14 precisa de Rust). Tentando iniciar mesmo assim..." -ForegroundColor Yellow
} else {
    Write-Host "Dependencias instaladas!" -ForegroundColor Green
}
Write-Host ""

# Aguardar um momento
Start-Sleep -Seconds 1

# Iniciar API
Write-Host "Iniciando servidor uvicorn..." -ForegroundColor Green
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "API rodando em: http://localhost:$Port" -ForegroundColor Green
Write-Host ""
Write-Host "Documentacao (Swagger): http://localhost:$Port/docs" -ForegroundColor Green
Write-Host "ReDoc: http://localhost:$Port/redoc" -ForegroundColor Green
Write-Host "Health Check: http://localhost:$Port/health" -ForegroundColor Green
Write-Host ""
Write-Host "Para adicionar forma de pagamento boleto (se necessario): python adicionar_boleto_api.py" -ForegroundColor Gray
Write-Host ""
Write-Host "Pressione CTRL+C para parar o servidor" -ForegroundColor Yellow
Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Iniciar servidor
Invoke-Expression "$PythonCmd -m uvicorn api:app --reload --host 127.0.0.1 --port $Port"

# Quando sair
Write-Host ""
Write-Host "Servidor parado" -ForegroundColor Yellow
