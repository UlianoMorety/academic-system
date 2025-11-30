"""
Script para ejecutar la aplicación Flask
"""

import os
from app.utils import create_app

# Obtener configuración del entorno
config_name = os.getenv('FLASK_ENV', 'development')

# Crear aplicación
app = create_app(config_name)

if __name__ == '__main__':
    # Configuración de desarrollo
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )