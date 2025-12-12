#!/usr/bin/env python3
"""
Fire Rescue Simulation - Setup Script
Este script configura el entorno de desarrollo
"""

import os
import sys
import subprocess
from pathlib import Path

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.absolute()
BACKEND_DIR = PROJECT_ROOT / "backend"

def create_logs_directory():
    """Crear directorio de logs si no existe"""
    logs_dir = BACKEND_DIR / "logs"
    if not logs_dir.exists():
        logs_dir.mkdir(parents=True)
        print("✅ Directorio de logs creado")
    else:
        print("📁 Directorio de logs ya existe")

def check_env_file():
    """Verificar si existe el archivo .env"""
    env_file = BACKEND_DIR / ".env"
    env_example = BACKEND_DIR / ".env.example"
    
    if not env_file.exists():
        if env_example.exists():
            import shutil
            shutil.copy(env_example, env_file)
            print("✅ Archivo .env creado desde .env.example")
            print("⚠️  Revisa y ajusta las variables en .env según tu entorno")
        else:
            print("ℹ️  No se encontró .env.example (opcional)")
            return True
    else:
        print("📄 Archivo .env ya existe")
    
    return True

def install_dependencies():
    """Instalar dependencias Python"""
    requirements_file = BACKEND_DIR / "requirements.txt"
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(requirements_file)])
        print("✅ Dependencias instaladas correctamente")
        return True
    except subprocess.CalledProcessError:
        print("❌ Error instalando dependencias")
        return False

def check_python_version():
    """Verificar versión de Python"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} no compatible (requiere 3.8+)")
        return False

def main():
    """Función principal de setup"""
    print("🚒 Fire Rescue Simulation - Configuración del Entorno")
    print("=" * 50)
    print(f"📂 Directorio del proyecto: {PROJECT_ROOT}")
    print(f"📂 Directorio backend: {BACKEND_DIR}")
    print()
    
    # Verificar Python
    if not check_python_version():
        sys.exit(1)
    
    # Crear directorios necesarios
    create_logs_directory()
    
    # Verificar archivo .env
    if not check_env_file():
        sys.exit(1)
    
    # Instalar dependencias
    if not install_dependencies():
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 ¡Configuración completada!")
    print("\nPara ejecutar la aplicación:")
    print(f"  cd {BACKEND_DIR}")
    print("  python app.py")
    print("\nO usar el script:")
    print("  ./run.bat (Windows)")
    print("  bash run.sh (Linux/Mac)")
    print("\nLa aplicación estará disponible en: http://localhost:5000")

if __name__ == "__main__":
    main()