import ipaddress
from app.models import Device  # Ajusta según tus modelos

def get_available_ips():
    used_ips = {device.dev_ip_address for device in Device.query.all()}
    network = ipaddress.IPv4Network('192.168.20.0/24')
    
    available_ips = [
        str(host) for host in network.hosts() 
        if str(host) not in used_ips and str(host) != '192.168.20.1'
    ]
    return available_ips