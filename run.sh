#!/bin/bash

echo "Iniciando Fire Rescue Simulation Web App..."
echo

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Verificar si Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 no está instalado."
    echo "Por favor instala Python 3.8+ desde https://python.org"
    exit 1
fi

# Verificar si pip está disponible
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 no está disponible."
    exit 1
fi

# Change to backend directory
cd "$SCRIPT_DIR/backend"

# Instalar dependencias si no existen
echo "Verificando dependencias..."
if ! pip3 show flask &> /dev/null; then
    echo "Instalando dependencias..."
    pip3 install -r requirements.txt
fi

# Ejecutar la aplicación
echo
echo "Iniciando servidor Flask..."
echo "La aplicación estará disponible en: http://localhost:5000"
echo "Presiona Ctrl+C para detener el servidor"
echo

python3 app.py