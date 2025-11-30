"""
Servicio de cursos
Lógica de negocio para operaciones CRUD de cursos
"""

from app.database import execute_query
from app.utils.validators import validate_string_length

class CourseService:
    """Servicio para gestión de cursos"""
    
    @staticmethod
    def get_all_courses(user_id=None, role_name=None, page=1, limit=50):
        """
        Obtiene lista de cursos según el rol del usuario
        
        Args:
            user_id: ID del usuario actual
            role_name: Rol del usuario (admin, teacher, student)
            page: Número de página
            limit: Cursos por página
            
        Returns:
            dict: Lista de cursos y metadatos
        """
        offset = (page - 1) * limit
        
        # Query base
        base_query = """
            SELECT c.id, c.name, c.description, c.code, c.created_at,
                   u.username as teacher_name, u.id as teacher_id
            FROM courses c
            JOIN users u ON c.teacher_id = u.id
        """
        
        # Filtrar según rol
        if role_name == 'teacher':
            # Profesores solo ven sus cursos
            query = base_query + " WHERE c.teacher_id = %s"
            params = (user_id, limit, offset)
            count_query = "SELECT COUNT(*) as total FROM courses WHERE teacher_id = %s"
            count_params = (user_id,)
        elif role_name == 'student':
            # Estudiantes solo ven cursos en los que están inscritos
            query = """
                SELECT c.id, c.name, c.description, c.code, c.created_at,
                       u.username as teacher_name, u.id as teacher_id
                FROM courses c
                JOIN users u ON c.teacher_id = u.id
                JOIN enrollments e ON c.id = e.course_id
                WHERE e.student_id = %s
            """
            params = (user_id, limit, offset)
            count_query = """
                SELECT COUNT(*) as total FROM courses c
                JOIN enrollments e ON c.id = e.course_id
                WHERE e.student_id = %s
            """
            count_params = (user_id,)
        else:
            # Admin y administrative ven todos
            query = base_query
            params = (limit, offset)
            count_query = "SELECT COUNT(*) as total FROM courses"
            count_params = ()
        
        query += " ORDER BY c.created_at DESC LIMIT %s OFFSET %s"
        courses = execute_query(query, params)
        
        # Contar total
        total = execute_query(count_query, count_params, fetch_one=True)['total']
        
        return {
            'courses': courses,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'pages': (total + limit - 1) // limit
            }
        }
    
    @staticmethod
    def get_course_by_id(course_id):
        """
        Obtiene un curso por ID
        
        Returns:
            dict: Curso o None
        """
        query = """
            SELECT c.id, c.name, c.description, c.code, c.created_at,
                   c.teacher_id, u.username as teacher_name
            FROM courses c
            JOIN users u ON c.teacher_id = u.id
            WHERE c.id = %s
        """
        return execute_query(query, (course_id,), fetch_one=True)
    
    @staticmethod
    def create_course(name, code, teacher_id, description=None):
        """
        Crea un nuevo curso
        
        Returns:
            dict: Curso creado
        Raises:
            ValueError: Si datos inválidos
        """
        # Validaciones
        if not validate_string_length(name, 3, 100):
            raise ValueError("Nombre debe tener entre 3 y 100 caracteres")
        
        if not validate_string_length(code, 2, 20):
            raise ValueError("Código debe tener entre 2 y 20 caracteres")
        
        # Verificar que el código no esté duplicado
        existing = execute_query(
            "SELECT id FROM courses WHERE code = %s",
            (code,),
            fetch_one=True
        )
        
        if existing:
            raise ValueError("El código del curso ya existe")
        
        # Verificar que el profesor existe y tiene rol de teacher
        teacher = execute_query(
            """SELECT u.id, r.name as role_name 
               FROM users u 
               JOIN roles r ON u.role_id = r.id 
               WHERE u.id = %s""",
            (teacher_id,),
            fetch_one=True
        )
        
        if not teacher:
            raise ValueError("Profesor no encontrado")
        
        if teacher['role_name'] not in ['teacher', 'admin']:
            raise ValueError("El usuario debe ser profesor o admin")
        
        # Insertar curso
        course_id = execute_query(
            """INSERT INTO courses (name, description, code, teacher_id)
               VALUES (%s, %s, %s, %s)""",
            (name, description, code, teacher_id),
            fetch_all=False
        )
        
        # Retornar curso creado
        return CourseService.get_course_by_id(course_id)
    
    @staticmethod
    def update_course(course_id, **kwargs):
        """
        Actualiza un curso
        
        Args:
            course_id: ID del curso
            **kwargs: Campos a actualizar (name, description, code)
            
        Returns:
            dict: Curso actualizado
        Raises:
            ValueError: Si datos inválidos
        """
        # Verificar que curso existe
        course = CourseService.get_course_by_id(course_id)
        if not course:
            raise ValueError("Curso no encontrado")
        
        updates = []
        params = []
        
        # Name
        if 'name' in kwargs:
            name = kwargs['name']
            if not validate_string_length(name, 3, 100):
                raise ValueError("Nombre inválido")
            updates.append("name = %s")
            params.append(name)
        
        # Description
        if 'description' in kwargs:
            updates.append("description = %s")
            params.append(kwargs['description'])
        
        # Code
        if 'code' in kwargs:
            code = kwargs['code']
            if not validate_string_length(code, 2, 20):
                raise ValueError("Código inválido")
            
            # Verificar duplicado
            existing = execute_query(
                "SELECT id FROM courses WHERE code = %s AND id != %s",
                (code, course_id),
                fetch_one=True
            )
            if existing:
                raise ValueError("El código ya existe")
            
            updates.append("code = %s")
            params.append(code)
        
        # Si hay actualizaciones
        if updates:
            query = f"UPDATE courses SET {', '.join(updates)} WHERE id = %s"
            params.append(course_id)
            execute_query(query, tuple(params), fetch_all=False)
        
        # Retornar curso actualizado
        return CourseService.get_course_by_id(course_id)
    
    @staticmethod
    def delete_course(course_id):
        """
        Elimina un curso (también elimina asignaciones relacionadas en cascada)
        
        Returns:
            bool: True si eliminado
        Raises:
            ValueError: Si curso no existe
        """
        course = CourseService.get_course_by_id(course_id)
        if not course:
            raise ValueError("Curso no encontrado")
        
        # Eliminar curso (las asignaciones se eliminan por CASCADE)
        execute_query(
            "DELETE FROM courses WHERE id = %s",
            (course_id,),
            fetch_all=False
        )
        
        return True
    
    @staticmethod
    def enroll_student(course_id, student_id):
        """
        Inscribe un estudiante en un curso
        
        Raises:
            ValueError: Si datos inválidos o ya inscrito
        """
        # Verificar que curso existe
        course = CourseService.get_course_by_id(course_id)
        if not course:
            raise ValueError("Curso no encontrado")
        
        # Verificar que estudiante existe y tiene rol student
        student = execute_query(
            """SELECT u.id, r.name as role_name 
               FROM users u 
               JOIN roles r ON u.role_id = r.id 
               WHERE u.id = %s""",
            (student_id,),
            fetch_one=True
        )
        
        if not student:
            raise ValueError("Estudiante no encontrado")
        
        if student['role_name'] != 'student':
            raise ValueError("El usuario debe ser estudiante")
        
        # Verificar que no esté ya inscrito
        existing = execute_query(
            "SELECT id FROM enrollments WHERE student_id = %s AND course_id = %s",
            (student_id, course_id),
            fetch_one=True
        )
        
        if existing:
            raise ValueError("El estudiante ya está inscrito en este curso")
        
        # Inscribir
        execute_query(
            "INSERT INTO enrollments (student_id, course_id) VALUES (%s, %s)",
            (student_id, course_id),
            fetch_all=False
        )
        
        return True
    
    @staticmethod
    def get_enrolled_students(course_id):
        """
        Obtiene lista de estudiantes inscritos en un curso
        
        Returns:
            list: Estudiantes inscritos
        """
        query = """
            SELECT u.id, u.username, u.email, e.enrolled_at
            FROM users u
            JOIN enrollments e ON u.id = e.student_id
            WHERE e.course_id = %s
            ORDER BY e.enrolled_at DESC
        """
        return execute_query(query, (course_id,))