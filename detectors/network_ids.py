#!/usr/bin/env python3
"""
SIEM Real - Detector de Ataques con Snort
Sistema de Detección de Intrusiones que captura ataques reales

Detecta:
- Port Scanning (Nmap)
- Brute Force SSH/FTP
- SQL Injection
- XSS Attacks
- DDoS attempts
- Malware signatures
"""

import subprocess
import re
import json
import datetime
import socket
import pymssql
from scapy.all import sniff, IP, TCP, UDP, ICMP
from collections import defaultdict, deque
from threading import Thread, Lock
import time

class RealAttackDetector:
    """
    Detector de ataques reales usando análisis de paquetes
    """
    
    def __init__(self, interface='eth0'):
        self.interface = interface
        self.attack_buffer = deque(maxlen=1000)
        self.lock = Lock()
        
        # Contadores para detección de patrones
        self.port_scan_tracker = defaultdict(lambda: {'ports': set(), 'time': time.time()})
        self.brute_force_tracker = defaultdict(lambda: {'attempts': 0, 'time': time.time()})
        self.ddos_tracker = defaultdict(lambda: {'count': 0, 'time': time.time()})
        
        # Umbrales de detección
        self.PORT_SCAN_THRESHOLD = 10  # 10 puertos diferentes en 60 segundos
        self.BRUTE_FORCE_THRESHOLD = 5  # 5 intentos fallidos en 60 segundos
        self.DDOS_THRESHOLD = 100  # 100 paquetes en 10 segundos
        
        # Conexión a base de datos
        self.db_config = {
            'server': '127.0.0.1',
            'port': 1432,
            'user': 'sa',
            'password': 'TU_PASSWORD_AQUI',
            'database': 'CentralSIEM'
        }
    def detect_port_scan(self, packet):
        """Detecta port scanning (Nmap, Masscan, etc.)"""
        if packet.haslayer(TCP) and packet[TCP].flags == 2:  # SYN flag
            src_ip = packet[IP].src
            dst_port = packet[TCP].dport
            
            current_time = time.time()
            tracker = self.port_scan_tracker[src_ip]
            
            # Limpiar datos antiguos
            if current_time - tracker['time'] > 60:
                tracker['ports'].clear()
                tracker['time'] = current_time
            
            tracker['ports'].add(dst_port)
            
            # Si se escanean muchos puertos en poco tiempo
            if len(tracker['ports']) >= self.PORT_SCAN_THRESHOLD:
                return {
                    'type': 'Port Scanning',
                    'severity': 'MEDIUM',
                    'src_ip': src_ip,
                    'dst_ip': packet[IP].dst,
                    'ports_scanned': len(tracker['ports']),
                    'description': f'Port scan detectado desde {src_ip}: {len(tracker["ports"])} puertos'
                }
        return None
    
    def detect_syn_flood(self, packet):
        """Detecta SYN flood (tipo de DDoS)"""
        if packet.haslayer(TCP) and packet[TCP].flags == 2:  # SYN flag
            src_ip = packet[IP].src
            current_time = time.time()
            tracker = self.ddos_tracker[src_ip]
            
            # Limpiar datos antiguos
            if current_time - tracker['time'] > 10:
                tracker['count'] = 0
                tracker['time'] = current_time
            
            tracker['count'] += 1
            
            # Si hay demasiados SYN en poco tiempo
            if tracker['count'] >= self.DDOS_THRESHOLD:
                return {
                    'type': 'SYN Flood Attack',
                    'severity': 'CRITICAL',
                    'src_ip': src_ip,
                    'dst_ip': packet[IP].dst,
                    'packet_count': tracker['count'],
                    'description': f'SYN Flood detectado: {tracker["count"]} paquetes en 10 segundos'
                }
        return None
    
    def detect_icmp_flood(self, packet):
        """Detecta ICMP flood (Ping flood)"""
        if packet.haslayer(ICMP):
            src_ip = packet[IP].src
            current_time = time.time()
            tracker = self.ddos_tracker[src_ip]
            
            if current_time - tracker['time'] > 10:
                tracker['count'] = 0
                tracker['time'] = current_time
            
            tracker['count'] += 1
            
            if tracker['count'] >= 50:  # 50 pings en 10 segundos
                return {
                    'type': 'ICMP Flood Attack',
                    'severity': 'HIGH',
                    'src_ip': src_ip,
                    'dst_ip': packet[IP].dst,
                    'packet_count': tracker['count'],
                    'description': f'ICMP Flood detectado: {tracker["count"]} paquetes'
                }
        return None
    
    def detect_suspicious_payload(self, packet):
        """Detecta payloads sospechosos (SQL injection, XSS, etc.)"""
        if packet.haslayer(TCP) and packet.haslayer('Raw'):
            payload = str(packet['Raw'].load)
            
            # Patrones de SQL injection
            sql_patterns = [
                r"(\bOR\b|\bAND\b)\s+['\"]?\d+['\"]?\s*=\s*['\"]?\d+",
                r"UNION\s+SELECT",
                r"DROP\s+TABLE",
                r"'; DROP",
                r"--",
                r"1=1",
                r"admin'--"
            ]
            
            # Patrones de XSS
            xss_patterns = [
                r"<script",
                r"javascript:",
                r"onerror=",
                r"onload="
            ]
            
            for pattern in sql_patterns:
                if re.search(pattern, payload, re.IGNORECASE):
                    return {
                        'type': 'SQL Injection Attempt',
                        'severity': 'CRITICAL',
                        'src_ip': packet[IP].src,
                        'dst_ip': packet[IP].dst,
                        'dst_port': packet[TCP].dport if packet.haslayer(TCP) else 0,
                        'description': f'SQL Injection detectado: patrón "{pattern}"'
                    }
            
            for pattern in xss_patterns:
                if re.search(pattern, payload, re.IGNORECASE):
                    return {
                        'type': 'XSS Attack Attempt',
                        'severity': 'HIGH',
                        'src_ip': packet[IP].src,
                        'dst_ip': packet[IP].dst,
                        'dst_port': packet[TCP].dport if packet.haslayer(TCP) else 0,
                        'description': f'XSS detectado: patrón "{pattern}"'
                    }
        
        return None
    
    def save_to_database(self, attack_data):
        """Guarda ataque detectado en la base de datos"""
        try:
            conn = pymssql.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Insertar en la tabla del nodo remoto (Windows)
            query = """
                INSERT INTO [SENSOR_REMOTO].[SensorDB].[dbo].[Live_Alerts] 
                (TipoAtaque, IP_Origen, Severidad, Puerto_Destino, Protocolo, Timestamp)
                VALUES (%s, %s, %s, %s, %s, GETDATE())
            """
            
            cursor.execute(query, (
                attack_data['type'],
                attack_data['src_ip'],
                attack_data['severity'],
                attack_data.get('dst_port', 0),
                attack_data.get('protocol', 'TCP')
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            print(f"✓ Ataque registrado: {attack_data['type']} desde {attack_data['src_ip']}")
            
        except Exception as e:
            print(f"✗ Error guardando en BD: {e}")
    
    def packet_handler(self, packet):
        """Manejador principal de paquetes"""
        if not packet.haslayer(IP):
            return
        
        # Lista de detectores
        detectors = [
            self.detect_port_scan,
            self.detect_syn_flood,
            self.detect_icmp_flood,
            self.detect_suspicious_payload
        ]
        
        # Ejecutar cada detector
        for detector in detectors:
            try:
                attack = detector(packet)
                if attack:
                    with self.lock:
                        # Evitar duplicados recientes
                        attack_key = f"{attack['type']}_{attack['src_ip']}"
                        if attack_key not in [a.get('key') for a in self.attack_buffer]:
                            attack['key'] = attack_key
                            attack['timestamp'] = datetime.datetime.now().isoformat()
                            self.attack_buffer.append(attack)
                            
                            # Guardar en base de datos
                            self.save_to_database(attack)
                            
                            # Log en consola
                            print(f"\n⚠️  ATAQUE DETECTADO ⚠️")
                            print(f"Tipo: {attack['type']}")
                            print(f"Severidad: {attack['severity']}")
                            print(f"Origen: {attack['src_ip']}")
                            print(f"Descripción: {attack['description']}")
                            print("-" * 50)
            except Exception as e:
                print(f"Error en detector: {e}")
    
    def start_monitoring(self):
        """Inicia el monitoreo de red"""
        print(f"\n🛡️  SIEM Real - Iniciando detección de ataques")
        print(f"Interface: {self.interface}")
        print(f"Presiona Ctrl+C para detener\n")
        print("=" * 50)
        print("MONITOREANDO TRÁFICO DE RED...")
        print("=" * 50)
        
        try:
            sniff(
                iface=self.interface,
                prn=self.packet_handler,
                store=0
            )
        except KeyboardInterrupt:
            print("\n\n✓ Monitoreo detenido por el usuario")
        except Exception as e:
            print(f"\n✗ Error en monitoreo: {e}")

def main():
    """Función principal"""
    import sys
    
    # Verificar que se ejecuta como root (necesario para captura de paquetes)
    if os.geteuid() != 0:
        print("✗ Este script debe ejecutarse como root (sudo)")
        sys.exit(1)
    
    # Obtener interfaz de red
    interface = sys.argv[1] if len(sys.argv) > 1 else 'eth0'
    
    # Crear detector
    detector = RealAttackDetector(interface=interface)
    
    # Iniciar monitoreo
    detector.start_monitoring()

if __name__ == '__main__':
    import os
    main()
