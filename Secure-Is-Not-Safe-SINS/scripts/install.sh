#!/bin/bash
# =====================================================
# Script de instalación - SIEM Distribuido
# =====================================================

echo "🔧 INSTALACIÓN - Sistema SIEM Distribuido"
echo "=========================================="

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Verificar que sea root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}✗ Por favor ejecuta con sudo${NC}"
    exit 1
fi

echo ""
echo "📦 Instalando dependencias Python..."
dnf install -y python3 python3-pip

echo ""
echo "📚 Instalando librerías Python..."
pip3 install --break-system-packages pymssql scapy requests

echo ""
echo "🌐 Configurando Apache..."
dnf install -y httpd php php-sqlsrv php-pdo_sqlsrv

echo ""
echo "🔥 Configurando firewall..."
firewall-cmd --add-service=http --permanent
firewall-cmd --add-port=1432/tcp --permanent
firewall-cmd --add-port=2222/tcp --permanent
firewall-cmd --add-port=8080/tcp --permanent
firewall-cmd --add-port=3306/tcp --permanent
firewall-cmd --add-port=5432/tcp --permanent
firewall-cmd --add-port=21/tcp --permanent
firewall-cmd --reload

echo ""
echo "📁 Copiando aplicación web..."
mkdir -p /var/www/html/PROYECTOPARCIAL3
cp -r web/* /var/www/html/PROYECTOPARCIAL3/
chown -R apache:apache /var/www/html/PROYECTOPARCIAL3
chmod -R 755 /var/www/html/PROYECTOPARCIAL3

echo ""
echo "🔐 Configurando SELinux..."
chcon -R -t httpd_sys_content_t /var/www/html/PROYECTOPARCIAL3
setsebool -P httpd_can_network_connect 1
setsebool -P httpd_can_network_connect_db 1

echo ""
echo "🚀 Iniciando Apache..."
systemctl enable httpd
systemctl start httpd

echo ""
echo -e "${GREEN}✓ Instalación completada${NC}"
echo ""
echo "📋 Próximos pasos:"
echo "1. Configurar SQL Server en Fedora (puerto 1432)"
echo "2. Ejecutar: sqlcmd -S localhost,1432 -U sa -P 'TU_PASSWORD' -i sql/setup_fedora.sql"
echo "3. Configurar SQL Server en Windows (puerto 1433)"
echo "4. Ejecutar en Windows: sqlcmd -S localhost -U sa -P 'PASSWORD' -i sql/setup_windows.sql"
echo "5. Configurar Linked Server: sqlcmd -S localhost,1432 -U sa -P 'PASSWORD' -i sql/setup_linked_server.sql"
echo "6. Editar detectors/honeypot.py con IP de Windows"
echo "7. Iniciar honeypot: sudo python3 detectors/honeypot.py"
echo ""
echo "🌐 Dashboard disponible en: http://localhost/PROYECTOPARCIAL3/"
