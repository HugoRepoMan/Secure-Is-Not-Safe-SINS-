"""
Configuración de ejemplo para detectores
Copiar a config.py y ajustar valores
"""

# Configuración de base de datos Windows (Sensor)
DB_CONFIG = {
    'server': '10.0.90.66',      
    'port': 1433,
    'user': 'chadi',             
    'password': 'pass',          
    'database': 'SensorDB'
}

# Puertos de honeypots
HONEYPOT_PORTS = {
    2222: 'SSH Honeypot',
    8080: 'HTTP Honeypot',
    3306: 'MySQL Honeypot',
    5432: 'PostgreSQL Honeypot',
    21: 'FTP Honeypot'
}
