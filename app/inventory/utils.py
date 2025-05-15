from app import db
from app.models import Device

def is_ip_available(ip_address):
    existing_device = Device.query.filter_by(dev_ip_address=ip_address).first()
    return existing_device is None

def get_devices_summary():
    from app.models import Device, Model, Rack
    
    summary = {
        'total_devices': Device.query.count(),
        'by_status': db.session.query(
            Device.dev_status,
            db.func.count(Device.dev_id)
        ).group_by(Device.dev_status).all(),
        'by_type': db.session.query(
            Device.dev_type,
            db.func.count(Device.dev_id)
        ).group_by(Device.dev_type).all(),
        'by_rack': db.session.query(
            Rack.rck_name,
            db.func.count(Device.dev_id)
        ).join(Device).group_by(Rack.rck_name).all()
    }
    
    return summary


def get_devices_chart_data():
    from app.models import Device, Rack

    # Agrupar por Rack y Estado
    devices_by_rack_status = db.session.query(
        Rack.rck_name,
        Device.dev_status,
        db.func.count(Device.dev_id)
    ).join(Device).group_by(Rack.rck_name, Device.dev_status).all()

    # Reestructurar datos para el gráfico
    data = {}
    statuses = set()

    for rack_name, status, count in devices_by_rack_status:
        statuses.add(status)
        if rack_name not in data:
            data[rack_name] = {}
        data[rack_name][status] = count

    # Asegurar que todos los racks tengan todas las categorías
    labels = sorted(data.keys())
    status_list = sorted(statuses)

    datasets = []
    for status in status_list:
        dataset_data = [data.get(rack, {}).get(status, 0) for rack in labels]
        datasets.append({
            'label': status.capitalize(),
            'data': dataset_data
        })

    return {
        'chart_id': 'overviewChart',
        'labels': labels,
        'datasets': datasets
    }
