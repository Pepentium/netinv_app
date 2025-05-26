from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required
import mysql
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


from flask import request
@inventory_bp.route("/device_list")
@login_required
def device_list():
    page = request.args.get('page', 1, type=int)
    per_page = 10

    # Capturar filtros
    building = request.args.get('building', type=str)
    dev_type = request.args.get('type', type=str)
    status = request.args.get('status', type=str)

    # Base de la consulta
    query = (
        db.session.query(
            Device,
            Location.loc_building_name,
            Location.loc_detail,
            Rack.rck_name,
            Model.mdl_name,
            Model.mdl_manufacturer,
        )
        .join(Rack, Device.rck_id == Rack.rck_id)
        .join(Location, Rack.loc_id == Location.loc_id)
        .join(Model, Device.mdl_id == Model.mdl_id)
    )

    # Aplicar filtros condicionales
    if building:
        query = query.filter(Location.loc_building_name == building)
    if dev_type:
        query = query.filter(Device.dev_type == dev_type)
    if status:
        query = query.filter(Device.dev_status == status)

    # Orden y paginación
    query = query.order_by(Device.dev_ip_address)
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    # Obtener listas únicas para los filtros dinámicos
    buildings = ["EDIFICIO1", "EDIFICIO2", "EDIFICIO3", "EDIFICIO4", "EDIFICIO5"]
    types = [t[0] for t in db.session.query(Device.dev_type).distinct().order_by(Device.dev_type).all()]
    statuses = [s[0] for s in db.session.query(Device.dev_status).distinct().order_by(Device.dev_status).all()]

    return render_template(
        "inventory/device_list.html",
        devices=pagination.items,
        pagination=pagination,
        buildings=buildings,
        types=types,
        statuses=statuses,
        selected_building=building or '',
        selected_type=dev_type or '',
        selected_status=status or ''
    )

from flask import render_template, request, redirect, url_for, flash
from app import db
from app.models import Location, Rack, Model, Device

@inventory_bp.route("/add_device", methods=["GET", "POST"])
@login_required
def add_device():

    if request.method == "POST":
        try:
            # ===== 1. Procesar ubicación =====
            location = Location(
                loc_building_name=request.form["building_name"],
                loc_detail=request.form["loc_detail"],
            )
            db.session.add(location)
            db.session.flush()  # Para obtener el ID

            # ===== 2. Procesar rack =====
            rack = Rack(rck_name=request.form["rck_name"], loc_id=location.loc_id)
            db.session.add(rack)
            db.session.flush()

            # ===== 3. Procesar modelo =====
            if request.form["model_option"] == "existing":
                model = Model.query.get(request.form["existing_model"])
            else:
                model = Model(
                    mdl_name=request.form["mdl_name"],
                    mdl_manufacturer=request.form["mdl_manufacturer"],
                    mdl_ports=request.form["mdl_ports"],
                    mdl_description=request.form["mdl_description"],
                )
                db.session.add(model)
                db.session.flush()

            # ===== 4. Procesar dispositivo =====
            device = Device(
                dev_ip_address=request.form["dev_ip_address"],
                dev_serial_number=request.form["dev_serial_number"],
                dev_type=request.form["dev_type"],
                mdl_id=model.mdl_id,
                rck_id=rack.rck_id,
            )
            db.session.add(device)

            db.session.commit()

            flash("Dispositivo registrado exitosamente!", "success")
            return redirect(url_for("inventory.device_list"))

        except Exception as e:
            db.session.rollback()
            flash(f"Error al registrar: {str(e)}", "danger")

    # GET request
    available_ips = get_available_ips()
    buildings = ["EDIFICIO1", "EDIFICIO2", "EDIFICIO3", "EDIFICIO4", "EDIFICIO5"]
    existing_models = Model.query.all()

    return render_template(
        "inventory/add_device.html",
        available_ips=available_ips,
        buildings=buildings,
        existing_models=existing_models,
    )


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

@inventory_bp.route("/delete_device/<int:device_id>", methods=["POST"])
@login_required
def delete_device(device_id):
    device = Device.query.get_or_404(device_id)

    try:
        db.session.delete(device)
        db.session.commit()
        flash(f"Dispositivo con IP {device.dev_ip_address} eliminado exitosamente.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"No se pudo eliminar el dispositivo: {str(e)}", "danger")

    return redirect(url_for("inventory.device_list"))
