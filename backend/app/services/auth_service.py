"""
Servicio de autenticación
Maneja registro, login y generación de tokens
"""

import jwt
import bcrypt
from datetime import datetime, timedelta
from app.config import Config
from app.database import execute_query
from app.utils.validators import validate_email, validate_password, validate_username

class AuthService:
    """Servicio para operaciones de autenticación"""
    
    @staticmethod
    def hash_password(password):
        """Hashea una contraseña con bcrypt"""
        salt = bcrypt.gensalt(rounds=Config.BCRYPT_ROUNDS)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def verify_password(password, password_hash):
        """Verifica si una contraseña coincide con su hash"""
        return bcrypt.checkpw(
            password.encode('utf-8'), 
            password_hash.encode('utf-8')
        )
    
    @staticmethod
    def generate_token(user_id, username, role_name):
        """
        Genera un token JWT para un usuario
        
        Returns:
            str: Token JWT
        """
        payload = {
            'user_id': user_id,
            'username': username,
            'role': role_name,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + Config.JWT_ACCESS_TOKEN_EXPIRES
        }
        
        token = jwt.encode(
            payload,
            Config.JWT_SECRET_KEY,
            algorithm=Config.JWT_ALGORITHM
        )
        
        return token
    
    @staticmethod
    def register(username, email, password, role_name='student'):
        """
        Registra un nuevo usuario
        
        Args:
            username: Nombre de usuario
            email: Correo electrónico
            password: Contraseña
            role_name: Rol del usuario (default: student)
            
        Returns:
            dict: Usuario creado o None si hay error
        Raises:
            ValueError: Si los datos son inválidos
        """
        # Validaciones
        if not validate_username(username):
            raise ValueError("Nombre de usuario inválido (3-50 caracteres alfanuméricos)")
        
        if not validate_email(email):
            raise ValueError("Correo electrónico inválido")
        
        if not validate_password(password):
            raise ValueError("Contraseña debe tener mínimo 8 caracteres, 1 mayúscula, 1 número y 1 símbolo")
        
        # Verificar si usuario ya existe
        existing = execute_query(
            "SELECT id FROM users WHERE username = %s OR email = %s",
            (username, email),
            fetch_one=True
        )
        
        if existing:
            raise ValueError("Usuario o correo ya registrado")
        
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
        
        # Insertar usuario
        user_id = execute_query(
            """INSERT INTO users (username, email, password_hash, role_id) 
               VALUES (%s, %s, %s, %s)""",
            (username, email, password_hash, role['id']),
            fetch_all=False
        )
        
        # Retornar usuario creado
        return {
            'id': user_id,
            'username': username,
            'email': email,
            'role': role_name
        }
    
    @staticmethod
    def login(username, password):
        """
        Autentica un usuario y genera token
        
        Args:
            username: Nombre de usuario o email
            password: Contraseña
            
        Returns:
            dict: Token y datos del usuario
        Raises:
            ValueError: Si las credenciales son inválidas
        """
        # Buscar usuario por username o email
        query = """
            SELECT u.id, u.username, u.email, u.password_hash, u.is_active,
                   r.name as role_name
            FROM users u
            JOIN roles r ON u.role_id = r.id
            WHERE (u.username = %s OR u.email = %s)
        """
        user = execute_query(query, (username, username), fetch_one=True)
        
        if not user:
            raise ValueError("Credenciales inválidas")
        
        if not user['is_active']:
            raise ValueError("Usuario inactivo")
        
        # Verificar contraseña
        if not AuthService.verify_password(password, user['password_hash']):
            raise ValueError("Credenciales inválidas")
        
        # Generar token
        token = AuthService.generate_token(
            user['id'],
            user['username'],
            user['role_name']
        )
        
        return {
            'token': token,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'role': user['role_name']
            }
        }