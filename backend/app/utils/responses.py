"""
Utilidades para respuestas HTTP estandarizadas
"""

from flask import jsonify

def success_response(data=None, message="Operación exitosa", status=200):
    """
    Genera respuesta exitosa estandarizada
    
    Args:
        data: Datos a retornar
        message: Mensaje descriptivo
        status: Código HTTP
        
    Returns:
        tuple: (response, status_code)
    """
    response = {
        'success': True,
        'message': message
    }
    
    if data is not None:
        response['data'] = data
    
    return jsonify(response), status

def error_response(message="Error en la operación", status=400, errors=None):
    """
    Genera respuesta de error estandarizada
    
    Args:
        message: Mensaje de error
        status: Código HTTP
        errors: Detalles adicionales del error
        
    Returns:
        tuple: (response, status_code)
    """
    response = {
        'success': False,
        'message': message
    }
    
    if errors:
        response['errors'] = errors
    
    return jsonify(response), status

def created_response(data, message="Recurso creado exitosamente"):
    """Respuesta para recurso creado (201)"""
    return success_response(data, message, 201)

def not_found_response(message="Recurso no encontrado"):
    """Respuesta para recurso no encontrado (404)"""
    return error_response(message, 404)

def unauthorized_response(message="No autorizado"):
    """Respuesta para acceso no autorizado (401)"""
    return error_response(message, 401)

def forbidden_response(message="Acceso prohibido"):
    """Respuesta para acceso prohibido (403)"""
    return error_response(message, 403)

def validation_error_response(errors):
    """Respuesta para errores de validación (422)"""
    return error_response(
        "Error de validación",
        422,
        errors
    )