from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, IPAddress
from app.models import Location, Rack, Model


class DeviceForm(FlaskForm):
    ip_address = SelectField("Dirección IP Disponible", validators=[DataRequired()])
    serial_number = StringField("Número de Serie", validators=[DataRequired()])
    building = StringField("Edificio", validators=[DataRequired()])
    rack = SelectField("Rack", validators=[DataRequired()])
    model = SelectField("Modelo", validators=[DataRequired()])
    manufacturer = StringField("Fabricante", validators=[DataRequired()])
    ports = StringField("Cantidad de Puertos", validators=[DataRequired()])
    description = StringField("Descripción", validators=[DataRequired()])
    device_type = SelectField(
        "Tipo de Dispositivo",
        choices=[
            ("switch", "Switch"),
            ("router", "Router"),
            ("firewall", "Firewall"),
            ("AP", "Access Point"),
            ("server", "Servidor"),
            ("other", "Otro"),
        ],
        validators=[DataRequired()],
    )
    submit = SubmitField("Guardar")
