"""
Servicio de usuarios
Lógica de negocio para operaciones CRUD de usuarios
"""

from app.database import execute_query
from app.services.auth_service import AuthService
from app.utils.validators import (
    validate_email, 
    validate_username, 
    validate_password,
    validate_role
)

class UserService:
    """Servicio para gestión de usuarios"""
    
    @staticmethod
    def get_all_users(page=1, limit=50):
        """
        Obtiene lista de usuarios con paginación
        
        Args:
            page: Número de página
            limit: Usuarios por página
            
        Returns:
            dict: Lista de usuarios y metadatos
        """
        offset = (page - 1) * limit
        
        # Consulta con JOIN para obtener rol
        query = """
            SELECT u.id, u.username, u.email, u.is_active, u.created_at,
                   r.name as role_name
            FROM users u
            JOIN roles r ON u.role_id = r.id
            ORDER BY u.created_at DESC
            LIMIT %s OFFSET %s
        """
        users = execute_query(query, (limit, offset))
        
        # Contar total
        count_query = "SELECT COUNT(*) as total FROM users"
        total = execute_query(count_query, fetch_one=True)['total']
        
        return {
            'users': users,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'pages': (total + limit - 1) // limit
            }
        }
    
    @staticmethod
    def get_user_by_id(user_id):
        """
        Obtiene un usuario por ID
        
        Returns:
            dict: Usuario o None
        """
        query = """
            SELECT u.id, u.username, u.email, u.is_active, u.created_at,
                   r.id as role_id, r.name as role_name
            FROM users u
            JOIN roles r ON u.role_id = r.id
            WHERE u.id = %s
        """
        return execute_query(query, (user_id,), fetch_one=True)
    
    @staticmethod
    def create_user(username, email, password, role_name='student'):
        """
        Crea un nuevo usuario
        
        Returns:
            dict: Usuario creado
        Raises:
            ValueError: Si datos inválidos
        """
        # Validaciones
        if not validate_username(username):
            raise ValueError("Nombre de usuario inválido")
        
        if not validate_email(email):
            raise ValueError("Email inválido")
        
        if not validate_password(password):
            raise ValueError("Contraseña inválida")
        
        if not validate_role(role_name):
            raise ValueError("Rol inválido")
        
        # Verificar duplicados
        existing = execute_query(
            "SELECT id FROM users WHERE username = %s OR email = %s",
            (username, email),
            fetch_one=True
        )
        
        if existing:
            raise ValueError("Usuario o email ya existe")
        
        # Obtener role_id
        role = execute_query(
            "SELECT id FROM roles WHERE name = %s",
            (role_name,),
            fetch_one=True
        )
        
        if not role:
            raise ValueError(f"Rol '{role_name}' no existe")
        
        # Hashear contraseña
        password_hash = AuthService.hash_password(password)
        
        # Insertar
        user_id = execute_query(
            """INSERT INTO users (username, email, password_hash, role_id)
               VALUES (%s, %s, %s, %s)""",
            (username, email, password_hash, role['id']),
            fetch_all=False
        )
        
        # Retornar usuario creado
        return UserService.get_user_by_id(user_id)
    
    @staticmethod
    def update_user(user_id, **kwargs):
        """
        Actualiza un usuario
        
        Args:
            user_id: ID del usuario
            **kwargs: Campos a actualizar (username, email, role_name, is_active)
            
        Returns:
            dict: Usuario actualizado
        Raises:
            ValueError: Si datos inválidos
        """
        # Verificar que usuario existe
        user = UserService.get_user_by_id(user_id)
        if not user:
            raise ValueError("Usuario no encontrado")
        
        updates = []
        params = []
        
        # Username
        if 'username' in kwargs:
            username = kwargs['username']
            if not validate_username(username):
                raise ValueError("Username inválido")
            
            # Verificar duplicado
            existing = execute_query(
                "SELECT id FROM users WHERE username = %s AND id != %s",
                (username, user_id),
                fetch_one=True
            )
            if existing:
                raise ValueError("Username ya existe")
            
            updates.append("username = %s")
            params.append(username)
        
        # Email
        if 'email' in kwargs:
            email = kwargs['email']
            if not validate_email(email):
                raise ValueError("Email inválido")
            
            # Verificar duplicado
            existing = execute_query(
                "SELECT id FROM users WHERE email = %s AND id != %s",
                (email, user_id),
                fetch_one=True
            )
            if existing:
                raise ValueError("Email ya existe")
            
            updates.append("email = %s")
            params.append(email)
        
        # Role
        if 'role_name' in kwargs:
            role_name = kwargs['role_name']
            if not validate_role(role_name):
                raise ValueError("Rol inválido")
            
            role = execute_query(
                "SELECT id FROM roles WHERE name = %s",
                (role_name,),
                fetch_one=True
            )
            if not role:
                raise ValueError("Rol no encontrado")
            
            updates.append("role_id = %s")
            params.append(role['id'])
        
        # Is Active
        if 'is_active' in kwargs:
            updates.append("is_active = %s")
            params.append(bool(kwargs['is_active']))
        
        # Si hay actualizaciones
        if updates:
            query = f"UPDATE users SET {', '.join(updates)} WHERE id = %s"
            params.append(user_id)
            execute_query(query, tuple(params), fetch_all=False)
        
        # Retornar usuario actualizado
        return UserService.get_user_by_id(user_id)
    
    @staticmethod
    def delete_user(user_id):
        """
        Elimina un usuario (soft delete - marca como inactivo)
        
        Returns:
            bool: True si eliminado
        Raises:
            ValueError: Si usuario no existe
        """
        user = UserService.get_user_by_id(user_id)
        if not user:
            raise ValueError("Usuario no encontrado")
        
        # Soft delete
        execute_query(
            "UPDATE users SET is_active = FALSE WHERE id = %s",
            (user_id,),
            fetch_all=False
        )
        
        return True
    
    @staticmethod
    def change_password(user_id, old_password, new_password):
        """
        Cambia la contraseña de un usuario
        
        Raises:
            ValueError: Si datos inválidos
        """
        # Obtener usuario
        user_data = execute_query(
            "SELECT password_hash FROM users WHERE id = %s",
            (user_id,),
            fetch_one=True
        )
        
        if not user_data:
            raise ValueError("Usuario no encontrado")
        
        # Verificar contraseña actual
        if not AuthService.verify_password(old_password, user_data['password_hash']):
            raise ValueError("Contraseña actual incorrecta")
        
        # Validar nueva contraseña
        if not validate_password(new_password):
            raise ValueError("Nueva contraseña no cumple requisitos")
        
        # Actualizar
        new_hash = AuthService.hash_password(new_password)
        execute_query(
            "UPDATE users SET password_hash = %s WHERE id = %s",
            (new_hash, user_id),
            fetch_all=False
        )
        
        return True