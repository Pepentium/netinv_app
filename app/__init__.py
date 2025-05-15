import os
import sys
from flask import Flask

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()


def resource_path(relative_path):
    """Obtiene la ruta absoluta en desarrollo o cuando está empaquetado con PyInstaller"""
    try:
        base_path = sys._MEIPASS  # directorio temporal de PyInstaller
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def create_app():
    # Obtén rutas correctas para templates y static
    template_dir = resource_path(os.path.join("app", "templates"))
    static_dir = resource_path(os.path.join("app", "static"))

    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

    # Configuración
    app.config.from_object("app.config.Config")

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = (
        "🔐 Por favor inicia sesión para acceder a esta página."
    )

    from app.auth.routes import auth_bp
    from app.inventory.routes import inventory_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(inventory_bp)

    return app
