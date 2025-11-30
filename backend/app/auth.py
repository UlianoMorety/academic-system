"""
Módulo de autenticación y autorización
Decoradores para proteger rutas con JWT
"""

import jwt
from functools import wraps
from flask import request, g
from app.config import Config
from app.utils.responses import error_response
from app.database import execute_query

def get_token_from_header():
    """Extrae el token JWT del header Authorization"""
    auth_header = request.headers.get('Authorization')
    
    if not auth_header:
        return None
    
    parts = auth_header.split()
    
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        return None
    
    return parts[1]

def decode_token(token):
    """
    Decodifica y valida un token JWT
    
    Returns:
        dict: Payload del token
    Raises:
        jwt.InvalidTokenError: Si el token es inválido
    """
    try:
        payload = jwt.decode(
            token,
            Config.JWT_SECRET_KEY,
            algorithms=[Config.JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise jwt.InvalidTokenError("Token expirado")
    except jwt.InvalidTokenError:
        raise jwt.InvalidTokenError("Token inválido")

def token_required(f):
    """
    Decorador para requerir autenticación JWT
    Almacena el usuario en g.current_user
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = get_token_from_header()
        
        if not token:
            return error_response("Token no proporcionado", 401)
        
        try:
            payload = decode_token(token)
            user_id = payload.get('user_id')
            
            # Obtener usuario de la BD
            query = """
                SELECT u.id, u.username, u.email, u.is_active, 
                       r.name as role_name, u.role_id
                FROM users u
                JOIN roles r ON u.role_id = r.id
                WHERE u.id = %s AND u.is_active = TRUE
            """
            user = execute_query(query, (user_id,), fetch_one=True)
            
            if not user:
                return error_response("Usuario no encontrado o inactivo", 401)
            
            # Almacenar usuario en contexto
            g.current_user = user
            
        except jwt.InvalidTokenError as e:
            return error_response(str(e), 401)
        except Exception as e:
            return error_response(f"Error de autenticación: {str(e)}", 401)
        
        return f(*args, **kwargs)
    
    return decorated

def role_required(*allowed_roles):
    """
    Decorador para requerir roles específicos
    Debe usarse después de @token_required
    
    Uso:
        @token_required
        @role_required('admin', 'teacher')
        def my_route():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not hasattr(g, 'current_user'):
                return error_response("Usuario no autenticado", 401)
            
            user_role = g.current_user.get('role_name')
            
            if user_role not in allowed_roles:
                return error_response(
                    f"Acceso denegado. Se requiere rol: {', '.join(allowed_roles)}", 
                    403
                )
            
            return f(*args, **kwargs)
        
        return decorated
    return decorator

def is_owner_or_admin(resource_owner_id):
    """
    Verifica si el usuario actual es el dueño del recurso o admin
    
    Args:
        resource_owner_id: ID del dueño del recurso
        
    Returns:
        bool: True si es dueño o admin
    """
    if not hasattr(g, 'current_user'):
        return False
    
    current_user = g.current_user
    is_admin = current_user.get('role_name') == 'admin'
    is_owner = current_user.get('id') == resource_owner_id
    
    return is_admin or is_owner