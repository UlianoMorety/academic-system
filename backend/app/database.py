"""
Módulo de conexión a la base de datos MySQL
Utiliza PyMySQL con consultas parametrizadas y connection pooling
"""

import pymysql
from pymysql.cursors import DictCursor
from contextlib import contextmanager
from app.config import Config
import threading

# Pool de conexiones simple
class ConnectionPool:
    def __init__(self, max_connections=10):
        self.max_connections = max_connections
        self.connections = []
        self.lock = threading.Lock()
    
    def get_connection(self):
        with self.lock:
            # Reutilizar conexión existente
            if self.connections:
                conn = self.connections.pop()
                # Verificar si está viva
                try:
                    conn.ping(reconnect=True)
                    return conn
                except:
                    pass
            
            # Crear nueva conexión
            return pymysql.connect(
                **Config.get_database_uri(),
                cursorclass=DictCursor
            )
    
    def return_connection(self, conn):
        with self.lock:
            if len(self.connections) < self.max_connections:
                try:
                    conn.ping(reconnect=True)
                    self.connections.append(conn)
                except:
                    try:
                        conn.close()
                    except:
                        pass
            else:
                try:
                    conn.close()
                except:
                    pass

# Pool global
_pool = ConnectionPool(max_connections=10)

def get_db_connection():
    """
    Obtiene una conexión del pool
    """
    try:
        return _pool.get_connection()
    except pymysql.Error as e:
        raise Exception(f"Error al conectar a la base de datos: {str(e)}")

@contextmanager
def get_db():
    """
    Context manager para manejar conexiones de BD con pool
    Uso: with get_db() as (conn, cursor): ...
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        yield conn, cursor
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        _pool.return_connection(conn)

def execute_query(query, params=None, fetch_one=False, fetch_all=True):
    """
    Ejecuta una consulta SQL de forma segura
    
    Args:
        query: Query SQL con placeholders %s
        params: Tupla o lista de parámetros
        fetch_one: Si es True, retorna solo un resultado
        fetch_all: Si es True, retorna todos los resultados
        
    Returns:
        Resultado de la consulta o None
    """
    with get_db() as (conn, cursor):
        cursor.execute(query, params or ())
        
        if fetch_one:
            return cursor.fetchone()
        elif fetch_all:
            return cursor.fetchall()
        else:
            return cursor.lastrowid

def execute_many(query, params_list):
    """
    Ejecuta múltiples inserts/updates de forma eficiente
    
    Args:
        query: Query SQL con placeholders
        params_list: Lista de tuplas de parámetros
        
    Returns:
        Número de filas afectadas
    """
    with get_db() as (conn, cursor):
        cursor.executemany(query, params_list)
        return cursor.rowcount