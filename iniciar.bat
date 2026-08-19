@echo off
chcp 65001 >nul 2>&1
title AudioClasifica - Servidor
color 0A

:: Ir a la carpeta del script (funciona desde cualquier ubicacion)
cd /d "%~dp0"

echo.
echo =======================================================
echo   AudioClasifica - Iniciando...
echo =======================================================
echo.

:: Verificar que el venv exista
if not exist "venv\Scripts\python.exe" (
    echo [!] No se encontro el entorno virtual.
    echo     Ejecuta primero "instalar_y_ejecutar.bat"
    echo.
    pause
    exit /b 1
)

echo [OK] Entorno virtual encontrado.

:: Abrir navegador automaticamente
start http://localhost:5000

echo.
echo =======================================================
echo   Servidor corriendo en: http://localhost:5000
echo   Para detener presiona Ctrl+C
echo =======================================================
echo.

:: Ejecutar directamente con el python del venv
venv\Scripts\python.exe app.py

:: Si se cierra el servidor
echo.
echo Servidor detenido.
pause
