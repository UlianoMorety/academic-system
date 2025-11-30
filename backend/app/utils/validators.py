"""
Módulo de validaciones
Funciones para validar datos de entrada
"""

import re
from datetime import datetime

def validate_email(email):
    """
    Valida formato de correo electrónico
    
    Returns:
        bool: True si es válido
    """
    if not email or not isinstance(email, str):
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_username(username):
    """
    Valida nombre de usuario (3-50 caracteres alfanuméricos y _)
    
    Returns:
        bool: True si es válido
    """
    if not username or not isinstance(username, str):
        return False
    
    if len(username) < 3 or len(username) > 50:
        return False
    
    pattern = r'^[a-zA-Z0-9_]+$'
    return re.match(pattern, username) is not None

def validate_password(password):
    """
    Valida contraseña fuerte:
    - Mínimo 8 caracteres
    - Al menos 1 mayúscula
    - Al menos 1 minúscula
    - Al menos 1 número
    - Al menos 1 símbolo especial
    
    Returns:
        bool: True si es válida
    """
    if not password or not isinstance(password, str):
        return False
    
    if len(password) < 8:
        return False
    
    has_upper = re.search(r'[A-Z]', password) is not None
    has_lower = re.search(r'[a-z]', password) is not None
    has_digit = re.search(r'\d', password) is not None
    has_special = re.search(r'[!@#$%^&*(),.?":{}|<>]', password) is not None
    
    return has_upper and has_lower and has_digit and has_special

def validate_required_fields(data, required_fields):
    """
    Valida que todos los campos requeridos estén presentes
    
    Args:
        data: Diccionario con los datos
        required_fields: Lista de campos requeridos
        
    Returns:
        tuple: (is_valid, missing_fields)
    """
    missing = [field for field in required_fields if not data.get(field)]
    return len(missing) == 0, missing

def validate_string_length(value, min_length=1, max_length=255):
    """
    Valida longitud de cadena
    
    Returns:
        bool: True si es válida
    """
    if not value or not isinstance(value, str):
        return False
    
    length = len(value.strip())
    return min_length <= length <= max_length

def validate_positive_number(value):
    """
    Valida que sea un número positivo
    
    Returns:
        bool: True si es válido
    """
    try:
        num = float(value)
        return num > 0
    except (ValueError, TypeError):
        return False

def validate_date_format(date_string, format='%Y-%m-%d'):
    """
    Valida formato de fecha
    
    Returns:
        bool: True si es válida
    """
    try:
        datetime.strptime(date_string, format)
        return True
    except (ValueError, TypeError):
        return False

def validate_datetime_format(datetime_string, format='%Y-%m-%d %H:%M:%S'):
    """
    Valida formato de fecha y hora
    
    Returns:
        bool: True si es válida
    """
    try:
        datetime.strptime(datetime_string, format)
        return True
    except (ValueError, TypeError):
        return False

def sanitize_string(value):
    """
    Sanitiza una cadena removiendo caracteres peligrosos
    
    Returns:
        str: Cadena sanitizada
    """
    if not value:
        return ''
    
    # Remover caracteres peligrosos
    value = str(value).strip()
    
    # Remover caracteres de control
    value = ''.join(char for char in value if ord(char) >= 32)
    
    return value

def validate_role(role_name):
    """
    Valida que el rol sea uno de los permitidos
    
    Returns:
        bool: True si es válido
    """
    valid_roles = ['admin', 'teacher', 'student', 'administrative']
    return role_name in valid_roles

def safe_int(value, default=1, min_value=None, max_value=None):
    """
    Convierte de forma segura un valor a entero
    
    Args:
        value: Valor a convertir
        default: Valor por defecto si falla
        min_value: Valor mínimo permitido
        max_value: Valor máximo permitido
        
    Returns:
        int: Valor convertido o default
    """
    try:
        result = int(value)
        
        if min_value is not None and result < min_value:
            return default
        
        if max_value is not None and result > max_value:
            return default
        
        return result
    except (ValueError, TypeError):
        return default