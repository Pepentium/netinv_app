from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import base64
from hashlib import scrypt
from app import db

class User(UserMixin, db.Model):
    __tablename__ = 'tbl_users'
    
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
        if not self.usr_password.startswith('scrypt:'):
            try:
                return check_password_hash(self.usr_password, password)
            except ValueError:
                return False
        
        try:
            # Parsear el hash almacenado
            parts = self.usr_password.split('$')
            if len(parts) != 4:
                return False
                
            # Extraer parámetros
            params = parts[1].split(':')
            n = int(params[0])
            r = int(params[1])
            p = int(params[2])
            salt = base64.b64decode(parts[2] + '=' * (4 - len(parts[2]) % 4))
            stored_key = base64.b64decode(parts[3] + '=' * (4 - len(parts[3]) % 4))
            
            # Generar hash con la contraseña proporcionada
            new_key = scrypt(
                password=password.encode('utf-8'),
                salt=salt,
                n=n,
                r=r,
                p=p,
                dklen=len(stored_key)
            )
            
            return new_key == stored_key
            
        except Exception as e:
            print(f"Error en verificación: {str(e)}")
            return False

class Location(db.Model):
    __tablename__ = 'tbl_locations'
    
    loc_id = db.Column('loc_id', db.Integer, primary_key=True)
    loc_building_name = db.Column('loc_building_name', db.String(100), nullable=False)
    loc_detail = db.Column('loc_detail', db.String(100), nullable=False)

class Rack(db.Model):
    __tablename__ = 'tbl_racks'
    
    rck_id = db.Column('rck_id', db.Integer, primary_key=True)
    rck_name = db.Column('rck_name', db.String(50), nullable=False)
    loc_id = db.Column('loc_id', db.Integer, db.ForeignKey('tbl_locations.loc_id'))
    
    location = db.relationship('Location', backref='racks')

class Model(db.Model):
    __tablename__ = 'tbl_models'
    
    mdl_id = db.Column('mdl_id', db.Integer, primary_key=True)
    mdl_name = db.Column('mdl_name', db.String(100), nullable=False)
    mdl_manufacturer = db.Column('mdl_manufacturer', db.String(100))
    mdl_ports = db.Column('mdl_ports', db.Integer)
    mdl_description = db.Column('mdl_description', db.Text)

from sqlalchemy.ext.hybrid import hybrid_property

class Device(db.Model):
    __tablename__ = 'tbl_devices'
    
    dev_id = db.Column('dev_id', db.Integer, primary_key=True)
    dev_ip_address = db.Column('dev_ip_address', db.String(45), nullable=False, unique=True)
    dev_serial_number = db.Column('dev_serial_number', db.String(100), nullable=False)
    dev_type = db.Column('dev_type', db.Enum('switch', 'router', 'firewall', 'AP', 'server', 'other'), nullable=False)
    mdl_id = db.Column('mdl_id', db.Integer, db.ForeignKey('tbl_models.mdl_id'), nullable=False)
    rck_id = db.Column('rck_id', db.Integer, db.ForeignKey('tbl_racks.rck_id'), nullable=False)
    dev_status = db.Column('dev_status', db.Enum('activo', 'inactivo', 'mantenimiento'), default='activo')

    # Relaciones
    model = db.relationship('Model', backref='devices')
    rack = db.relationship('Rack', backref='devices')

    # Propiedades para acceder a campos relacionados
    @hybrid_property
    def mdl_name(self):
        return self.model.mdl_name if self.model else None

    @hybrid_property
    def mdl_manufacturer(self):
        return self.model.mdl_manufacturer if self.model else None

    @hybrid_property
    def mdl_ports(self):
        return self.model.mdl_ports if self.model else None

    @hybrid_property
    def mdl_description(self):
        return self.model.mdl_description if self.model else None

    @hybrid_property
    def rck_name(self):
        return self.rack.rck_name if self.rack else None

    @hybrid_property
    def loc_building_name(self):
        return self.rack.location.loc_building_name if self.rack and self.rack.location else None

    @hybrid_property
    def loc_detail(self):
        return self.rack.location.loc_detail if self.rack and self.rack.location else None
