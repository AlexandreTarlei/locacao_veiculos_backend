# Inicia a API SEM reload (um unico processo - use se iniciar_api.ps1 falhar)
# Execute: .\iniciar_api_simples.ps1
$Port = "8000"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir
Write-Host "API em http://127.0.0.1:$Port - Frontend: http://127.0.0.1:$Port/locacao_veiculos.html" -ForegroundColor Cyan
& python -m uvicorn api:app --host 127.0.0.1 --port $Port
