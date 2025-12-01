"""
Script de diagnóstico para verificar el estado de la base de datos
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import get_db_connection

def check_database():
    """Verifica el estado de la base de datos"""
    
    print("=" * 70)
    print("  Diagnóstico de Base de Datos")
    print("=" * 70 + "\n")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        print("✅ Conexión a base de datos: OK\n")
        
        # Verificar que las tablas existen
        print("📋 Verificando tablas...")
        tables = ['roles', 'users', 'courses', 'assignments', 'enrollments']
        tables_ok = True
        
        for table in tables:
            try:
                cursor.execute(f"SHOW TABLES LIKE '{table}'")
                result = cursor.fetchone()
                if result:
                    print(f"  ✅ Tabla '{table}' existe")
                else:
                    print(f"  ❌ Tabla '{table}' NO EXISTE")
                    tables_ok = False
            except Exception as e:
                print(f"  ❌ Error verificando tabla '{table}': {str(e)}")
                tables_ok = False
        
        if not tables_ok:
            print("\n❌ Faltan tablas. Ejecuta: python scripts/init_db.py")
            return False
        
        print("\n✅ Todas las tablas existen\n")
        
        # Contar registros en cada tabla
        print("📊 Contando registros...")
        
        counts = {}
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) as total FROM {table}")
            count = cursor.fetchone()['total']
            counts[table] = count
            print(f"  • {table}: {count} registros")
        
        # Verificar roles específicos
        print("\n🔍 Verificando roles...")
        expected_roles = ['admin', 'teacher', 'student', 'administrative']
        cursor.execute("SELECT name FROM roles")
        existing_roles = [row['name'] for row in cursor.fetchall()]
        
        for role in expected_roles:
            if role in existing_roles:
                print(f"  ✅ Rol '{role}' existe")
            else:
                print(f"  ❌ Rol '{role}' NO EXISTE")
        
        # Verificar usuarios de prueba
        print("\n👥 Verificando usuarios de prueba...")
        test_users = ['admin', 'teacher1', 'student1', 'admin_staff']
        cursor.execute("SELECT username FROM users")
        existing_users = [row['username'] for row in cursor.fetchall()]
        
        for user in test_users:
            if user in existing_users:
                print(f"  ✅ Usuario '{user}' existe")
            else:
                print(f"  ⚠️  Usuario '{user}' NO EXISTE")
        
        # Verificar integridad referencial
        print("\n🔗 Verificando integridad referencial...")
        
        # Usuarios con roles válidos
        cursor.execute("""
            SELECT COUNT(*) as total FROM users u
            LEFT JOIN roles r ON u.role_id = r.id
            WHERE r.id IS NULL
        """)
        orphan_users = cursor.fetchone()['total']
        
        if orphan_users == 0:
            print(f"  ✅ Todos los usuarios tienen rol válido")
        else:
            print(f"  ❌ {orphan_users} usuarios sin rol válido")
        
        # Cursos con profesores válidos
        cursor.execute("""
            SELECT COUNT(*) as total FROM courses c
            LEFT JOIN users u ON c.teacher_id = u.id
            WHERE u.id IS NULL
        """)
        orphan_courses = cursor.fetchone()['total']
        
        if orphan_courses == 0:
            print(f"  ✅ Todos los cursos tienen profesor válido")
        else:
            print(f"  ❌ {orphan_courses} cursos sin profesor válido")
        
        # Asignaciones con cursos válidos
        cursor.execute("""
            SELECT COUNT(*) as total FROM assignments a
            LEFT JOIN courses c ON a.course_id = c.id
            WHERE c.id IS NULL
        """)
        orphan_assignments = cursor.fetchone()['total']
        
        if orphan_assignments == 0:
            print(f"  ✅ Todas las asignaciones tienen curso válido")
        else:
            print(f"  ❌ {orphan_assignments} asignaciones sin curso válido")
        
        # Resumen final
        print("\n" + "=" * 70)
        
        all_ok = (tables_ok and 
                  len(existing_roles) == 4 and 
                  orphan_users == 0 and 
                  orphan_courses == 0 and 
                  orphan_assignments == 0)
        
        if all_ok:
            print("✅ BASE DE DATOS EN BUEN ESTADO")
            
            if counts['users'] == 0:
                print("\n💡 Sugerencia: Ejecuta 'python scripts/seed_data.py' para cargar datos de prueba")
        else:
            print("⚠️  SE ENCONTRARON PROBLEMAS")
            print("\n💡 Sugerencias:")
            if not tables_ok:
                print("  1. Ejecuta: python scripts/init_db.py")
            if counts['users'] == 0:
                print("  2. Ejecuta: python scripts/seed_data.py")
        
        print("=" * 70 + "\n")
        
        cursor.close()
        conn.close()
        
        return all_ok
        
    except Exception as e:
        print(f"\n❌ Error al verificar base de datos: {str(e)}")
        import traceback
        traceback.print_exc()
        
        print("\n💡 Verifica:")
        print("  1. MySQL está corriendo")
        print("  2. Credenciales en .env son correctas")
        print("  3. Base de datos 'academic_system' existe")
        print()
        
        return False

if __name__ == '__main__':
    success = check_database()
    sys.exit(0 if success else 1)