from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired

class DeviceForm(FlaskForm):
    ip_address = SelectField("Dirección IP Disponible", validators=[DataRequired()], coerce=str)
    
    building = SelectField("Edificio", validators=[DataRequired()], coerce=int)  # almacena loc_id
    loc_detail = StringField("Detalle de Ubicación", render_kw={"readonly": True})
    
    rack = SelectField("Rack", validators=[DataRequired()], coerce=int)  # almacena rck_id
    
    model = SelectField("Modelo", validators=[DataRequired()], coerce=int)  # almacena mdl_id
    manufacturer = StringField("Fabricante", render_kw={"readonly": True})
    ports = StringField("Cantidad de Puertos", render_kw={"readonly": True})
    mdl_description = StringField("Detalle del Modelo", render_kw={"readonly": True})
    
    serial_number = StringField("Número de Serie", validators=[DataRequired()])
    
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
