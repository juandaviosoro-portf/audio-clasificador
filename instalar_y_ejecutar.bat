@echo off
chcp 65001 >nul 2>&1
title Sistema Clasificador de Audios IA
color 0A

echo.
echo =======================================================
echo   Sistema de Clasificacion de Audios de Clientes
echo =======================================================
echo.

:: Ir a la carpeta del script (funciona desde cualquier ubicacion)
cd /d "%~dp0"

:: Verificar que Python este instalado
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python no esta instalado o no esta en el PATH.
    echo.
    echo Descargalo desde: https://www.python.org/downloads/
    echo IMPORTANTE: Al instalar, marca la casilla "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

echo [OK] Python encontrado.

:: Verificar si el entorno virtual ya existe
if exist "venv\Scripts\activate.bat" (
    echo [OK] Entorno virtual encontrado.
    goto :ACTIVAR
)

:: Crear entorno virtual
echo.
echo [...] Creando entorno virtual...
python -m venv venv
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] No se pudo crear el entorno virtual.
    pause
    exit /b 1
)
echo [OK] Entorno virtual creado.

:ACTIVAR
:: Activar entorno virtual
call venv\Scripts\activate.bat
echo [OK] Entorno virtual activado.

:: Verificar si las dependencias ya estan instaladas
pip show flask >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] Dependencias ya instaladas.
    goto :VERIFICAR_ENV
)

:: Instalar dependencias
echo.
echo [...] Actualizando pip...
python -m pip install --upgrade pip >nul 2>&1

echo [...] Instalando Whisper (esto tarda unos minutos)...
pip install --no-cache-dir openai-whisper
if %ERRORLEVEL% NEQ 0 (
    echo [AVISO] Whisper no se pudo instalar. La app funcionara sin transcripcion de audio.
)

echo.
echo [...] Instalando el resto de dependencias...
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] No se pudieron instalar las dependencias.
    pause
    exit /b 1
)
echo [OK] Todas las dependencias instaladas.

:VERIFICAR_ENV
:: Crear .env si no existe
if not exist ".env" (
    if exist ".env.example" (
        copy .env.example .env >nul
        echo.
        echo [AVISO] Se creo el archivo .env desde .env.example
        echo         Edita .env con tu API Key de Gemini para mejor precision.
        echo         Sin API Key la app funciona igual con clasificacion local.
    )
) else (
    echo [OK] Archivo .env encontrado.
)

:: Ejecutar la app
echo.
echo =======================================================
echo   Iniciando servidor...
echo   Abri tu navegador en: http://localhost:5000
echo =======================================================
echo.
echo   Para detener el servidor presiona Ctrl+C
echo.

:: Abrir navegador automaticamente
start http://localhost:5000

:: Ejecutar
python app.py

:: Si se cierra el servidor
echo.
echo Servidor detenido.
pause
