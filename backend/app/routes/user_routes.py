"""
Rutas de usuarios
Endpoints: /api/users/*
CRUD completo con autorización
"""

from flask import Blueprint, request, g
from app.auth import token_required, role_required
from app.services.user_service import UserService
from app.utils.responses import (
    success_response, 
    error_response, 
    created_response,
    not_found_response
)
from app.utils.validators import sanitize_string, safe_int

user_bp = Blueprint('users', __name__, url_prefix='/api/users')

@user_bp.route('', methods=['GET'])
@token_required
@role_required('admin', 'administrative')
def get_users():
    """
    GET /api/users
    Lista todos los usuarios (solo admin/administrative)
    
    Query params:
        - page: número de página (default: 1)
        - limit: usuarios por página (default: 50)
    """
    try:
        page = safe_int(request.args.get('page', 1), default=1, min_value=1)
        limit = safe_int(request.args.get('limit', 50), default=50, min_value=1, max_value=100)
        
        result = UserService.get_all_users(page, limit)
        
        return success_response(result, "Usuarios obtenidos exitosamente")
        
    except Exception as e:
        return error_response(f"Error al obtener usuarios: {str(e)}", 500)

@user_bp.route('/<int:user_id>', methods=['GET'])
@token_required
def get_user(user_id):
    """
    GET /api/users/<id>
    Obtiene un usuario específico
    Usuarios pueden ver su propia información, admin puede ver todos
    """
    try:
        # Verificar permisos
        current_user = g.current_user
        if current_user['role_name'] not in ['admin', 'administrative']:
            if current_user['id'] != user_id:
                return error_response("No autorizado", 403)
        
        user = UserService.get_user_by_id(user_id)
        
        if not user:
            return not_found_response("Usuario no encontrado")
        
        # Remover datos sensibles
        user_data = {k: v for k, v in user.items() if k != 'password_hash'}
        
        return success_response(user_data, "Usuario obtenido exitosamente")
        
    except Exception as e:
        return error_response(f"Error al obtener usuario: {str(e)}", 500)

@user_bp.route('', methods=['POST'])
@token_required
@role_required('admin')
def create_user():
    """
    POST /api/users
    Crea un nuevo usuario (solo admin)
    
    Body:
        {
            "username": "string",
            "email": "string",
            "password": "string",
            "role": "admin|teacher|student|administrative"
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return error_response("Datos no proporcionados", 400)
        
        # Extraer datos
        username = sanitize_string(data.get('username', ''))
        email = sanitize_string(data.get('email', ''))
        password = data.get('password', '')
        role = sanitize_string(data.get('role', 'student'))
        
        # Validar campos requeridos
        if not username or not email or not password:
            return error_response(
                "Campos requeridos: username, email, password", 
                400
            )
        
        # Crear usuario
        user = UserService.create_user(username, email, password, role)
        
        # Remover datos sensibles
        user_data = {k: v for k, v in user.items() if k != 'password_hash'}
        
        return created_response(user_data, "Usuario creado exitosamente")
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f"Error al crear usuario: {str(e)}", 500)

@user_bp.route('/<int:user_id>', methods=['PUT'])
@token_required
def update_user(user_id):
    """
    PUT /api/users/<id>
    Actualiza un usuario
    Usuarios pueden actualizar su propia info, admin puede actualizar cualquiera
    
    Body:
        {
            "username": "string" (opcional),
            "email": "string" (opcional),
            "role": "string" (opcional, solo admin),
            "is_active": boolean (opcional, solo admin)
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return error_response("Datos no proporcionados", 400)
        
        # Verificar permisos
        current_user = g.current_user
        is_admin = current_user['role_name'] == 'admin'
        
        if not is_admin and current_user['id'] != user_id:
            return error_response("No autorizado", 403)
        
        # Preparar datos de actualización
        update_data = {}
        
        if 'username' in data:
            update_data['username'] = sanitize_string(data['username'])
        
        if 'email' in data:
            update_data['email'] = sanitize_string(data['email'])
        
        # Solo admin puede cambiar rol y estado
        if is_admin:
            if 'role' in data:
                update_data['role_name'] = sanitize_string(data['role'])
            
            if 'is_active' in data:
                update_data['is_active'] = data['is_active']
        
        if not update_data:
            return error_response("No hay datos para actualizar", 400)
        
        # Actualizar usuario
        user = UserService.update_user(user_id, **update_data)
        
        if not user:
            return not_found_response("Usuario no encontrado")
        
        # Remover datos sensibles
        user_data = {k: v for k, v in user.items() if k != 'password_hash'}
        
        return success_response(user_data, "Usuario actualizado exitosamente")
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f"Error al actualizar usuario: {str(e)}", 500)

@user_bp.route('/<int:user_id>', methods=['DELETE'])
@token_required
@role_required('admin')
def delete_user(user_id):
    """
    DELETE /api/users/<id>
    Elimina (desactiva) un usuario (solo admin)
    """
    try:
        # No permitir auto-eliminación
        if g.current_user['id'] == user_id:
            return error_response("No puedes eliminar tu propia cuenta", 400)
        
        UserService.delete_user(user_id)
        
        return success_response(None, "Usuario eliminado exitosamente")
        
    except ValueError as e:
        return error_response(str(e), 404)
    except Exception as e:
        return error_response(f"Error al eliminar usuario: {str(e)}", 500)

@user_bp.route('/change-password', methods=['POST'])
@token_required
def change_password():
    """
    POST /api/users/change-password
    Cambia la contraseña del usuario actual
    
    Body:
        {
            "old_password": "string",
            "new_password": "string"
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return error_response("Datos no proporcionados", 400)
        
        old_password = data.get('old_password', '')
        new_password = data.get('new_password', '')
        
        if not old_password or not new_password:
            return error_response(
                "Campos requeridos: old_password, new_password", 
                400
            )
        
        user_id = g.current_user['id']
        
        UserService.change_password(user_id, old_password, new_password)
        
        return success_response(None, "Contraseña actualizada exitosamente")
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f"Error al cambiar contraseña: {str(e)}", 500)