"""
Script para inicializar la base de datos
Crea todas las tablas necesarias para el sistema
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import get_db_connection

def create_tables():
    """Crea todas las tablas del sistema"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        print("🗄️  Creando tablas...")
        
        # Tabla roles
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS roles (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(50) NOT NULL UNIQUE,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_name (name)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """)
        print("✅ Tabla 'roles' creada")
        
        # Tabla users
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE,
            email VARCHAR(100) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            role_id INT NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE RESTRICT,
            INDEX idx_username (username),
            INDEX idx_email (email),
            INDEX idx_role (role_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """)
        print("✅ Tabla 'users' creada")
        
        # Tabla courses
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            description TEXT,
            code VARCHAR(20) NOT NULL UNIQUE,
            teacher_id INT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (teacher_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_code (code),
            INDEX idx_teacher (teacher_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """)
        print("✅ Tabla 'courses' creada")
        
        # Tabla assignments
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS assignments (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            description TEXT,
            course_id INT NOT NULL,
            due_date DATETIME,
            max_score DECIMAL(5,2) DEFAULT 100.00,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
            INDEX idx_course (course_id),
            INDEX idx_due_date (due_date)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """)
        print("✅ Tabla 'assignments' creada")
        
        # Tabla enrollments
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS enrollments (
            id INT AUTO_INCREMENT PRIMARY KEY,
            student_id INT NOT NULL,
            course_id INT NOT NULL,
            enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
            UNIQUE KEY unique_enrollment (student_id, course_id),
            INDEX idx_student (student_id),
            INDEX idx_course (course_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """)
        print("✅ Tabla 'enrollments' creada")
        
        conn.commit()
        print("\n✨ ¡Base de datos inicializada exitosamente!")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Error al crear tablas: {str(e)}")
        raise
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    print("=" * 50)
    print("  Inicialización de Base de Datos")
    print("=" * 50)
    create_tables()