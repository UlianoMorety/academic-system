"""
Script para limpiar completamente la base de datos
USAR CON PRECAUCIÓN - Elimina todos los datos
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import get_db_connection

def confirm_reset():
    """Solicita confirmación del usuario"""
    print("\n⚠️  ADVERTENCIA: Este script eliminará TODOS los datos de la base de datos")
    print("=" * 70)
    response = input("\n¿Estás seguro de que quieres continuar? (escribe 'SI' para confirmar): ")
    return response.strip().upper() == 'SI'

def reset_database():
    """Elimina todos los datos de las tablas manteniendo la estructura"""
    
    if not confirm_reset():
        print("\n❌ Operación cancelada por el usuario")
        return False
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        print("\n🗑️  Limpiando base de datos...")
        
        # Desactivar foreign key checks temporalmente
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        
        # Eliminar datos de todas las tablas (en orden inverso de dependencias)
        tables = ['enrollments', 'assignments', 'courses', 'users', 'roles']
        
        for table in tables:
            cursor.execute(f"DELETE FROM {table}")
            affected = cursor.rowcount
            print(f"  ✅ Tabla '{table}': {affected} registros eliminados")
        
        # Resetear auto_increment de todas las tablas
        for table in tables:
            cursor.execute(f"ALTER TABLE {table} AUTO_INCREMENT = 1")
        
        # Reactivar foreign key checks
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        
        conn.commit()
        
        print("\n✨ Base de datos limpiada exitosamente")
        print("\n💡 Próximo paso: python scripts/seed_data.py")
        
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Error al limpiar base de datos: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    print("=" * 70)
    print("  Script de Limpieza de Base de Datos")
    print("=" * 70)
    
    success = reset_database()
    
    if success:
        print("\n✅ Proceso completado\n")
        sys.exit(0)
    else:
        print("\n❌ Proceso fallido\n")
        sys.exit(1)