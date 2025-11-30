"""
Rutas de autenticación
Endpoints: /api/auth/*
"""

from flask import Blueprint, request
from app.services.auth_service import AuthService
from app.utils.responses import success_response, error_response, created_response
from app.utils.validators import sanitize_string

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    POST /api/auth/register
    Registra un nuevo usuario
    
    Body:
        {
            "username": "string",
            "email": "string",
            "password": "string",
            "role": "student|teacher|admin|administrative" (opcional, default: student)
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return error_response("Datos no proporcionados", 400)
        
        # Extraer y sanitizar datos
        username = sanitize_string(data.get('username', ''))
        email = sanitize_string(data.get('email', ''))
        password = data.get('password', '')
        role = sanitize_string(data.get('role', 'student'))
        
        # Validar campos requeridos
        if not username or not email or not password:
            return error_response("Campos requeridos: username, email, password", 400)
        
        # Registrar usuario
        user = AuthService.register(username, email, password, role)
        
        return created_response(
            user,
            "Usuario registrado exitosamente"
        )
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f"Error al registrar usuario: {str(e)}", 500)

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    POST /api/auth/login
    Inicia sesión y retorna token JWT
    
    Body:
        {
            "username": "string",  // puede ser username o email
            "password": "string"
        }
    
    Response:
        {
            "success": true,
            "message": "...",
            "data": {
                "token": "jwt_token",
                "user": {
                    "id": int,
                    "username": "string",
                    "email": "string",
                    "role": "string"
                }
            }
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return error_response("Datos no proporcionados", 400)
        
        # Extraer datos
        username = sanitize_string(data.get('username', ''))
        password = data.get('password', '')
        
        # Validar campos requeridos
        if not username or not password:
            return error_response("Campos requeridos: username, password", 400)
        
        # Autenticar
        result = AuthService.login(username, password)
        
        return success_response(
            result,
            "Inicio de sesión exitoso"
        )
        
    except ValueError as e:
        return error_response(str(e), 401)
    except Exception as e:
        return error_response(f"Error al iniciar sesión: {str(e)}", 500)