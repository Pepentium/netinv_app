from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import base64
from hashlib import scrypt
from app import db


class User(UserMixin, db.Model):
    __tablename__ = "tbl_users"

    usr_id = db.Column(db.Integer, primary_key=True)
    usr_name = db.Column(db.String(50), unique=True, nullable=False)
    usr_password = db.Column(db.String(100), nullable=False)

    # Métodos requeridos por Flask-Login
    def get_id(self):
        """Retorna el ID del usuario como string"""
        return str(self.usr_id)

    @property
    def is_active(self):
        """Todos los usuarios están activos por defecto"""
        return True

    @property
    def is_authenticated(self):
        """El usuario está autenticado si existe en la BD"""
        return True

    @property
    def is_anonymous(self):
        """No es un usuario anónimo"""
        return False

    # Métodos existentes de gestión de contraseñas
    def set_password(self, password):
        """Genera un hash seguro con werkzeug"""
        self.usr_password = generate_password_hash(password)

    def check_password(self, password):
        """Verificación mejorada para hashes scrypt"""
        if not self.usr_password.startswith("scrypt:"):
            try:
                return check_password_hash(self.usr_password, password)
            except ValueError:
                return False

        try:
            # Parsear el hash almacenado
            parts = self.usr_password.split("$")
            if len(parts) != 4:
                return False

            # Extraer parámetros
            params = parts[1].split(":")
            n = int(params[0])
            r = int(params[1])
            p = int(params[2])
            salt = base64.b64decode(parts[2] + "=" * (4 - len(parts[2]) % 4))
            stored_key = base64.b64decode(parts[3] + "=" * (4 - len(parts[3]) % 4))

            # Generar hash con la contraseña proporcionada
            new_key = scrypt(
                password=password.encode("utf-8"),
                salt=salt,
                n=n,
                r=r,
                p=p,
                dklen=len(stored_key),
            )

            return new_key == stored_key

        except Exception as e:
            print(f"Error en verificación: {str(e)}")
            return False


from app import db

class Location(db.Model):
    __tablename__ = 'tbl_locations'
    loc_id = db.Column(db.Integer, primary_key=True)
    loc_building_name = db.Column(db.String(100), nullable=False)
    loc_detail = db.Column(db.String(100), nullable=False)
    racks = db.relationship('Rack', backref='location', lazy=True)

class Rack(db.Model):
    __tablename__ = 'tbl_racks'
    rck_id = db.Column(db.Integer, primary_key=True)
    rck_name = db.Column(db.String(50), nullable=False)
    loc_id = db.Column(db.Integer, db.ForeignKey('tbl_locations.loc_id'), nullable=False)
    devices = db.relationship('Device', backref='rack', lazy=True)

class Model(db.Model):
    __tablename__ = 'tbl_models'
    mdl_id = db.Column(db.Integer, primary_key=True)
    mdl_name = db.Column(db.String(100), nullable=False)
    mdl_manufacturer = db.Column(db.String(100))
    mdl_ports = db.Column(db.Integer)
    mdl_description = db.Column(db.Text)
    devices = db.relationship('Device', backref='model', lazy=True)

class Device(db.Model):
    __tablename__ = 'tbl_devices'
    dev_id = db.Column(db.Integer, primary_key=True)
    dev_ip_address = db.Column(db.String(45), unique=True, nullable=False)
    dev_serial_number = db.Column(db.String(100), nullable=False)
    dev_type = db.Column(
        db.Enum('switch', 'router', 'firewall', 'AP', 'server', 'other', name='device_types'),
        nullable=False
    )
    mdl_id = db.Column(db.Integer, db.ForeignKey('tbl_models.mdl_id'), nullable=False)
    rck_id = db.Column(db.Integer, db.ForeignKey('tbl_racks.rck_id'), nullable=False)
    dev_status = db.Column(
        db.Enum('activo', 'inactivo', 'mantenimiento', name='status_types'),
        default='activo'
    )