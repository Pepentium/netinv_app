from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, validators

class DeviceForm(FlaskForm):
    ip_address = SelectField('IP Address', choices=[])  # Se llena dinámicamente
    serial_number = StringField('Serial', validators=[validators.DataRequired()])
    building = StringField('Edificio', validators=[validators.DataRequired()])
    rack = StringField('Rack', validators=[validators.DataRequired()])
    model = StringField('Modelo', validators=[validators.DataRequired()])