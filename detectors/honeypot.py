#!/usr/bin/env python3
"""
Honeypot Simple - Atrae y registra ataques reales
Simula servicios vulnerables para capturar atacantes
"""

import socket
import threading
import pymssql
import datetime
import time

class SimpleHoneypot:
    """
    Honeypot que simula servicios vulnerables para atraer atacantes reales
    """
    
    def __init__(self):
        self.db_config = {
            'server': '127.0.0.1',
            'port': 1432,
            'user': 'sa',
            'password': 'TU_PASSWORD_AQUI',
            'database': 'CentralSIEM'
        }
        
        # Servicios a simular
        self.services = {
            2222: 'SSH Honeypot',
            8080: 'HTTP Honeypot',
            3306: 'MySQL Honeypot',
            5432: 'PostgreSQL Honeypot',
            1433: 'MSSQL Honeypot',
            21: 'FTP Honeypot'
        }
    
def log_attack(self, service, client_ip, client_port, data):
    """Registra ataque en la base de datos"""
    try:
        # Conexión DIRECTA a Windows (NO usar Linked Server)
        conn = pymssql.connect(
            server=self.db_config['server'],  # 10.0.90.66
            port=self.db_config['port'],      # 1433
            user=self.db_config['user'],      # chadi
            password=self.db_config['password'], # pass
            database=self.db_config['database']  # SensorDB
        )
        cursor = conn.cursor()
        
        attack_type = self.classify_attack(service, data)
        severity = self.get_severity(attack_type)
        service_port = [port for port, name in self.services.items() if name == service][0]
        
        query = """
            INSERT INTO Live_Alerts 
            (TipoAtaque, IP_Origen, Severidad, Puerto_Destino, Protocolo, Timestamp)
            VALUES (%s, %s, %s, %s, %s, GETDATE())
        """
        
        cursor.execute(query, (attack_type, client_ip, severity, service_port, 'TCP'))
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"✓ Ataque registrado: {attack_type} desde {client_ip}")
        
    except Exception as e:
        print(f"✗ Error guardando ataque: {e}")
    
    def classify_attack(self, service, data):
        """Clasifica el tipo de ataque basado en el servicio y datos"""
        data_str = str(data).lower()
        
        if 'SSH' in service:
            if 'admin' in data_str or 'root' in data_str:
                return 'SSH Brute Force Attempt'
            return 'SSH Scanning'
        
        elif 'HTTP' in service:
            if '<script' in data_str or 'javascript:' in data_str:
                return 'XSS Attack Attempt'
            elif 'union' in data_str or 'select' in data_str or '1=1' in data_str:
                return 'SQL Injection Attempt'
            elif '../' in data_str or '..\\' in data_str:
                return 'Path Traversal Attempt'
            return 'HTTP Scanning'
        
        elif 'MySQL' in service or 'PostgreSQL' in service or 'MSSQL' in service:
            return 'Database Port Scanning'
        
        elif 'FTP' in service:
            if 'anonymous' in data_str or 'admin' in data_str:
                return 'FTP Brute Force Attempt'
            return 'FTP Scanning'
        
        return f'{service} - Unauthorized Access Attempt'
    
    def get_severity(self, attack_type):
        """Determina severidad del ataque"""
        high_severity = ['SQL Injection', 'XSS Attack', 'Brute Force']
        
        for keyword in high_severity:
            if keyword in attack_type:
                return 'HIGH'
        
        return 'MEDIUM'
    
    def handle_client(self, client_socket, client_address, service):
        """Maneja conexión de cliente (atacante)"""
        client_ip = client_address[0]
        client_port = client_address[1]
        
        print(f"\n⚠️  CONEXIÓN DETECTADA ⚠️")
        print(f"Servicio: {service}")
        print(f"IP Origen: {client_ip}:{client_port}")
        print(f"Timestamp: {datetime.datetime.now()}")
        
        try:
            # Recibir datos del atacante
            client_socket.settimeout(5)
            data = client_socket.recv(4096)
            
            if data:
                print(f"Datos recibidos: {data[:100]}...")
                
                # Registrar ataque
                self.log_attack(service, client_ip, client_port, data)
                
                # Enviar respuesta falsa para parecer real
                if 'SSH' in service:
                    response = b"SSH-2.0-OpenSSH_7.4\r\n"
                elif 'HTTP' in service:
                    response = b"HTTP/1.1 200 OK\r\nServer: Apache/2.4.41\r\n\r\n"
                elif 'MySQL' in service:
                    response = b"\x4a\x00\x00\x00\x0a5.7.33-0ubuntu0.18.04.1\x00"
                elif 'FTP' in service:
                    response = b"220 FTP Server Ready\r\n"
                else:
                    response = b"Service Ready\r\n"
                
                client_socket.send(response)
        
        except socket.timeout:
            print("Timeout - conexión cerrada")
        except Exception as e:
            print(f"Error manejando cliente: {e}")
        finally:
            client_socket.close()
            print("-" * 50)
    
    def start_service(self, port, service_name):
        """Inicia un servicio honeypot en un puerto"""
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind(('0.0.0.0', port))
            server.listen(5)
            
            print(f"✓ {service_name} escuchando en puerto {port}")
            
            while True:
                client_socket, client_address = server.accept()
                
                # Manejar cada conexión en un thread separado
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, client_address, service_name)
                )
                client_thread.daemon = True
                client_thread.start()
        
        except Exception as e:
            print(f"✗ Error en {service_name}: {e}")
    
    def start_all(self):
        """Inicia todos los servicios honeypot"""
        print("\n🍯 HONEYPOT - Sistema de Captura de Ataques Reales")
        print("=" * 60)
        print("Los siguientes servicios están simulados para atraer atacantes:")
        print()
        
        threads = []
        for port, service in self.services.items():
            thread = threading.Thread(
                target=self.start_service,
                args=(port, service)
            )
            thread.daemon = True
            thread.start()
            threads.append(thread)
            time.sleep(0.1)
        
        print()
        print("=" * 60)
        print("✓ Todos los honeypots activos")
        print("⚠️  ADVERTENCIA: Estos son señuelos para capturar atacantes")
        print("Presiona Ctrl+C para detener")
        print("=" * 60)
        print()
        
        try:
            # Mantener el programa corriendo
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n✓ Honeypot detenido")

def main():
    import os
    import sys
    
    # Verificar permisos para puertos bajos
    if os.geteuid() != 0:
        print("⚠️  Advertencia: Algunos puertos (<1024) requieren privilegios root")
        print("Ejecuta con sudo para todos los honeypots")
    
    honeypot = SimpleHoneypot()
    honeypot.start_all()

if __name__ == '__main__':
    main()
