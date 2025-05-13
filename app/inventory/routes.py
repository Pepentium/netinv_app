from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required
from app.models import Device, Rack, Location, Model
from app.inventory.utils import is_ip_available, get_devices_summary
from app import db

inventory_bp = Blueprint('inventory', __name__)

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
    if request.method == 'POST':
        ip_address = request.form.get('ip_address')
        if is_ip_available(ip_address):
            flash(f'La IP {ip_address} está disponible', 'success')
        else:
            flash(f'La IP {ip_address} ya está en uso', 'danger')
    
    return render_template('inventory/ip_manager.html')