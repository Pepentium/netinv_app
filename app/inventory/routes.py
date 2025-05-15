from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required
from app.models import Device, Rack, Location, Model
from app.inventory.utils import (
    is_ip_available,
    get_devices_summary,
    get_devices_chart_data,
)
from app import db
from ipaddress import IPv4Network
from app.inventory.forms import DeviceForm

inventory_bp = Blueprint("inventory", __name__)


# --- Rutas existentes ---
@inventory_bp.route("/")
@inventory_bp.route("/dashboard")
@login_required
def dashboard():
    summary = get_devices_summary()
    chart_overview = get_devices_chart_data()
    return render_template(
        "inventory/dashboard.html", summary=summary, chart_overview=chart_overview
    )


@inventory_bp.route("/devices")
@login_required
def devices():
    devices = Device.query.all()

    table_headers = [
        "IP",
        "Serial",
        "Tipo",
        "Estado",
        "Modelo",
        "Fabricante",
        "Puertos",
        "Descripción",
        "Rack",
        "Edificio",
        "Detalle",
    ]

    return render_template(
        "inventory/devices.html", devices=devices, table_headers=table_headers
    )


@inventory_bp.route("/ip-check", methods=["GET", "POST"])
@login_required
def ip_check():
    form = DeviceForm()

    form.ip_address.choices = [(ip, ip) for ip in get_available_ips()]
    form.building.choices = [
        (loc.loc_id, loc.loc_building_name) for loc in Location.query.all()
    ]
    form.rack.choices = [(rack.rck_id, rack.rck_name) for rack in Rack.query.all()]
    form.model.choices = [(model.mdl_id, model.mdl_name) for model in Model.query.all()]

    if form.validate_on_submit():
        if not is_ip_available(form.ip_address.data):
            flash(f"La IP {form.ip_address.data} ya está en uso", "error")
        else:
            device = Device(
                dev_ip_address=form.ip_address.data,
                dev_serial_number=form.serial_number.data,
                dev_type=form.device_type.data,
                mdl_id=form.model.data,
                rck_id=form.rack.data,
            )
            db.session.add(device)
            db.session.commit()
            flash("Dispositivo registrado con éxito", "success")
            return redirect(url_for("inventory.ip_check"))

    return render_template("inventory/ip_manager.html", form=form)


# --- Nueva funcionalidad ---
def get_available_ips():
    """Obtiene todas las IPs disponibles en el rango 192.168.20.0/24"""
    used_ips = {device.dev_ip_address for device in Device.query.all()}
    network = IPv4Network("192.168.20.0/24")

    return [
        str(host)
        for host in network.hosts()
        if str(host) not in used_ips
        and str(host) != "192.168.20.1"  # Excluye la IP gateway
    ]
