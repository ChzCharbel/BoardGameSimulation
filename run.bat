@echo off
echo Iniciando Fire Rescue Simulation Web App...
echo.

REM Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python no está instalado o no está en el PATH.
    echo Por favor instala Python 3.8+ desde https://python.org
    pause
    exit /b 1
)

REM Verificar si pip está disponible
pip --version >nul 2>&1
if errorlevel 1 (
    echo Error: pip no está disponible.
    pause
    exit /b 1
)

REM Cambiar al directorio backend
cd /d "%~dp0backend"

REM Instalar dependencias si no existen
echo Verificando dependencias...
pip show flask >nul 2>&1
if errorlevel 1 (
    echo Instalando dependencias...
    pip install -r requirements.txt
)

REM Ejecutar la aplicación
echo.
echo Iniciando servidor Flask...
echo La aplicación estará disponible en: http://localhost:5000
echo Presiona Ctrl+C para detener el servidor
echo.

python app.py