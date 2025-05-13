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