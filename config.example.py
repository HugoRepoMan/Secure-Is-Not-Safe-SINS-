# Archivo de Configuración de Ejemplo
# Copiar este archivo como config.py en cada directorio de detectores

# =============================================================================
# CONFIGURACIÓN DE BASE DE DATOS
# =============================================================================

DB_CONFIG = {
    # Servidor SQL Server
    'server': '127.0.0.1',      # Cambiar a IP remota si es necesario
    'port': 1432,                # Puerto de SQL Server
    
    # Credenciales
    'user': 'sa',
    'password': 'TU_PASSWORD_AQUI',  # ⚠️ CAMBIAR ESTO
    
    # Base de datos
    'database': 'CentralSIEM'
}

# =============================================================================
# CONFIGURACIÓN DE NETWORK IDS
# =============================================================================

NETWORK_IDS = {
    # Interfaz de red a monitorear
    'interface': 'eth0',  # Cambiar según tu sistema: eth0, enp0s3, wlan0, etc.
    
    # Umbrales de detección
    'port_scan_threshold': 10,      # Puertos escaneados para alertar
    'port_scan_window': 10,         # Ventana de tiempo (segundos)
    
    'syn_flood_threshold': 100,     # Paquetes SYN para alertar
    'syn_flood_window': 1,          # Ventana de tiempo (segundos)
    
    'icmp_flood_threshold': 50,     # Paquetes ICMP para alertar
    'icmp_flood_window': 1,         # Ventana de tiempo (segundos)
    
    # Patrones SQL Injection
    'sql_patterns': [
        "' OR '1'='1",
        "' OR 1=1",
        "UNION SELECT",
        "DROP TABLE",
        "'; DROP",
        "admin'--",
        "' AND '1'='1"
    ],
    
    # Patrones XSS
    'xss_patterns': [
        "<script>",
        "javascript:",
        "onerror=",
        "onload=",
        "<iframe"
    ]
}

# =============================================================================
# CONFIGURACIÓN DE SSH BRUTE FORCE MONITOR
# =============================================================================

SSH_MONITOR = {
    # Archivo de log a monitorear
    'log_file': '/var/log/auth.log',  # Fedora/RHEL usa /var/log/secure
    
    # Umbrales de detección
    'failed_login_threshold': 5,    # Intentos fallidos para alertar
    'time_window': 300,             # Ventana de tiempo (segundos)
    
    # Palabras clave en logs
    'failed_keywords': [
        'Failed password',
        'authentication failure',
        'Invalid user'
    ],
    
    'success_keywords': [
        'Accepted password',
        'Accepted publickey'
    ]
}

# =============================================================================
# CONFIGURACIÓN DE HONEYPOT
# =============================================================================

HONEYPOT = {
    # Puertos a abrir (servicios señuelo)
    'ports': {
        2222: 'SSH',
        8080: 'HTTP',
        3306: 'MySQL',
        5432: 'PostgreSQL',
        1433: 'MSSQL',
        21: 'FTP'
    },
    
    # Banners falsos (para simular servicios reales)
    'banners': {
        2222: 'SSH-2.0-OpenSSH_8.0\r\n',
        8080: 'HTTP/1.1 200 OK\r\nServer: Apache/2.4.41\r\n\r\n',
        3306: '5.7.0-Fake-MySQL\x00',
        5432: 'PostgreSQL 12.0\x00',
        1433: 'Microsoft SQL Server 2019\x00',
        21: '220 FTP Server Ready\r\n'
    },
    
    # Host y configuración
    'host': '0.0.0.0',  # Escuchar en todas las interfaces
    'backlog': 5        # Cola de conexiones
}

# =============================================================================
# CONFIGURACIÓN DE ATTACK GENERATOR
# =============================================================================

ATTACK_GENERATOR = {
    # Target (solo para demo)
    'target_ip': '127.0.0.1',  # ⚠️ Solo usar localhost para demo
    
    # Interfaz de red
    'interface': 'eth0',
    
    # Intensidad de ataques
    'port_scan_ports': [21, 22, 23, 25, 80, 443, 3306, 3389, 5432, 8080],
    'syn_flood_count': 200,
    'icmp_flood_count': 100,
    
    # Payloads SQL Injection
    'sql_payloads': [
        "' OR '1'='1",
        "admin'--",
        "' UNION SELECT NULL--"
    ],
    
    # Payloads XSS
    'xss_payloads': [
        "<script>alert('XSS')</script>",
        "javascript:alert('XSS')",
        "<img src=x onerror=alert('XSS')>"
    ],
    
    # SSH brute force
    'ssh_users': ['root', 'admin', 'user'],
    'ssh_attempts': 10
}

# =============================================================================
# CONFIGURACIÓN DE LOGGING
# =============================================================================

LOGGING = {
    # Nivel de log
    'level': 'INFO',  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    
    # Archivos de log
    'network_ids_log': '/var/log/siem/network_ids.log',
    'ssh_monitor_log': '/var/log/siem/ssh_monitor.log',
    'honeypot_log': '/var/log/siem/honeypot.log',
    
    # Formato de log
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'date_format': '%Y-%m-%d %H:%M:%S'
}

# =============================================================================
# NOTAS DE SEGURIDAD
# =============================================================================

"""
⚠️ IMPORTANTE:

1. NUNCA subir este archivo a GitHub con credenciales reales
2. Agregar config.py al .gitignore
3. Cambiar password por defecto 'sa' en producción
4. Usar cifrado SSL/TLS para conexiones de base de datos
5. Restringir acceso por IP al SQL Server
6. No exponer honeypots directamente a Internet sin supervisión
7. Usar el attack generator SOLO en red propia para fines académicos

Para uso académico:
- ✅ Usar en red privada/aislada
- ✅ Documentar todos los ataques de prueba
- ✅ Informar al administrador de red
- ❌ NO usar contra sistemas de terceros
- ❌ NO usar en producción sin medidas de seguridad adicionales
"""
