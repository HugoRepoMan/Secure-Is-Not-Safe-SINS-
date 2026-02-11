#!/bin/bash
# Script de configuración rápida del SIEM Distribuido
# Ejecutar: sudo bash setup.sh

echo "🛡️  SIEM DISTRIBUIDO - CONFIGURACIÓN RÁPIDA"
echo "=========================================="
echo ""

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar que se ejecuta como root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}❌ Este script debe ejecutarse como root (sudo)${NC}"
   exit 1
fi

echo "📋 Checklist de pre-requisitos:"
echo ""

# Verificar SQL Server
echo -n "Verificando SQL Server... "
if systemctl is-active --quiet mssql-server; then
    echo -e "${GREEN}✓ Activo${NC}"
else
    echo -e "${RED}✗ No encontrado${NC}"
    echo "   Instala SQL Server primero: https://docs.microsoft.com/sql/linux/"
    exit 1
fi

# Verificar Python
echo -n "Verificando Python 3... "
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo -e "${GREEN}✓ $PYTHON_VERSION${NC}"
else
    echo -e "${RED}✗ No encontrado${NC}"
    exit 1
fi

# Verificar Apache/Nginx
echo -n "Verificando servidor web... "
if systemctl is-active --quiet httpd || systemctl is-active --quiet apache2; then
    echo -e "${GREEN}✓ Apache activo${NC}"
    WEB_SERVER="httpd"
elif systemctl is-active --quiet nginx; then
    echo -e "${GREEN}✓ Nginx activo${NC}"
    WEB_SERVER="nginx"
else
    echo -e "${YELLOW}⚠ No encontrado (instalar Apache o Nginx)${NC}"
    WEB_SERVER="none"
fi

echo ""
echo "🔧 Configurando el sistema..."
echo ""

# 1. Crear directorios necesarios
echo -n "Creando directorios de logs... "
mkdir -p /var/log/siem
chmod 755 /var/log/siem
echo -e "${GREEN}✓${NC}"

# 2. Pedir credenciales
echo ""
echo "🔐 Configuración de credenciales SQL Server:"
read -p "Usuario SA: " SQL_USER
read -sp "Contraseña SA: " SQL_PASSWORD
echo ""

# 3. Detectar interfaz de red
echo ""
echo "🌐 Interfaces de red disponibles:"
ip -o link show | awk -F': ' '{print "   - " $2}' | grep -v lo
echo ""
read -p "Interfaz a monitorear (ej: eth0): " NETWORK_INTERFACE

# 4. Configurar detectores
echo ""
echo -n "Configurando detectores... "

# Network IDS
sed -i "s/'password': '.*'/'password': '$SQL_PASSWORD'/g" detectors/network_ids.py
sed -i "s/'user': '.*'/'user': '$SQL_USER'/g" detectors/network_ids.py

# SSH Monitor
sed -i "s/'password': '.*'/'password': '$SQL_PASSWORD'/g" detectors/ssh_bruteforce.py
sed -i "s/'user': '.*'/'user': '$SQL_USER'/g" detectors/ssh_bruteforce.py

# Honeypot
sed -i "s/'password': '.*'/'password': '$SQL_PASSWORD'/g" detectors/honeypot.py
sed -i "s/'user': '.*'/'user': '$SQL_USER'/g" detectors/honeypot.py

echo -e "${GREEN}✓${NC}"

# 5. Configurar dashboard
if [ "$WEB_SERVER" != "none" ]; then
    echo -n "Configurando dashboard web... "
    
    # Copiar dashboard
    if [ "$WEB_SERVER" = "httpd" ]; then
        WEB_DIR="/var/www/html"
    else
        WEB_DIR="/usr/share/nginx/html"
    fi
    
    cp -r dashboard "$WEB_DIR/siem-dashboard"
    chown -R apache:apache "$WEB_DIR/siem-dashboard" 2>/dev/null || \
    chown -R nginx:nginx "$WEB_DIR/siem-dashboard" 2>/dev/null
    chmod -R 755 "$WEB_DIR/siem-dashboard"
    
    # Configurar credenciales
    cat > "$WEB_DIR/siem-dashboard/config/database.php" << EOF
<?php
\$serverName = "localhost,1432";
\$uid = "$SQL_USER";
\$pwd = "$SQL_PASSWORD";
\$database = "CentralSIEM";

\$connectionOptions = array(
    "Database" => \$database,
    "UID" => \$uid,
    "PWD" => \$pwd,
    "TrustServerCertificate" => true
);
?>
EOF
    
    echo -e "${GREEN}✓${NC}"
fi

# 6. Configurar firewall
echo -n "Configurando firewall... "
if command -v firewall-cmd &> /dev/null; then
    firewall-cmd --permanent --add-service=http --quiet
    firewall-cmd --permanent --add-port=1432/tcp --quiet
    firewall-cmd --permanent --add-port=2222/tcp --quiet
    firewall-cmd --permanent --add-port=8080/tcp --quiet
    firewall-cmd --permanent --add-port=3306/tcp --quiet
    firewall-cmd --permanent --add-port=5432/tcp --quiet
    firewall-cmd --reload --quiet
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${YELLOW}⚠ firewall-cmd no encontrado (saltar)${NC}"
fi

# 7. Verificar conectividad con SQL Server
echo ""
echo -n "Probando conexión a SQL Server... "
if command -v sqlcmd &> /dev/null; then
    if sqlcmd -S localhost -U "$SQL_USER" -P "$SQL_PASSWORD" -C -Q "SELECT 1" &> /dev/null; then
        echo -e "${GREEN}✓ Conexión exitosa${NC}"
    else
        echo -e "${RED}✗ Error de conexión${NC}"
        echo "   Verifica usuario y contraseña"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠ sqlcmd no encontrado (saltar verificación)${NC}"
fi

# 8. Crear script de inicio rápido
echo ""
echo -n "Creando scripts de inicio... "

cat > /usr/local/bin/start-siem << 'EOF'
#!/bin/bash
echo "🛡️  Iniciando SIEM Distribuido..."
cd INSTALL_DIR

# Terminal 1: Network IDS
gnome-terminal -- bash -c "sudo python3 detectors/network_ids.py NETWORK_IF; exec bash" &

# Terminal 2: Honeypot
gnome-terminal -- bash -c "sudo python3 detectors/honeypot.py; exec bash" &

# Terminal 3: Dashboard
sleep 2
xdg-open "http://localhost/siem-dashboard/" &

echo "✅ SIEM iniciado"
echo "   - Network IDS monitoreando NETWORK_IF"
echo "   - Honeypot escuchando en puertos señuelo"
echo "   - Dashboard: http://localhost/siem-dashboard/"
EOF

sed -i "s|INSTALL_DIR|$(pwd)|g" /usr/local/bin/start-siem
sed -i "s|NETWORK_IF|$NETWORK_INTERFACE|g" /usr/local/bin/start-siem
chmod +x /usr/local/bin/start-siem

cat > /usr/local/bin/stop-siem << 'EOF'
#!/bin/bash
echo "🛑 Deteniendo SIEM Distribuido..."
sudo pkill -f network_ids.py
sudo pkill -f honeypot.py
sudo pkill -f ssh_bruteforce.py
echo "✅ SIEM detenido"
EOF

chmod +x /usr/local/bin/stop-siem

echo -e "${GREEN}✓${NC}"

# Resumen final
echo ""
echo "=========================================="
echo -e "${GREEN}✅ CONFIGURACIÓN COMPLETADA${NC}"
echo "=========================================="
echo ""
echo "📝 Resumen de configuración:"
echo "   • SQL Server: localhost:1432"
echo "   • Usuario: $SQL_USER"
echo "   • Interfaz: $NETWORK_INTERFACE"
if [ "$WEB_SERVER" != "none" ]; then
    echo "   • Dashboard: http://localhost/siem-dashboard/"
fi
echo ""
echo "🚀 Para iniciar el sistema:"
echo "   sudo start-siem"
echo ""
echo "🛑 Para detener el sistema:"
echo "   sudo stop-siem"
echo ""
echo "📚 Documentación:"
echo "   • Uso: docs/USO.md"
echo "   • Demo: docs/DEMOSTRACION.md"
echo ""
echo "⚠️  NOTA: Verifica que las bases de datos estén creadas"
echo "   Ver: database/setup_real_attacks.sql"
echo ""

# Preguntar si crear base de datos
read -p "¿Deseas crear las bases de datos ahora? (s/n): " CREATE_DB

if [ "$CREATE_DB" = "s" ] || [ "$CREATE_DB" = "S" ]; then
    echo ""
    echo "Creando bases de datos..."
    
    if [ -f "database/setup_real_attacks.sql" ]; then
        sqlcmd -S localhost -U "$SQL_USER" -P "$SQL_PASSWORD" -C -i database/setup_real_attacks.sql
        echo -e "${GREEN}✅ Bases de datos creadas${NC}"
    else
        echo -e "${RED}❌ No se encontró setup_real_attacks.sql${NC}"
    fi
fi

echo ""
echo "✨ ¡Listo para usar!"
