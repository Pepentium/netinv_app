from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required
from app.models import Device, Rack, Location, Model
from app.inventory.utils import is_ip_available, get_devices_summary
from app import db
from ipaddress import IPv4Network
from app.inventory.forms import DeviceForm

inventory_bp = Blueprint('inventory', __name__)

# --- Rutas existentes ---
@inventory_bp.route('/')
@inventory_bp.route('/dashboard')
@login_required
def dashboard():
    summary = get_devices_summary()
    return render_template('inventory/dashboard.html', summary=summary)

@inventory_bp.route('/devices')
@login_required
def devices():
    devices = Device.query.all()
    return render_template('inventory/devices.html', devices=devices)

@inventory_bp.route('/ip-check', methods=['GET', 'POST'])
@login_required
def ip_check():
    form = DeviceForm()
    form.ip_address.choices = [(ip, ip) for ip in get_available_ips()]
    
    if form.validate_on_submit():
        ip_address = form.ip_address.data
        if is_ip_available(ip_address):
            flash(f'La IP {ip_address} está disponible', 'success')
        else:
            flash(f'La IP {ip_address} ya está en uso', 'error')
    
    return render_template('inventory/ip_manager.html', form=form)

# --- Nueva funcionalidad ---
def get_available_ips():
    """Obtiene todas las IPs disponibles en el rango 192.168.20.0/24"""
    used_ips = {device.dev_ip_address for device in Device.query.all()}
    network = IPv4Network('192.168.20.0/24')
    
    return [
        str(host) for host in network.hosts() 
        if str(host) not in used_ips 
        and str(host) != '192.168.20.1'  # Excluye la IP gateway
    ]

@inventory_bp.route('/add-device', methods=['GET', 'POST'])
@login_required
def add_device():
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            building = request.form.get('building')
            rack = request.form.get('rack')
            model_name = request.form.get('model')
            ip_address = request.form.get('ip_address')
            serial_number = request.form.get('serial_number')
            
            # Validar IP disponible
            if not is_ip_available(ip_address):
                flash('La IP seleccionada ya está en uso', 'danger')
                return redirect(url_for('inventory.add_device'))

            # 1. Insertar ubicación
            new_location = Location(
                loc_building_name=building,
                loc_detail='Detalle del edificio'
            )
            db.session.add(new_location)
            db.session.flush()  # Para obtener el ID

            # 2. Insertar rack
            new_rack = Rack(
                rck_name=rack,
                loc_id=new_location.loc_id
            )
            db.session.add(new_rack)
            db.session.flush()

            # 3. Insertar o recuperar modelo
            model = Model.query.filter_by(mdl_name=model_name).first()
            if not model:
                model = Model(
                    mdl_name=model_name,
                    mdl_manufacturer='Cisco',
                    mdl_ports=24,
                    mdl_description=f'Switch {model_name}'
                )
                db.session.add(model)
                db.session.flush()

            # 4. Insertar dispositivo
            new_device = Device(
                dev_ip_address=ip_address,
                dev_serial_number=serial_number,
                dev_type='switch',
                mdl_id=model.mdl_id,
                rck_id=new_rack.rck_id
            )
            db.session.add(new_device)
            
            db.session.commit()
            flash('Dispositivo agregado exitosamente!', 'success')
            return redirect(url_for('inventory.devices'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al agregar dispositivo: {str(e)}', 'error')

    # Para GET: mostrar formulario con IPs disponibles
    available_ips = get_available_ips()
    return render_template(
        'inventory/add_device.html',
        available_ips=available_ips
    )