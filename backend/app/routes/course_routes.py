"""
Rutas de cursos
Endpoints: /api/courses/*
CRUD completo con autorización
"""

from flask import Blueprint, request, g
from app.auth import token_required, role_required, is_owner_or_admin
from app.services.course_service import CourseService
from app.utils.responses import (
    success_response, 
    error_response, 
    created_response,
    not_found_response
)
from app.utils.validators import sanitize_string

course_bp = Blueprint('courses', __name__, url_prefix='/api/courses')

@course_bp.route('', methods=['GET'])
@token_required
def get_courses():
    """
    GET /api/courses
    Lista cursos según el rol del usuario
    
    Query params:
        - page: número de página (default: 1)
        - limit: cursos por página (default: 50)
    """
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))
        
        if page < 1 or limit < 1 or limit > 100:
            return error_response("Parámetros de paginación inválidos", 400)
        
        current_user = g.current_user
        
        result = CourseService.get_all_courses(
            user_id=current_user['id'],
            role_name=current_user['role_name'],
            page=page,
            limit=limit
        )
        
        return success_response(result, "Cursos obtenidos exitosamente")
        
    except Exception as e:
        return error_response(f"Error al obtener cursos: {str(e)}", 500)

@course_bp.route('/<int:course_id>', methods=['GET'])
@token_required
def get_course(course_id):
    """
    GET /api/courses/<id>
    Obtiene un curso específico
    """
    try:
        course = CourseService.get_course_by_id(course_id)
        
        if not course:
            return not_found_response("Curso no encontrado")
        
        # Verificar permisos para estudiantes
        current_user = g.current_user
        if current_user['role_name'] == 'student':
            # Verificar que el estudiante esté inscrito
            from app.database import execute_query
            enrolled = execute_query(
                "SELECT id FROM enrollments WHERE student_id = %s AND course_id = %s",
                (current_user['id'], course_id),
                fetch_one=True
            )
            
            if not enrolled:
                return error_response("No tienes acceso a este curso", 403)
        
        return success_response(course, "Curso obtenido exitosamente")
        
    except Exception as e:
        return error_response(f"Error al obtener curso: {str(e)}", 500)

@course_bp.route('', methods=['POST'])
@token_required
@role_required('admin', 'teacher')
def create_course():
    """
    POST /api/courses
    Crea un nuevo curso (admin o teacher)
    
    Body:
        {
            "name": "string",
            "code": "string",
            "description": "string" (opcional),
            "teacher_id": int (opcional, solo admin)
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return error_response("Datos no proporcionados", 400)
        
        # Extraer datos
        name = sanitize_string(data.get('name', ''))
        code = sanitize_string(data.get('code', ''))
        description = sanitize_string(data.get('description', ''))
        
        # Validar campos requeridos
        if not name or not code:
            return error_response("Campos requeridos: name, code", 400)
        
        # Determinar teacher_id
        current_user = g.current_user
        if current_user['role_name'] == 'admin' and 'teacher_id' in data:
            # Admin puede asignar cualquier profesor
            teacher_id = data['teacher_id']
        else:
            # Teachers se auto-asignan
            teacher_id = current_user['id']
        
        # Crear curso
        course = CourseService.create_course(name, code, teacher_id, description)
        
        return created_response(course, "Curso creado exitosamente")
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f"Error al crear curso: {str(e)}", 500)

@course_bp.route('/<int:course_id>', methods=['PUT'])
@token_required
def update_course(course_id):
    """
    PUT /api/courses/<id>
    Actualiza un curso
    Solo el profesor dueño o admin pueden actualizar
    
    Body:
        {
            "name": "string" (opcional),
            "code": "string" (opcional),
            "description": "string" (opcional)
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return error_response("Datos no proporcionados", 400)
        
        # Obtener curso
        course = CourseService.get_course_by_id(course_id)
        if not course:
            return not_found_response("Curso no encontrado")
        
        # Verificar permisos
        if not is_owner_or_admin(course['teacher_id']):
            return error_response("No tienes permiso para modificar este curso", 403)
        
        # Preparar datos de actualización
        update_data = {}
        
        if 'name' in data:
            update_data['name'] = sanitize_string(data['name'])
        
        if 'code' in data:
            update_data['code'] = sanitize_string(data['code'])
        
        if 'description' in data:
            update_data['description'] = sanitize_string(data['description'])
        
        if not update_data:
            return error_response("No hay datos para actualizar", 400)
        
        # Actualizar curso
        updated_course = CourseService.update_course(course_id, **update_data)
        
        return success_response(updated_course, "Curso actualizado exitosamente")
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f"Error al actualizar curso: {str(e)}", 500)

@course_bp.route('/<int:course_id>', methods=['DELETE'])
@token_required
def delete_course(course_id):
    """
    DELETE /api/courses/<id>
    Elimina un curso (solo dueño o admin)
    """
    try:
        # Obtener curso
        course = CourseService.get_course_by_id(course_id)
        if not course:
            return not_found_response("Curso no encontrado")
        
        # Verificar permisos
        if not is_owner_or_admin(course['teacher_id']):
            return error_response("No tienes permiso para eliminar este curso", 403)
        
        CourseService.delete_course(course_id)
        
        return success_response(None, "Curso eliminado exitosamente")
        
    except ValueError as e:
        return error_response(str(e), 404)
    except Exception as e:
        return error_response(f"Error al eliminar curso: {str(e)}", 500)

@course_bp.route('/<int:course_id>/enroll', methods=['POST'])
@token_required
@role_required('admin', 'teacher')
def enroll_student(course_id):
    """
    POST /api/courses/<id>/enroll
    Inscribe un estudiante en el curso
    
    Body:
        {
            "student_id": int
        }
    """
    try:
        data = request.get_json()
        
        if not data or 'student_id' not in data:
            return error_response("Campo requerido: student_id", 400)
        
        student_id = data['student_id']
        
        # Verificar permisos para teachers
        current_user = g.current_user
        if current_user['role_name'] == 'teacher':
            course = CourseService.get_course_by_id(course_id)
            if not course or course['teacher_id'] != current_user['id']:
                return error_response("No tienes permiso para inscribir en este curso", 403)
        
        CourseService.enroll_student(course_id, student_id)
        
        return success_response(None, "Estudiante inscrito exitosamente")
        
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(f"Error al inscribir estudiante: {str(e)}", 500)

@course_bp.route('/<int:course_id>/students', methods=['GET'])
@token_required
def get_enrolled_students(course_id):
    """
    GET /api/courses/<id>/students
    Lista estudiantes inscritos en el curso
    """
    try:
        # Verificar que el curso existe
        course = CourseService.get_course_by_id(course_id)
        if not course:
            return not_found_response("Curso no encontrado")
        
        # Verificar permisos
        current_user = g.current_user
        if current_user['role_name'] == 'teacher':
            if course['teacher_id'] != current_user['id']:
                return error_response("No tienes acceso a este curso", 403)
        
        students = CourseService.get_enrolled_students(course_id)
        
        return success_response(
            {'students': students},
            "Estudiantes obtenidos exitosamente"
        )
        
    except Exception as e:
        return error_response(f"Error al obtener estudiantes: {str(e)}", 500)