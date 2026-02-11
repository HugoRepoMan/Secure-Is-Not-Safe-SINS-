#!/bin/bash
# Script de instalación para SIEM Real
# Sistema de detección de ataques reales

echo "=================================================="
echo "🛡️  INSTALADOR SIEM REAL - Detector de Ataques"
echo "=================================================="
echo ""

# Verificar que se ejecuta como root
if [ "$EUID" -ne 0 ]; then 
    echo "✗ Este script debe ejecutarse como root (sudo)"
    exit 1
fi

echo "📦 Instalando dependencias del sistema..."
echo ""

# Actualizar repositorios
echo "[1/8] Actualizando repositorios..."
dnf update -y >/dev/null 2>&1
echo "✓ Repositorios actualizados"

# Instalar Python 3 y pip
echo "[2/8] Instalando Python 3..."
dnf install -y python3 python3-pip python3-devel >/dev/null 2>&1
echo "✓ Python 3 instalado"

# Instalar herramientas de red
echo "[3/8] Instalando herramientas de red..."
dnf install -y tcpdump nmap netcat >/dev/null 2>&1
echo "✓ Herramientas de red instaladas"

# Instalar librerías de desarrollo
echo "[4/8] Instalando librerías de desarrollo..."
dnf install -y gcc libpcap-devel >/dev/null 2>&1
echo "✓ Librerías instaladas"

# Instalar FreeTDS (para pymssql)
echo "[5/8] Instalando FreeTDS..."
dnf install -y freetds freetds-devel >/dev/null 2>&1
echo "✓ FreeTDS instalado"

echo ""
echo "📦 Instalando paquetes de Python..."
echo ""

# Instalar paquetes de Python
echo "[6/8] Instalando Scapy..."
pip3 install scapy --quiet
echo "✓ Scapy instalado"

echo "[7/8] Instalando pymssql..."
pip3 install pymssql --quiet
echo "✓ pymssql instalado"

echo "[8/8] Instalando requests..."
pip3 install requests --quiet
echo "✓ requests instalado"

echo ""
echo "=================================================="
echo "✓ INSTALACIÓN COMPLETADA"
echo "=================================================="
echo ""
echo "Herramientas instaladas:"
echo "  • Python 3 con pip"
echo "  • Scapy (captura de paquetes)"
echo "  • pymssql (conexión a SQL Server)"
echo "  • tcpdump, nmap, netcat"
echo ""
echo "Próximos pasos:"
echo "  1. Configura las credenciales de BD en los scripts"
echo "  2. Ejecuta un detector: sudo python3 detectors/network_ids.py"
echo "  3. O ejecuta el honeypot: sudo python3 detectors/honeypot.py"
echo "  4. Genera ataques de prueba: sudo python3 attack_generator.py"
echo ""
echo "=================================================="
