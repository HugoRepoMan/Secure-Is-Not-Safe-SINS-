#!/usr/bin/env python3
"""
SSH Brute Force Detector - Detector de ataques reales de fuerza bruta
Monitorea logs de SSH y detecta intentos de autenticación fallidos
"""

import re
import time
import pymssql
from collections import defaultdict
from threading import Thread
import subprocess

class SSHBruteForceDetector:
    """
    Detecta ataques de fuerza bruta SSH reales analizando logs del sistema
    """
    
    def __init__(self):
        self.failed_attempts = defaultdict(list)
        self.threshold = 5  # 5 intentos fallidos
        self.time_window = 300  # en 5 minutos
        
        # Configuración de BD
        self.db_config = {
            'server': '127.0.0.1',
            'port': 1432,
            'user': 'sa',
            'password': 'TU_PASSWORD_AQUI',
            'database': 'CentralSIEM'
        }
    
    def parse_ssh_log(self, log_line):
        """
        Parsea líneas del log de SSH
        Ejemplo: "Failed password for root from 192.168.1.100 port 52341 ssh2"
        """
        # Patrón para intentos fallidos
        failed_pattern = r'Failed password for (?:invalid user )?(\w+) from ([\d.]+) port (\d+)'
        match = re.search(failed_pattern, log_line)
        
        if match:
            username = match.group(1)
            ip_address = match.group(2)
            port = match.group(3)
            
            return {
                'type': 'failed_login',
                'username': username,
                'ip': ip_address,
                'port': port,
                'timestamp': time.time()
            }
        
        # Patrón para login exitoso después de intentos fallidos (posible compromiso)
        success_pattern = r'Accepted password for (\w+) from ([\d.]+) port (\d+)'
        match = re.search(success_pattern, log_line)
        
        if match:
            username = match.group(1)
            ip_address = match.group(2)
            port = match.group(3)
            
            return {
                'type': 'successful_login',
                'username': username,
                'ip': ip_address,
                'port': port,
                'timestamp': time.time()
            }
        
        return None
    
    def check_brute_force(self, ip_address):
        """
        Verifica si una IP está realizando brute force
        """
        current_time = time.time()
        
        # Limpiar intentos antiguos
        self.failed_attempts[ip_address] = [
            t for t in self.failed_attempts[ip_address]
            if current_time - t < self.time_window
        ]
        
        # Verificar umbral
        if len(self.failed_attempts[ip_address]) >= self.threshold:
            return True
        
        return False
    
    def save_attack_to_db(self, attack_data):
        """Guarda ataque en la base de datos"""
        try:
            conn = pymssql.connect(**self.db_config)
            cursor = conn.cursor()
            
            query = """
                INSERT INTO [SENSOR_REMOTO].[SensorDB].[dbo].[Live_Alerts] 
                (TipoAtaque, IP_Origen, Severidad, Puerto_Destino, Protocolo, Timestamp)
                VALUES (%s, %s, %s, %s, %s, GETDATE())
            """
            
            cursor.execute(query, (
                'SSH Brute Force',
                attack_data['ip'],
                'CRITICAL' if attack_data['attempts'] > 10 else 'HIGH',
                22,
                'SSH'
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            print(f"✓ Ataque SSH registrado: {attack_data['ip']} ({attack_data['attempts']} intentos)")
            
        except Exception as e:
            print(f"✗ Error guardando en BD: {e}")
    
    def monitor_ssh_logs(self):
        """
        Monitorea logs de SSH en tiempo real
        """
        print("\n🔐 SSH Brute Force Detector - Iniciado")
        print("=" * 50)
        print("Monitoreando /var/log/auth.log")
        print("Presiona Ctrl+C para detener\n")
        
        try:
            # Seguir el archivo de log en tiempo real (como tail -f)
            process = subprocess.Popen(
                ['tail', '-F', '/var/log/auth.log'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            for line in iter(process.stdout.readline, ''):
                if 'sshd' in line:
                    parsed = self.parse_ssh_log(line)
                    
                    if parsed and parsed['type'] == 'failed_login':
                        ip = parsed['ip']
                        self.failed_attempts[ip].append(parsed['timestamp'])
                        
                        # Verificar brute force
                        if self.check_brute_force(ip):
                            attack_data = {
                                'ip': ip,
                                'attempts': len(self.failed_attempts[ip]),
                                'username': parsed['username']
                            }
                            
                            print(f"\n⚠️  BRUTE FORCE DETECTADO ⚠️")
                            print(f"IP: {ip}")
                            print(f"Intentos fallidos: {attack_data['attempts']}")
                            print(f"Usuario objetivo: {parsed['username']}")
                            print("-" * 50)
                            
                            # Guardar en BD
                            self.save_attack_to_db(attack_data)
                            
                            # Limpiar para evitar duplicados inmediatos
                            self.failed_attempts[ip].clear()
                    
                    elif parsed and parsed['type'] == 'successful_login':
                        # Verificar si hubo intentos fallidos previos (posible compromiso)
                        ip = parsed['ip']
                        if ip in self.failed_attempts and len(self.failed_attempts[ip]) > 0:
                            print(f"\n⚠️  POSIBLE COMPROMISO ⚠️")
                            print(f"Login exitoso después de {len(self.failed_attempts[ip])} intentos fallidos")
                            print(f"IP: {ip}")
                            print(f"Usuario: {parsed['username']}")
                            print("-" * 50)
        
        except KeyboardInterrupt:
            print("\n\n✓ Monitoreo SSH detenido")
        except Exception as e:
            print(f"\n✗ Error: {e}")

def main():
    import os
    import sys
    
    # Verificar permisos
    if os.geteuid() != 0:
        print("✗ Este script debe ejecutarse como root (sudo)")
        sys.exit(1)
    
    detector = SSHBruteForceDetector()
    detector.monitor_ssh_logs()

if __name__ == '__main__':
    main()
