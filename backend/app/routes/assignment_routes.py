"""
Rutas de asignaciones
Endpoints: /api/assignments/* y /api/courses/<id>/assignments
CRUD completo con autorización
"""

from flask import Blueprint, request, g
from app.auth import token_required, role_required
from app.services.assignment_service import AssignmentService
from app.services.course_service import CourseService
from app.utils.responses import (
    success_response, 
    error_response, 
    created_response,
    not_found_response
)
from app.utils.validators import sanitize_string

assignment_bp = Blueprint('assignments', __name__, url_prefix='/api')

@assignment_bp.route('/assignments', methods=['GET'])
@token_required
def get_all_assignments():
    """
    GET /api/assignments
    Lista todas las asignaciones según el rol del usuario
    
    Query params:
        - page: número de página (default: 1)
        - limit: asignaciones por página (default: 50)
    """
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))
        
        if page < 1 or limit < 1 or limit > 100:
            return error_response("Parámetros de paginación inválidos", 400)
        
        current_user = g.current_user
        
        result = AssignmentService.get_all_assignments(
            user_id=current_user['id'],
            role_name=current_user['role_name'],
            page=page,
            limit=limit
        )
        
        return success_response(result, "Asignaciones obtenidas exitosamente")
        
    except Exception as e:
        return error_response(f"Error al obtener asignaciones: {str(e)}", 500)

@assignment_bp.route('/courses/<int:course_id>/assignments', methods=['GET'])
@token_required
def get_course_assignments(course_id):
    """
    GET /api/courses/<id>/assignments
    Lista asignaciones de un curso específico
    """
    try:
        current_user = g.current_user
        
        assignments = AssignmentService.get_assignments_by_course(
            course_id,
            user_id=current_user['id'],
            role_name=current_user['role_name']
        )
        
        return success_response(
            {'assignments': assignments},
            "Asignaciones obtenidas exitosamente"
        )
        
    except ValueError as e:
        return error_response(str(e), 403)
    except Exception as e:
        return error_response(f"Error al obtener asignaciones: {str(e)}", 500)

@assignment_bp.route('/assignments/<int:assignment_id>', methods=['GET'])
@token_required
def get_assignment(assignment_id):
    """
    GET /api/assignments/<id>
    Obtiene una asignación específica
    """
    try:
        assignment = AssignmentService.get_assignment_by_id(assignment_id)
        
        if not assignment:
            return not_found_response("Asignación no encontrada")
        
        # Verificar permisos para estudiantes
        current_user = g.current_user
        if current_user['role_name'] == 'student':
            from app.database import execute_query
            enrolled = execute_query(
                "SELECT id FROM enrollments WHERE student_id = %s AND course_id = %s",
                (current_user['id'], assignment['course_id']),
                fetch_one=True
            )
            
            if not enrolled:
                return error_response("No tienes acceso a esta asignación", 403)
        
        elif current_user['role_name'] == 'teacher':
            # Verificar que sea el profesor del curso
            if assignment['teacher_id'] != current_user['id']:
                return error_response("No tienes acceso a esta asignación", 403)
        
        return success_response(assignment, "Asignación obtenida exitosamente")
        
    except Exception as e:
        return error_response(f"Error al obtener asignación: {str(e)}", 500)

@assignment_bp.route('/assignments', methods=['POST'])
@token_required
@role_required('admin', 'teacher')
def create_assignment():
    """
    POST /api/assignments
    Crea una nueva asignación
    
    Body:
        {
            "title": "string",
            "course_id": int,
            "description": "string" (opcional),
            "due_date": "YYYY-MM-DD HH:MM:SS" (opcional),
            "max_score": float (opcional, default: 100.0)
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return error_response("Datos no proporcionados", 400)
        
        # Extraer datos
        title = sanitize_string(data.get('title', ''))
        course_id = data.get('course_id')
        description = sanitize_string(data.get('description', ''))
        due_date = data.get('due_date')
        max_score = data.get('max_score', 100.0)
        
        # Validar campos requeridos
        if not title or not course_id:
            return error_response("Campos requeridos: title, course_id", 400)
        
        # Verificar permisos para teachers
        current_user = g.current_user
        if current_user['role_name'] == 'teacher':
            course = CourseService.get_course_by_id(course_id)
            if not course or course['teacher_id'] != current_user['id']:
                return error_response("No tienes permiso para crear asignaciones en este curso", 403)
        
        # Crear asignación
        assignment = AssignmentService.create_assignment(
            title, course_id, description, due_date, max_score
        )
        
        return created_response(assignment, "Asignación creada exitosamente")
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f"Error al crear asignación: {str(e)}", 500)

@assignment_bp.route('/assignments/<int:assignment_id>', methods=['PUT'])
@token_required
@role_required('admin', 'teacher')
def update_assignment(assignment_id):
    """
    PUT /api/assignments/<id>
    Actualiza una asignación
    
    Body:
        {
            "title": "string" (opcional),
            "description": "string" (opcional),
            "due_date": "YYYY-MM-DD HH:MM:SS" (opcional),
            "max_score": float (opcional)
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return error_response("Datos no proporcionados", 400)
        
        # Obtener asignación
        assignment = AssignmentService.get_assignment_by_id(assignment_id)
        if not assignment:
            return not_found_response("Asignación no encontrada")
        
        # Verificar permisos para teachers
        current_user = g.current_user
        if current_user['role_name'] == 'teacher':
            if assignment['teacher_id'] != current_user['id']:
                return error_response("No tienes permiso para modificar esta asignación", 403)
        
        # Preparar datos de actualización
        update_data = {}
        
        if 'title' in data:
            update_data['title'] = sanitize_string(data['title'])
        
        if 'description' in data:
            update_data['description'] = sanitize_string(data['description'])
        
        if 'due_date' in data:
            update_data['due_date'] = data['due_date']
        
        if 'max_score' in data:
            update_data['max_score'] = data['max_score']
        
        if not update_data:
            return error_response("No hay datos para actualizar", 400)
        
        # Actualizar asignación
        updated_assignment = AssignmentService.update_assignment(
            assignment_id, **update_data
        )
        
        return success_response(
            updated_assignment, 
            "Asignación actualizada exitosamente"
        )
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f"Error al actualizar asignación: {str(e)}", 500)

@assignment_bp.route('/assignments/<int:assignment_id>', methods=['DELETE'])
@token_required
@role_required('admin', 'teacher')
def delete_assignment(assignment_id):
    """
    DELETE /api/assignments/<id>
    Elimina una asignación
    """
    try:
        # Obtener asignación
        assignment = AssignmentService.get_assignment_by_id(assignment_id)
        if not assignment:
            return not_found_response("Asignación no encontrada")
        
        # Verificar permisos para teachers
        current_user = g.current_user
        if current_user['role_name'] == 'teacher':
            if assignment['teacher_id'] != current_user['id']:
                return error_response("No tienes permiso para eliminar esta asignación", 403)
        
        AssignmentService.delete_assignment(assignment_id)
        
        return success_response(None, "Asignación eliminada exitosamente")
        
    except ValueError as e:
        return error_response(str(e), 404)
    except Exception as e:
        return error_response(f"Error al eliminar asignación: {str(e)}", 500)