"""
Servicio de asignaciones
Lógica de negocio para operaciones CRUD de asignaciones
"""

from app.database import execute_query
from app.utils.validators import validate_string_length, validate_positive_number

class AssignmentService:
    """Servicio para gestión de asignaciones"""
    
    @staticmethod
    def get_assignments_by_course(course_id, user_id=None, role_name=None):
        """
        Obtiene asignaciones de un curso
        
        Args:
            course_id: ID del curso
            user_id: ID del usuario actual
            role_name: Rol del usuario
            
        Returns:
            list: Asignaciones del curso
        """
        # Verificar acceso al curso
        if role_name == 'student':
            # Verificar que el estudiante esté inscrito
            enrolled = execute_query(
                "SELECT id FROM enrollments WHERE student_id = %s AND course_id = %s",
                (user_id, course_id),
                fetch_one=True
            )
            
            if not enrolled:
                raise ValueError("No tienes acceso a este curso")
        
        elif role_name == 'teacher':
            # Verificar que sea el profesor del curso
            course = execute_query(
                "SELECT teacher_id FROM courses WHERE id = %s",
                (course_id,),
                fetch_one=True
            )
            
            if not course or course['teacher_id'] != user_id:
                raise ValueError("No tienes acceso a este curso")
        
        # Obtener asignaciones
        query = """
            SELECT a.id, a.title, a.description, a.course_id, 
                   a.due_date, a.max_score, a.created_at,
                   c.name as course_name, c.code as course_code
            FROM assignments a
            JOIN courses c ON a.course_id = c.id
            WHERE a.course_id = %s
            ORDER BY a.due_date ASC
        """
        
        return execute_query(query, (course_id,))
    
    @staticmethod
    def get_assignment_by_id(assignment_id):
        """
        Obtiene una asignación por ID
        
        Returns:
            dict: Asignación o None
        """
        query = """
            SELECT a.id, a.title, a.description, a.course_id,
                   a.due_date, a.max_score, a.created_at,
                   c.name as course_name, c.code as course_code,
                   c.teacher_id
            FROM assignments a
            JOIN courses c ON a.course_id = c.id
            WHERE a.id = %s
        """
        return execute_query(query, (assignment_id,), fetch_one=True)
    
    @staticmethod
    def create_assignment(title, course_id, description=None, due_date=None, max_score=100.0):
        """
        Crea una nueva asignación
        
        Returns:
            dict: Asignación creada
        Raises:
            ValueError: Si datos inválidos
        """
        # Validaciones
        if not validate_string_length(title, 3, 200):
            raise ValueError("Título debe tener entre 3 y 200 caracteres")
        
        if max_score and not validate_positive_number(max_score):
            raise ValueError("Puntaje máximo debe ser positivo")
        
        # Verificar que el curso existe
        course = execute_query(
            "SELECT id FROM courses WHERE id = %s",
            (course_id,),
            fetch_one=True
        )
        
        if not course:
            raise ValueError("Curso no encontrado")
        
        # Insertar asignación
        assignment_id = execute_query(
            """INSERT INTO assignments (title, description, course_id, due_date, max_score)
               VALUES (%s, %s, %s, %s, %s)""",
            (title, description, course_id, due_date, max_score),
            fetch_all=False
        )
        
        # Retornar asignación creada
        return AssignmentService.get_assignment_by_id(assignment_id)
    
    @staticmethod
    def update_assignment(assignment_id, **kwargs):
        """
        Actualiza una asignación
        
        Args:
            assignment_id: ID de la asignación
            **kwargs: Campos a actualizar
            
        Returns:
            dict: Asignación actualizada
        Raises:
            ValueError: Si datos inválidos
        """
        # Verificar que asignación existe
        assignment = AssignmentService.get_assignment_by_id(assignment_id)
        if not assignment:
            raise ValueError("Asignación no encontrada")
        
        updates = []
        params = []
        
        # Title
        if 'title' in kwargs:
            title = kwargs['title']
            if not validate_string_length(title, 3, 200):
                raise ValueError("Título inválido")
            updates.append("title = %s")
            params.append(title)
        
        # Description
        if 'description' in kwargs:
            updates.append("description = %s")
            params.append(kwargs['description'])
        
        # Due date
        if 'due_date' in kwargs:
            updates.append("due_date = %s")
            params.append(kwargs['due_date'])
        
        # Max score
        if 'max_score' in kwargs:
            max_score = kwargs['max_score']
            if not validate_positive_number(max_score):
                raise ValueError("Puntaje máximo inválido")
            updates.append("max_score = %s")
            params.append(max_score)
        
        # Si hay actualizaciones
        if updates:
            query = f"UPDATE assignments SET {', '.join(updates)} WHERE id = %s"
            params.append(assignment_id)
            execute_query(query, tuple(params), fetch_all=False)
        
        # Retornar asignación actualizada
        return AssignmentService.get_assignment_by_id(assignment_id)
    
    @staticmethod
    def delete_assignment(assignment_id):
        """
        Elimina una asignación
        
        Returns:
            bool: True si eliminado
        Raises:
            ValueError: Si asignación no existe
        """
        assignment = AssignmentService.get_assignment_by_id(assignment_id)
        if not assignment:
            raise ValueError("Asignación no encontrada")
        
        execute_query(
            "DELETE FROM assignments WHERE id = %s",
            (assignment_id,),
            fetch_all=False
        )
        
        return True
    
    @staticmethod
    def get_all_assignments(user_id, role_name, page=1, limit=50):
        """
        Obtiene todas las asignaciones según el rol del usuario
        
        Returns:
            dict: Lista de asignaciones y metadatos
        """
        offset = (page - 1) * limit
        
        base_query = """
            SELECT a.id, a.title, a.description, a.due_date, a.max_score, a.created_at,
                   c.name as course_name, c.code as course_code, c.id as course_id
            FROM assignments a
            JOIN courses c ON a.course_id = c.id
        """
        
        if role_name == 'teacher':
            # Profesores ven asignaciones de sus cursos
            query = base_query + " WHERE c.teacher_id = %s"
            params = (user_id, limit, offset)
            count_query = """
                SELECT COUNT(*) as total FROM assignments a
                JOIN courses c ON a.course_id = c.id
                WHERE c.teacher_id = %s
            """
            count_params = (user_id,)
        elif role_name == 'student':
            # Estudiantes ven asignaciones de cursos inscritos
            query = base_query + """
                JOIN enrollments e ON c.id = e.course_id
                WHERE e.student_id = %s
            """
            params = (user_id, limit, offset)
            count_query = """
                SELECT COUNT(*) as total FROM assignments a
                JOIN courses c ON a.course_id = c.id
                JOIN enrollments e ON c.id = e.course_id
                WHERE e.student_id = %s
            """
            count_params = (user_id,)
        else:
            # Admin ve todas
            query = base_query
            params = (limit, offset)
            count_query = "SELECT COUNT(*) as total FROM assignments"
            count_params = ()
        
        query += " ORDER BY a.due_date ASC LIMIT %s OFFSET %s"
        assignments = execute_query(query, params)
        
        # Contar total
        total = execute_query(count_query, count_params, fetch_one=True)['total']
        
        return {
            'assignments': assignments,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'pages': (total + limit - 1) // limit
            }
        }