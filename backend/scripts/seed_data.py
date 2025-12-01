"""
Script para cargar datos de prueba en la base de datos
VERSIÓN MEJORADA - Con manejo robusto de errores
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import bcrypt
from datetime import datetime, timedelta
from app.database import get_db_connection

def hash_password(password):
    """Hashea una contraseña usando bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(12)).decode('utf-8')

def seed_data():
    """Inserta datos de prueba en todas las tablas"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        print("🌱 Insertando datos de prueba...\n")
        
        # ============================================
        # 1. INSERTAR Y OBTENER ROLES
        # ============================================
        print("📋 Procesando roles...")
        
        roles_data = [
            ('admin', 'Administrador del sistema con acceso total'),
            ('teacher', 'Profesor que puede gestionar cursos y asignaciones'),
            ('student', 'Estudiante que puede inscribirse en cursos'),
            ('administrative', 'Personal administrativo con acceso limitado')
        ]
        
        roles = {}  # Diccionario para almacenar role_id por nombre
        
        for role_name, role_desc in roles_data:
            try:
                # Verificar si el rol existe
                cursor.execute("SELECT id FROM roles WHERE name = %s", (role_name,))
                existing_role = cursor.fetchone()
                
                if existing_role:
                    # Rol existe, usar su ID
                    roles[role_name] = existing_role['id']
                    print(f"  ✓ Rol '{role_name}' ya existe (ID: {existing_role['id']})")
                else:
                    # Insertar nuevo rol
                    cursor.execute(
                        "INSERT INTO roles (name, description) VALUES (%s, %s)",
                        (role_name, role_desc)
                    )
                    conn.commit()
                    role_id = cursor.lastrowid
                    roles[role_name] = role_id
                    print(f"  ✅ Rol '{role_name}' creado (ID: {role_id})")
            
            except Exception as e:
                print(f"  ❌ Error con rol '{role_name}': {str(e)}")
                conn.rollback()
                raise
        
        # Verificar que tenemos todos los roles
        if len(roles) != 4:
            raise Exception(f"Error: Solo se crearon {len(roles)} de 4 roles necesarios")
        
        print(f"  ✅ Total: {len(roles)} roles procesados\n")
        
        # ============================================
        # 2. INSERTAR Y OBTENER USUARIOS
        # ============================================
        print("👥 Procesando usuarios...")
        
        users_data = [
            ('admin', 'admin@academic.com', 'Admin123!', 'admin'),
            ('teacher1', 'teacher1@academic.com', 'Teacher123!', 'teacher'),
            ('teacher2', 'teacher2@academic.com', 'Teacher123!', 'teacher'),
            ('student1', 'student1@academic.com', 'Student123!', 'student'),
            ('student2', 'student2@academic.com', 'Student123!', 'student'),
            ('student3', 'student3@academic.com', 'Student123!', 'student'),
            ('admin_staff', 'admin.staff@academic.com', 'Admin123!', 'administrative')
        ]
        
        users = {}  # Diccionario para almacenar user_id por username
        
        for username, email, password, role_name in users_data:
            try:
                # Verificar si el usuario existe
                cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
                existing_user = cursor.fetchone()
                
                if existing_user:
                    users[username] = existing_user['id']
                    print(f"  ✓ Usuario '{username}' ya existe (ID: {existing_user['id']})")
                else:
                    # Hashear contraseña
                    password_hash = hash_password(password)
                    role_id = roles[role_name]
                    
                    # Insertar nuevo usuario
                    cursor.execute(
                        """INSERT INTO users (username, email, password_hash, role_id)
                           VALUES (%s, %s, %s, %s)""",
                        (username, email, password_hash, role_id)
                    )
                    conn.commit()
                    user_id = cursor.lastrowid
                    users[username] = user_id
                    print(f"  ✅ Usuario '{username}' creado (ID: {user_id})")
            
            except Exception as e:
                print(f"  ❌ Error con usuario '{username}': {str(e)}")
                conn.rollback()
                raise
        
        print(f"  ✅ Total: {len(users)} usuarios procesados\n")
        
        # ============================================
        # 3. INSERTAR Y OBTENER CURSOS
        # ============================================
        print("📚 Procesando cursos...")
        
        courses_data = [
            ('Matemáticas Avanzadas', 'Cálculo diferencial e integral', 'MATH301', 'teacher1'),
            ('Programación Web', 'Desarrollo de aplicaciones web modernas', 'CS201', 'teacher1'),
            ('Base de Datos', 'Diseño e implementación de bases de datos', 'CS301', 'teacher2'),
            ('Física General', 'Mecánica clásica y termodinámica', 'PHYS101', 'teacher2')
        ]
        
        courses = {}  # Diccionario para almacenar course_id por code
        
        for name, description, code, teacher_username in courses_data:
            try:
                # Verificar si el curso existe
                cursor.execute("SELECT id FROM courses WHERE code = %s", (code,))
                existing_course = cursor.fetchone()
                
                if existing_course:
                    courses[code] = existing_course['id']
                    print(f"  ✓ Curso '{code}' ya existe (ID: {existing_course['id']})")
                else:
                    teacher_id = users[teacher_username]
                    
                    # Insertar nuevo curso
                    cursor.execute(
                        """INSERT INTO courses (name, description, code, teacher_id)
                           VALUES (%s, %s, %s, %s)""",
                        (name, description, code, teacher_id)
                    )
                    conn.commit()
                    course_id = cursor.lastrowid
                    courses[code] = course_id
                    print(f"  ✅ Curso '{code}' creado (ID: {course_id})")
            
            except Exception as e:
                print(f"  ❌ Error con curso '{code}': {str(e)}")
                conn.rollback()
                raise
        
        print(f"  ✅ Total: {len(courses)} cursos procesados\n")
        
        # ============================================
        # 4. INSERTAR ASIGNACIONES
        # ============================================
        print("📝 Procesando asignaciones...")
        
        due_date_1 = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')
        due_date_2 = (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d %H:%M:%S')
        
        assignments_data = [
            ('Tarea 1: Derivadas', 'Resolver ejercicios de derivadas parciales', 
             'MATH301', due_date_1, 100.00),
            ('Proyecto Final: Calculadora', 'Implementar calculadora científica', 
             'MATH301', due_date_2, 150.00),
            ('Lab 1: HTML y CSS', 'Crear página web responsive', 
             'CS201', due_date_1, 80.00),
            ('Proyecto: Sistema CRUD', 'Desarrollar aplicación web completa', 
             'CS201', due_date_2, 200.00),
            ('Tarea 1: Normalización', 'Ejercicios de formas normales', 
             'CS301', due_date_1, 100.00),
            ('Examen: Cinemática', 'Examen de movimiento rectilíneo', 
             'PHYS101', due_date_1, 120.00)
        ]
        
        assignment_count = 0
        
        for title, description, course_code, due_date, max_score in assignments_data:
            try:
                # Verificar si la asignación ya existe (por título y curso)
                course_id = courses[course_code]
                cursor.execute(
                    "SELECT id FROM assignments WHERE title = %s AND course_id = %s",
                    (title, course_id)
                )
                existing_assignment = cursor.fetchone()
                
                if existing_assignment:
                    print(f"  ✓ Asignación '{title[:30]}...' ya existe")
                else:
                    # Insertar nueva asignación
                    cursor.execute(
                        """INSERT INTO assignments (title, description, course_id, due_date, max_score)
                           VALUES (%s, %s, %s, %s, %s)""",
                        (title, description, course_id, due_date, max_score)
                    )
                    conn.commit()
                    assignment_count += 1
                    print(f"  ✅ Asignación '{title[:30]}...' creada")
            
            except Exception as e:
                print(f"  ❌ Error con asignación '{title}': {str(e)}")
                conn.rollback()
                raise
        
        print(f"  ✅ Total: {assignment_count} nuevas asignaciones creadas\n")
        
        # ============================================
        # 5. INSERTAR INSCRIPCIONES
        # ============================================
        print("🎓 Procesando inscripciones...")
        
        enrollments_data = [
            ('student1', 'MATH301'),
            ('student1', 'CS201'),
            ('student2', 'CS201'),
            ('student2', 'CS301'),
            ('student3', 'PHYS101'),
            ('student3', 'MATH301')
        ]
        
        enrollment_count = 0
        
        for student_username, course_code in enrollments_data:
            try:
                student_id = users[student_username]
                course_id = courses[course_code]
                
                # Verificar si ya está inscrito
                cursor.execute(
                    "SELECT id FROM enrollments WHERE student_id = %s AND course_id = %s",
                    (student_id, course_id)
                )
                existing_enrollment = cursor.fetchone()
                
                if existing_enrollment:
                    print(f"  ✓ {student_username} ya inscrito en {course_code}")
                else:
                    # Insertar nueva inscripción
                    cursor.execute(
                        "INSERT INTO enrollments (student_id, course_id) VALUES (%s, %s)",
                        (student_id, course_id)
                    )
                    conn.commit()
                    enrollment_count += 1
                    print(f"  ✅ {student_username} inscrito en {course_code}")
            
            except Exception as e:
                print(f"  ❌ Error con inscripción {student_username}/{course_code}: {str(e)}")
                conn.rollback()
                raise
        
        print(f"  ✅ Total: {enrollment_count} nuevas inscripciones creadas\n")
        
        # ============================================
        # RESUMEN FINAL
        # ============================================
        print("\n" + "=" * 60)
        print("✨ ¡Datos de prueba cargados exitosamente!")
        print("=" * 60)
        
        # Contar totales actuales en la BD
        cursor.execute("SELECT COUNT(*) as total FROM roles")
        total_roles = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM users")
        total_users = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM courses")
        total_courses = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM assignments")
        total_assignments = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as total FROM enrollments")
        total_enrollments = cursor.fetchone()['total']
        
        print("\n📊 Estado actual de la base de datos:")
        print(f"  • {total_roles} roles")
        print(f"  • {total_users} usuarios")
        print(f"  • {total_courses} cursos")
        print(f"  • {total_assignments} asignaciones")
        print(f"  • {total_enrollments} inscripciones")
        
        print("\n🔐 Credenciales de prueba:")
        print("-" * 60)
        print("  Admin:    admin / Admin123!")
        print("  Teacher:  teacher1 / Teacher123!")
        print("  Student:  student1 / Student123!")
        print("  Staff:    admin_staff / Admin123!")
        print("-" * 60)
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Error al insertar datos: {str(e)}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    print("=" * 60)
    print("  Carga de Datos de Prueba")
    print("=" * 60 + "\n")
    
    try:
        seed_data()
        print("\n✅ Proceso completado exitosamente\n")
    except Exception as e:
        print(f"\n❌ Error fatal: {str(e)}")
        print("\n💡 Sugerencias:")
        print("  1. Verifica que la base de datos existe")
        print("  2. Verifica las credenciales en .env")
        print("  3. Ejecuta primero: python scripts/init_db.py")
        print("  4. Revisa el error detallado arriba\n")
        sys.exit(1)