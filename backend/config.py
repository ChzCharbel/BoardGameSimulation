"""
Fire Rescue Web App Configuration
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

class Config:
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'fire-rescue-secret-key-2025'
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    HOST = os.environ.get('FLASK_HOST') or '0.0.0.0'
    PORT = int(os.environ.get('FLASK_PORT') or 5000)
    
    # SocketIO Configuration
    SOCKETIO_ASYNC_MODE = os.environ.get('SOCKETIO_ASYNC_MODE') or 'threading'
    SOCKETIO_CORS_ALLOWED_ORIGINS = os.environ.get('SOCKETIO_CORS_ALLOWED_ORIGINS') or "*"
    
    # Simulation Configuration
    MAX_SIMULATIONS = int(os.environ.get('MAX_SIMULATIONS') or 100)
    DEFAULT_STEP_DELAY = float(os.environ.get('DEFAULT_STEP_DELAY') or 2.0)
    SIMULATION_TIMEOUT_MINUTES = int(os.environ.get('SIMULATION_TIMEOUT_MINUTES') or 60)
    
    # Game Configuration
    MAX_FIREFIGHTERS = int(os.environ.get('MAX_FIREFIGHTERS') or 6)
    GRID_WIDTH = int(os.environ.get('GRID_WIDTH') or 8)
    GRID_HEIGHT = int(os.environ.get('GRID_HEIGHT') or 6)
    VICTIMS_TO_WIN = int(os.environ.get('VICTIMS_TO_WIN') or 7)
    MAX_VICTIMS_LOST = int(os.environ.get('MAX_VICTIMS_LOST') or 4)
    MAX_STRUCTURAL_DAMAGE = int(os.environ.get('MAX_STRUCTURAL_DAMAGE') or 24)
    
    # Performance Configuration
    AUTO_CLEANUP_INACTIVE_SIMULATIONS = os.environ.get('AUTO_CLEANUP_INACTIVE_SIMULATIONS', 'True').lower() == 'true'
    CLEANUP_INTERVAL_MINUTES = int(os.environ.get('CLEANUP_INTERVAL_MINUTES') or 30)
    
    # Logging Configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    LOG_FILE = os.environ.get('LOG_FILE') or 'logs/fire_rescue.log'

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    if not SECRET_KEY:
        raise ValueError("No SECRET_KEY set for production environment")

class TestingConfig(Config):
    TESTING = True
    DEBUG = True

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}