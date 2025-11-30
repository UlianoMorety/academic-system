"""
Inicialización de la aplicación Flask
"""

from flask import Flask
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app.config import config

def create_app(config_name='default'):
    """
    Factory pattern para crear la aplicación Flask
    
    Args:
        config_name: Nombre de la configuración a usar
        
    Returns:
        Flask app instance
    """
    app = Flask(__name__)
    
    # Cargar configuración
    app.config.from_object(config[config_name])
    
    # Configurar CORS
    CORS(app, origins=config[config_name].CORS_ORIGINS)
    
    # Configurar rate limiting
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://"
    )
    
    # Registrar blueprints
    from app.routes.auth_routes import auth_bp
    from app.routes.user_routes import user_bp
    from app.routes.course_routes import course_bp
    from app.routes.assignment_routes import assignment_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(course_bp)
    app.register_blueprint(assignment_bp)
    
    # Aplicar rate limit específico a rutas de auth
    limiter.limit("5 per minute")(auth_bp)
    
    # Ruta de prueba
    @app.route('/')
    def index():
        return {
            'message': 'Sistema de Gestión Académica API',
            'version': '1.0.0',
            'status': 'running'
        }
    
    # Manejador de errores 404
    @app.errorhandler(404)
    def not_found(error):
        return {
            'success': False,
            'message': 'Endpoint no encontrado'
        }, 404
    
    # Manejador de errores 500
    @app.errorhandler(500)
    def internal_error(error):
        return {
            'success': False,
            'message': 'Error interno del servidor'
        }, 500
    
    # Manejador de rate limit
    @app.errorhandler(429)
    def ratelimit_handler(error):
        return {
            'success': False,
            'message': 'Demasiadas peticiones. Intenta de nuevo más tarde.'
        }, 429
    
    return app