# Cria atalhos na Area de Trabalho para o Frontend e para a API (se nao existirem)
# Execute: .\criar_atalhos_desktop.ps1

$projetoDir = $PSScriptRoot
$desktop = [Environment]::GetFolderPath("Desktop")

$frontendHtml = Join-Path $projetoDir "locacao_veiculos.html"
$atalhoFrontend = Join-Path $desktop "Locacao Veiculos - Frontend.lnk"
$atalhoApi = Join-Path $desktop "Locacao Veiculos - Iniciar API.lnk"

$WshShell = New-Object -ComObject WScript.Shell

# 1) Atalho do Frontend (abrir no navegador)
if (-not (Test-Path $atalhoFrontend)) {
    $shortcut = $WshShell.CreateShortcut($atalhoFrontend)
    $shortcut.TargetPath = $frontendHtml
    $shortcut.WorkingDirectory = $projetoDir
    $shortcut.Description = "Abrir sistema de locacao de veiculos (frontend)"
    $shortcut.Save()
    Write-Host "Atalho criado: Locacao Veiculos - Frontend" -ForegroundColor Green
} else {
    Write-Host "Atalho ja existe: Locacao Veiculos - Frontend" -ForegroundColor Gray
}

# 2) Atalho do Backup (executar backup do banco, API e frontend)
$atalhoBackup = Join-Path $desktop "Locacao Veiculos - Backup.lnk"
if (-not (Test-Path $atalhoBackup)) {
    $shortcut = $WshShell.CreateShortcut($atalhoBackup)
    $shortcut.TargetPath = "powershell.exe"
    $shortcut.Arguments = "-ExecutionPolicy Bypass -File `"$projetoDir\backup_projeto.ps1`""
    $shortcut.WorkingDirectory = $projetoDir
    $shortcut.Description = "Fazer backup do banco, API e frontend (execute apos atualizacoes)"
    $shortcut.Save()
    Write-Host "Atalho criado: Locacao Veiculos - Backup" -ForegroundColor Green
} else {
    Write-Host "Atalho ja existe: Locacao Veiculos - Backup" -ForegroundColor Gray
}

# 3) Atalho da API (abrir PowerShell e executar iniciar_api.ps1)
if (-not (Test-Path $atalhoApi)) {
    $shortcut = $WshShell.CreateShortcut($atalhoApi)
    $shortcut.TargetPath = "powershell.exe"
    $shortcut.Arguments = "-NoExit -ExecutionPolicy Bypass -File `"$projetoDir\iniciar_api.ps1`""
    $shortcut.WorkingDirectory = $projetoDir
    $shortcut.Description = "Iniciar a API FastAPI do sistema de locacao de veiculos"
    $shortcut.Save()
    Write-Host "Atalho criado: Locacao Veiculos - Iniciar API" -ForegroundColor Green
} else {
    Write-Host "Atalho ja existe: Locacao Veiculos - Iniciar API" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Dica: use o atalho 'Locacao Veiculos - Backup' apos cada atualizacao para manter tudo salvo em codigos\backups\" -ForegroundColor Yellow
Write-Host ""
Write-Host "Atalhos na Area de Trabalho:" -ForegroundColor Cyan
Write-Host "  $desktop" -ForegroundColor Gray
