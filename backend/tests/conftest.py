"""
Configuración de pytest
Fixtures y setup para tests
"""

import pytest
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app.utils import create_app
from app.database import get_db_connection
from app.services.auth_service import AuthService

@pytest.fixture
def app():
    """Crea y configura una instancia de la app para tests"""
    app = create_app('testing')
    return app

@pytest.fixture
def client(app):
    """Cliente de prueba para hacer peticiones"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Runner de comandos CLI"""
    return app.test_cli_runner()

@pytest.fixture
def auth_headers():
    """Headers de autorización para tests"""
    # Crear usuario de prueba y obtener token
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Crear rol admin si no existe
        cursor.execute("SELECT id FROM roles WHERE name = 'admin'")
        role = cursor.fetchone()
        
        if not role:
            cursor.execute(
                "INSERT INTO roles (name, description) VALUES ('admin', 'Administrator')"
            )
            conn.commit()
            role_id = cursor.lastrowid
        else:
            role_id = role['id']
        
        # Crear usuario de prueba si no existe
        cursor.execute("SELECT id FROM users WHERE username = 'test_user'")
        user = cursor.fetchone()
        
        if not user:
            password_hash = AuthService.hash_password('Test123!')
            cursor.execute(
                """INSERT INTO users (username, email, password_hash, role_id)
                   VALUES ('test_user', 'test@test.com', %s, %s)""",
                (password_hash, role_id)
            )
            conn.commit()
            user_id = cursor.lastrowid
        else:
            user_id = user['id']
        
        # Generar token
        token = AuthService.generate_token(user_id, 'test_user', 'admin')
        
        return {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
    finally:
        cursor.close()
        conn.close()

@pytest.fixture
def sample_user_data():
    """Datos de ejemplo para crear usuario"""
    return {
        'username': 'newuser',
        'email': 'newuser@test.com',
        'password': 'NewUser123!',
        'role': 'student'
    }

@pytest.fixture(autouse=True)
def cleanup_test_data():
    """Limpia datos de prueba después de cada test"""
    yield
    
    # Aquí puedes agregar lógica para limpiar datos de prueba
    # Por ejemplo, eliminar usuarios creados durante tests