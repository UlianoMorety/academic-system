"""
Configuración de la aplicación
Carga variables de entorno y define configuraciones
"""

import os
import sys
from datetime import timedelta
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def check_required_env_vars():
    """Verifica que las variables de entorno requeridas existan"""
    required_vars = [
        'DATABASE_HOST',
        'DATABASE_USER',
        'DATABASE_PASSWORD',
        'DATABASE_NAME',
        'SECRET_KEY',
        'JWT_SECRET_KEY'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ ERROR: Faltan las siguientes variables de entorno:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nCopia .env.example a .env y configura las variables.")
        sys.exit(1)

# Verificar en desarrollo
if os.getenv('FLASK_ENV') == 'development':
    check_required_env_vars()

class Config:
    """Configuración base de la aplicación"""
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-cambiar-en-produccion')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = FLASK_ENV == 'development'
    
    # Base de Datos
    DATABASE_HOST = os.getenv('DATABASE_HOST', 'localhost')
    DATABASE_PORT = int(os.getenv('DATABASE_PORT', 3306))
    DATABASE_USER = os.getenv('DATABASE_USER', 'academic_user')
    DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD', 'Academic123!')
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'academic_system')
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-cambiar-en-produccion')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        seconds=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 1800))
    )
    JWT_ALGORITHM = 'HS256'
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:5000').split(',')
    
    # Seguridad
    BCRYPT_ROUNDS = 12
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max
    
    @staticmethod
    def get_database_uri():
        """Retorna la URI de conexión a la base de datos"""
        return {
            'host': Config.DATABASE_HOST,
            'port': Config.DATABASE_PORT,
            'user': Config.DATABASE_USER,
            'password': Config.DATABASE_PASSWORD,
            'database': Config.DATABASE_NAME,
            'charset': 'utf8mb4',
            'autocommit': False
        }

class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True

class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False

class TestingConfig(Config):
    """Configuración para tests"""
    TESTING = True
    DATABASE_NAME = os.getenv('TEST_DATABASE_NAME', 'academic_system_test')

# Diccionario de configuraciones
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}