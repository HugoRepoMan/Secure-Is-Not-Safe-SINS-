# 📖 Guía de Instalación Completa

## Requisitos del Sistema

### Hardware Mínimo
- **CPU**: 2 núcleos
- **RAM**: 4 GB
- **Disco**: 20 GB libres
- **Red**: Tarjeta de red con modo promiscuo

### Software Requerido

#### Nodo Fedora (Master)
- Fedora 35+ o RHEL 8+
- SQL Server 2019+ para Linux
- Python 3.8 o superior
- Apache/Nginx (para dashboard)
- PHP 7.4+

#### Nodo Windows (Sensor) - Simulado en Fedora
- SQL Server 2019+ configurado como linked server
- O simular con segundo SQL Server en Fedora

## Instalación Paso a Paso

### 1. Preparar el Sistema Base

#### Actualizar el sistema
```bash
sudo dnf update -y
```

#### Instalar herramientas básicas
```bash
sudo dnf install -y git curl wget vim nano
```

### 2. Instalar SQL Server en Fedora

#### Configurar repositorio de Microsoft
```bash
# Descargar configuración del repositorio
sudo curl -o /etc/yum.repos.d/mssql-server.repo \
  https://packages.microsoft.com/config/rhel/8/mssql-server-2019.repo

# Instalar SQL Server
sudo dnf install -y mssql-server
```

#### Configurar SQL Server
```bash
# Ejecutar configuración inicial
sudo /opt/mssql/bin/mssql-conf setup

# Seleccionar:
# - Edición: Developer (gratuita)
# - Aceptar licencia: Yes
# - Contraseña SA: (tu contraseña segura, mín. 8 caracteres)
```

#### Habilitar y arrancar servicio
```bash
sudo systemctl enable mssql-server
sudo systemctl start mssql-server
sudo systemctl status mssql-server
```

#### Instalar herramientas de SQL Server
```bash
# Repositorio de herramientas
sudo curl -o /etc/yum.repos.d/msprod.repo \
  https://packages.microsoft.com/config/rhel/8/prod.repo

# Instalar sqlcmd
sudo dnf install -y mssql-tools unixODBC-devel

# Agregar al PATH
echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc
source ~/.bashrc
```

#### Probar conexión
```bash
sqlcmd -S localhost -U sa -P 'TuPassword' -C
# Deberías ver: 1>
# Escribe: SELECT @@VERSION
# Luego: GO
# Luego: QUIT
```

### 3. Configurar Base de Datos

#### Crear las bases de datos
```bash
# Conectar a SQL Server
sqlcmd -S localhost -U sa -P 'TuPassword' -C

# Ejecutar estos comandos:
CREATE DATABASE CentralSIEM;
GO

CREATE DATABASE SensorDB;
GO

USE CentralSIEM;
GO
```

#### Ejecutar script de schema
```bash
# Desde la terminal (fuera de sqlcmd)
cd siem-distributed-security/database

sqlcmd -S localhost -U sa -P 'TuPassword' -C \
  -d CentralSIEM -i setup_real_attacks.sql
```

#### Verificar tablas creadas
```bash
sqlcmd -S localhost -U sa -P 'TuPassword' -C

USE CentralSIEM;
SELECT name FROM sys.tables;
GO
# Deberías ver: Forense_Logs

USE SensorDB;
SELECT name FROM sys.tables;
GO
# Deberías ver: Live_Alerts
```

### 4. Configurar Linked Server

#### Crear linked server (simula Windows desde Fedora)
```bash
sqlcmd -S localhost,1432 -U sa -P 'TuPassword' -C
```

```sql
-- Crear linked server apuntando a localhost (simula remoto)
EXEC sp_addlinkedserver 
    @server = 'SENSOR_REMOTO',
    @srvproduct = '',
    @provider = 'SQLNCLI',
    @datasrc = 'localhost';
GO

-- Configurar credenciales
EXEC sp_addlinkedsrvlogin 
    @rmtsrvname = 'SENSOR_REMOTO',
    @useself = 'FALSE',
    @rmtuser = 'sa',
    @rmtpassword = 'TuPassword';
GO

-- Probar linked server
SELECT * FROM [SENSOR_REMOTO].[SensorDB].[sys].[tables];
GO
```

### 5. Instalar Python y Dependencias

#### Ejecutar script de instalación
```bash
cd siem-distributed-security/scripts
sudo chmod +x install.sh
sudo ./install.sh
```

El script instala:
- Python 3 y pip
- Scapy (captura de paquetes)
- pymssql (conexión SQL Server)
- tcpdump, nmap (herramientas de red)

#### Verificar instalación
```bash
python3 --version
# Python 3.X.X

python3 -c "import scapy; print('Scapy OK')"
# Scapy OK

python3 -c "import pymssql; print('pymssql OK')"
# pymssql OK
```

### 6. Configurar Detectores de Ataques

#### Configurar network_ids.py
```bash
nano detectors/network_ids.py
```

Modificar líneas 20-26:
```python
self.db_config = {
    'server': '127.0.0.1',           # Tu IP si es remoto
    'port': 1432,                     # Puerto de SQL Server
    'user': 'sa',
    'password': 'TU_PASSWORD_AQUI',  # ← CAMBIAR
    'database': 'CentralSIEM'
}
```

#### Configurar ssh_bruteforce.py
```bash
nano detectors/ssh_bruteforce.py
```

Modificar líneas 15-21:
```python
self.db_config = {
    'server': '127.0.0.1',
    'port': 1432,
    'user': 'sa',
    'password': 'TU_PASSWORD_AQUI',  # ← CAMBIAR
    'database': 'CentralSIEM'
}
```

#### Configurar honeypot.py
```bash
nano detectors/honeypot.py
```

Modificar líneas 40-46:
```python
self.db_config = {
    'server': '127.0.0.1',
    'port': 1432,
    'user': 'sa',
    'password': 'TU_PASSWORD_AQUI',  # ← CAMBIAR
    'database': 'CentralSIEM'
}
```

### 7. Configurar Dashboard Web

#### Instalar Apache y PHP
```bash
sudo dnf install -y httpd php php-mysqlnd php-sqlsrv
sudo systemctl enable httpd
sudo systemctl start httpd
```

#### Instalar driver PHP para SQL Server
```bash
# Agregar repositorio PECL
sudo dnf install -y php-pear php-devel

# Descargar drivers de Microsoft
curl https://packages.microsoft.com/config/rhel/8/prod.repo | \
  sudo tee /etc/yum.repos.d/mssql-release.repo

# Instalar drivers
sudo ACCEPT_EULA=Y dnf install -y msodbcsql17 mssql-tools

# Instalar extensiones PHP
sudo pecl install sqlsrv
sudo pecl install pdo_sqlsrv

# Habilitar extensiones
echo "extension=sqlsrv.so" | sudo tee -a /etc/php.ini
echo "extension=pdo_sqlsrv.so" | sudo tee -a /etc/php.ini

# Reiniciar Apache
sudo systemctl restart httpd
```

#### Copiar dashboard a directorio web
```bash
sudo cp -r dashboard /var/www/html/siem-dashboard
sudo chown -R apache:apache /var/www/html/siem-dashboard
sudo chmod -R 755 /var/www/html/siem-dashboard
```

#### Configurar credenciales del dashboard
```bash
sudo nano /var/www/html/siem-dashboard/config/database.php
```

Modificar:
```php
<?php
$serverName = "localhost,1432";
$uid = "sa";
$pwd = "TU_PASSWORD_AQUI";  // ← CAMBIAR
$database = "CentralSIEM";
?>
```

#### Configurar SELinux (si está habilitado)
```bash
# Permitir que Apache se conecte a la red
sudo setsebool -P httpd_can_network_connect 1
sudo setsebool -P httpd_can_network_connect_db 1
```

#### Configurar firewall
```bash
# Permitir HTTP
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https

# Permitir SQL Server
sudo firewall-cmd --permanent --add-port=1432/tcp

# Permitir honeypots
sudo firewall-cmd --permanent --add-port=2222/tcp
sudo firewall-cmd --permanent --add-port=8080/tcp
sudo firewall-cmd --permanent --add-port=3306/tcp
sudo firewall-cmd --permanent --add-port=5432/tcp

# Recargar firewall
sudo firewall-cmd --reload
```

### 8. Verificar Interfaz de Red

```bash
# Listar interfaces
ip link show

# Comunes: eth0, enp0s3, ens33, wlp2s0, etc.
# Usar en los detectores
```

### 9. Probar el Sistema

#### Test 1: Probar detector
```bash
cd siem-distributed-security/detectors
sudo python3 network_ids.py eth0  # Reemplazar eth0
```

Deberías ver:
```
🛡️ Network IDS iniciado en interfaz: eth0
📊 Conectado a base de datos: CentralSIEM
⏳ Monitoreando tráfico...
```

#### Test 2: Probar dashboard
```bash
# Abrir navegador
firefox http://localhost/siem-dashboard/

# Deberías ver el dashboard vacío (sin alertas aún)
```

#### Test 3: Generar alerta de prueba
```bash
# Desde otra terminal
sudo python3 scripts/attack_generator.py
```

#### Test 4: Verificar alerta en BD
```bash
sqlcmd -S localhost -U sa -P 'TuPassword' -C

USE CentralSIEM;
SELECT TOP 5 * FROM [SENSOR_REMOTO].[SensorDB].[dbo].[Live_Alerts] 
ORDER BY Timestamp DESC;
GO
```

## Configuraciones Adicionales

### Habilitar captura de paquetes sin sudo (opcional)
```bash
# Dar permisos a Python
sudo setcap cap_net_raw,cap_net_admin=eip $(which python3)

# Ahora puedes ejecutar sin sudo
python3 detectors/network_ids.py eth0
```

### Configurar ejecución automática (systemd)
```bash
# Crear servicio para network_ids
sudo nano /etc/systemd/system/siem-ids.service
```

```ini
[Unit]
Description=SIEM Network IDS
After=network.target mssql-server.service

[Service]
Type=simple
User=root
WorkingDirectory=/home/usuario/siem-distributed-security/detectors
ExecStart=/usr/bin/python3 network_ids.py eth0
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Habilitar servicio
sudo systemctl daemon-reload
sudo systemctl enable siem-ids
sudo systemctl start siem-ids
```

### Configurar logs rotación
```bash
# Crear configuración logrotate
sudo nano /etc/logrotate.d/siem
```

```
/var/log/siem/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 root root
}
```

## Solución de Problemas Comunes

### Error: "Cannot connect to SQL Server"
```bash
# Verificar servicio
sudo systemctl status mssql-server

# Verificar puerto
sudo netstat -tulpn | grep 1432

# Verificar firewall
sudo firewall-cmd --list-all

# Reintentar conexión
sqlcmd -S localhost -U sa -P 'Password' -C
```

### Error: "Permission denied" en detectors
```bash
# Ejecutar con sudo
sudo python3 detectors/network_ids.py eth0

# O configurar capabilities (ver arriba)
```

### Error: "Module not found: scapy"
```bash
# Reinstalar dependencias
sudo pip3 install scapy pymssql

# Verificar
python3 -c "import scapy; print('OK')"
```

### Dashboard no carga
```bash
# Verificar Apache
sudo systemctl status httpd

# Ver logs
sudo tail -f /var/log/httpd/error_log

# Verificar permisos
sudo chown -R apache:apache /var/www/html/siem-dashboard
```

### No se detectan ataques
```bash
# Verificar interfaz correcta
ip addr show

# Probar con tcpdump
sudo tcpdump -i eth0 -c 5

# Generar tráfico de prueba
ping -c 5 google.com
```

## Checklist de Instalación

- [ ] SQL Server instalado y funcionando
- [ ] Bases de datos CentralSIEM y SensorDB creadas
- [ ] Tablas creadas (Forense_Logs, Live_Alerts)
- [ ] Linked Server configurado
- [ ] Python 3 instalado
- [ ] Scapy y pymssql instalados
- [ ] Detectores configurados con credenciales
- [ ] Apache y PHP instalados
- [ ] Dashboard copiado a /var/www/html
- [ ] Dashboard configurado con credenciales
- [ ] Firewall configurado
- [ ] Interfaz de red identificada
- [ ] Pruebas básicas exitosas

## Próximos Pasos

Una vez instalado todo:
1. Lee el [Manual de Uso](USO.md)
2. Ejecuta los detectores
3. Genera ataques de prueba
4. Prepara tu [Demostración](DEMOSTRACION.md)

---

**¿Problemas?** Revisa [Troubleshooting](TROUBLESHOOTING.md)
