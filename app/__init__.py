from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Crear instancias de extensiones primero
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    
    # Configuración
    app.config.from_object('app.config.Config')
    
    # Inicializar extensiones con la app
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    # Importar blueprints aquí para evitar importaciones circulares
    from app.auth.routes import auth_bp
    from app.inventory.routes import inventory_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(inventory_bp)
    
    return app