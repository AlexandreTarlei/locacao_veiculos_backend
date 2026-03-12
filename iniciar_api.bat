@echo off
cd /d "%~dp0"
echo Iniciando API - Sistema de Locacao de Veiculos
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0iniciar_api.ps1" %*
pause
