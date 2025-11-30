"""
Sistema de logging centralizado
"""

import logging
import os
from datetime import datetime
from app.config import Config

def setup_logger(name):
    """
    Configura y retorna un logger
    
    Args:
        name: Nombre del módulo
        
    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    
    # Evitar duplicación de handlers
    if logger.handlers:
        return logger
    
    logger.setLevel(logging.DEBUG if Config.DEBUG else logging.INFO)
    
    # Formato
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    )
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler para archivo (solo en producción)
    if not Config.DEBUG:
        # Crear directorio de logs si no existe
        log_dir = 'logs'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Archivo con fecha
        log_file = os.path.join(
            log_dir, 
            f'app_{datetime.now().strftime("%Y%m%d")}.log'
        )
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

# Logger global
app_logger = setup_logger('academic_system')