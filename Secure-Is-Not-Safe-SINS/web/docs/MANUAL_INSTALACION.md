# 🚀 MANUAL DE INSTALACIÓN Y CONFIGURACIÓN
## Sistema SIEM con Base de Datos Distribuida

---

## 📋 TABLA DE CONTENIDOS

1. [Requisitos Previos](#requisitos-previos)
2. [Instalación Nodo Fedora (Central)](#instalación-nodo-fedora)
3. [Instalación Nodo Windows (Sensor)](#instalación-nodo-windows)
4. [Configuración de Red](#configuración-de-red)
5. [Configuración de Linked Server](#configuración-linked-server)
6. [Instalación de la Aplicación Web](#instalación-aplicación-web)
7. [Pruebas y Verificación](#pruebas-verificación)
8. [Solución de Problemas](#solución-problemas)

---

## 1️⃣ REQUISITOS PREVIOS

### Nodo Fedora Linux (Central)

**Especificaciones Mínimas:**
- Fedora Linux 38 o superior
- 4 GB RAM mínimo (8 GB recomendado)
- 20 GB espacio en disco
- Conexión a Internet

**Software Requerido:**
- SQL Server 2019/2022 para Linux
- Apache/Nginx
- PHP 8.0 o superior
- Driver PHP para SQL Server (sqlsrv, pdo_sqlsrv)

### Nodo Windows (Sensor)

**Especificaciones Mínimas:**
- Windows 10/11 o Windows Server 2019/2022
- 4 GB RAM mínimo
- 10 GB espacio en disco
- Conexión a red local

**Software Requerido:**
- SQL Server 2019/2022
- SQL Server Management Studio (SSMS)

---

## 2️⃣ INSTALACIÓN NODO FEDORA (CENTRAL)

### Paso 1: Actualizar el Sistema

```bash
sudo dnf update -y
sudo dnf upgrade -y
sudo reboot
```

### Paso 2: Instalar SQL Server para Linux

```bash
# Agregar repositorio de Microsoft
sudo curl -o /etc/yum.repos.d/mssql-server.repo https://packages.microsoft.com/config/rhel/9/mssql-server-2022.repo

# Instalar SQL Server
sudo dnf install -y mssql-server

# Configurar SQL Server
sudo /opt/mssql/bin/mssql-conf setup

# Seleccionar opciones:
# - Edition: Developer (gratis para desarrollo)
# - Accept license: Yes
# - SA password: CyberPass2026 (o tu contraseña segura)

# Verificar estado
sudo systemctl status mssql-server

# Habilitar inicio automático
sudo systemctl enable mssql-server
```

### Paso 3: Instalar Herramientas de SQL Server

```bash
# Agregar repositorio de herramientas
sudo curl -o /etc/yum.repos.d/msprod.repo https://packages.microsoft.com/config/rhel/9/prod.repo

# Instalar herramientas
sudo dnf install -y mssql-tools18 unixODBC-devel

# Agregar herramientas al PATH
echo 'export PATH="$PATH:/opt/mssql-tools18/bin"' >> ~/.bashrc
source ~/.bashrc

# Probar conexión
sqlcmd -S localhost -U sa -P 'CyberPass2026' -C -Q "SELECT @@VERSION"
```

### Paso 4: Configurar Firewall

```bash
# Abrir puerto SQL Server
sudo firewall-cmd --add-port=1432/tcp --permanent
sudo firewall-cmd --add-port=1433/tcp --permanent
sudo firewall-cmd --reload

# Verificar reglas
sudo firewall-cmd --list-ports
```

### Paso 5: Instalar Apache y PHP

```bash
# Instalar Apache
sudo dnf install -y httpd

# Instalar PHP y módulos
sudo dnf install -y php php-cli php-common php-json php-mbstring php-xml

# Instalar repositorio REMI para PHP 8.x (si es necesario)
sudo dnf install -y https://rpms.remirepo.net/fedora/remi-release-$(rpm -E %fedora).rpm
sudo dnf module enable php:remi-8.2 -y
sudo dnf install -y php php-cli php-fpm

# Verificar versión de PHP
php -v
```

### Paso 6: Instalar Driver PHP para SQL Server

```bash
# Instalar dependencias
sudo dnf install -y gcc gcc-c++ make autoconf unixODBC unixODBC-devel

# Instalar PECL
sudo dnf install -y php-pear php-devel

# Instalar driver sqlsrv
sudo pecl channel-update pecl.php.net
sudo pecl install sqlsrv
sudo pecl install pdo_sqlsrv

# Crear archivos de configuración
echo "extension=sqlsrv.so" | sudo tee /etc/php.d/30-sqlsrv.ini
echo "extension=pdo_sqlsrv.so" | sudo tee /etc/php.d/30-pdo_sqlsrv.ini

# Reiniciar Apache
sudo systemctl restart httpd

# Verificar instalación
php -m | grep sqlsrv
php -m | grep pdo_sqlsrv
```

### Paso 7: Configurar Apache

```bash
# Habilitar inicio automático
sudo systemctl enable httpd

# Iniciar servicio
sudo systemctl start httpd

# Verificar estado
sudo systemctl status httpd

# Configurar SELinux (si está activo)
sudo setsebool -P httpd_can_network_connect_db 1
sudo setsebool -P httpd_can_network_connect 1
```

---

## 3️⃣ INSTALACIÓN NODO WINDOWS (SENSOR)

### Paso 1: Descargar e Instalar SQL Server

1. **Descargar SQL Server 2022 Developer Edition**
   - URL: https://www.microsoft.com/en-us/sql-server/sql-server-downloads
   - Seleccionar: Developer Edition (gratis)

2. **Ejecutar instalador**
   - Tipo de instalación: Básica
   - Directorio: Dejar por defecto
   - Aceptar términos de licencia

3. **Configurar instancia**
   - Modo de autenticación: Modo mixto
   - Contraseña de SA: `WindowsPass2026` (o tu contraseña segura)
   - Agregar usuario actual como administrador

### Paso 2: Instalar SQL Server Management Studio (SSMS)

1. **Descargar SSMS**
   - URL: https://aka.ms/ssmsfullsetup

2. **Instalar SSMS**
   - Ejecutar instalador
   - Seguir pasos del wizard
   - Reiniciar si es necesario

### Paso 3: Configurar SQL Server para Acceso Remoto

1. **Abrir SQL Server Configuration Manager**

2. **Habilitar TCP/IP**
   - SQL Server Network Configuration → Protocols for MSSQLSERVER
   - TCP/IP → Right-click → Enable
   - Double-click TCP/IP → IP Addresses tab
   - IPAll → TCP Port: `1433`
   - Click OK

3. **Reiniciar servicio SQL Server**
   - SQL Server Services → SQL Server (MSSQLSERVER)
   - Right-click → Restart

### Paso 4: Configurar Firewall de Windows

```powershell
# Ejecutar PowerShell como Administrador

# Abrir puerto SQL Server
New-NetFirewallRule -DisplayName "SQL Server" -Direction Inbound -Protocol TCP -LocalPort 1433 -Action Allow

# Verificar regla
Get-NetFirewallRule -DisplayName "SQL Server"
```

### Paso 5: Obtener IP de Windows

```cmd
ipconfig

# Buscar la IP en "Adaptador de Ethernet" o "Adaptador de Wi-Fi"
# Ejemplo: 192.168.1.105
# ANOTAR ESTA IP - la necesitarás para configurar el Linked Server
```

---

## 4️⃣ CONFIGURACIÓN DE RED

### Verificar Conectividad entre Nodos

#### Desde Fedora hacia Windows:

```bash
# Ping a Windows (reemplazar IP)
ping 192.168.1.105

# Verificar puerto SQL Server abierto
nc -zv 192.168.1.105 1433
# o
telnet 192.168.1.105 1433

# Probar conexión SQL
sqlcmd -S 192.168.1.105,1433 -U sa -P 'WindowsPass2026' -C -Q "SELECT @@VERSION"
```

#### Desde Windows hacia Fedora:

```cmd
# Ping a Fedora (reemplazar IP)
ping 192.168.1.XXX

# Probar conexión SQL
sqlcmd -S 192.168.1.XXX,1432 -U sa -P "CyberPass2026" -Q "SELECT @@VERSION"
```

**IMPORTANTE:** Si la conexión falla, verificar:
- Firewalls en ambos lados
- IPs correctas
- Servicios SQL Server activos
- Contraseñas correctas

---

## 5️⃣ CONFIGURACIÓN DE LINKED SERVER

### En Nodo Fedora (Central)

1. **Conectar a SQL Server**

```bash
sqlcmd -S localhost,1432 -U sa -P 'CyberPass2026' -C
```

2. **Ejecutar script de configuración**

```sql
-- Crear Linked Server al nodo Windows
-- REEMPLAZAR '192.168.1.105' con la IP REAL de tu Windows
EXEC sp_addlinkedserver 
    @server = 'SENSOR_REMOTO',
    @srvproduct = '',
    @provider = 'SQLNCLI',
    @datasrc = '192.168.1.105,1433';
GO

-- Configurar credenciales
EXEC sp_addlinkedsrvlogin 
    @rmtsrvname = 'SENSOR_REMOTO',
    @useself = 'false',
    @rmtuser = 'sa',
    @rmtpassword = 'WindowsPass2026'; -- Contraseña de Windows
GO

-- Verificar configuración
EXEC sp_linkedservers;
GO

-- Probar conexión
SELECT * FROM [SENSOR_REMOTO].[master].[sys].[databases];
GO
```

3. **Ejecutar script completo de configuración**

```bash
# Copiar setup_distributed_database.sql al servidor
scp sql/setup_distributed_database.sql usuario@fedora:/tmp/

# En Fedora, ejecutar script
sqlcmd -S localhost,1432 -U sa -P 'CyberPass2026' -C -i /tmp/setup_distributed_database.sql
```

### En Nodo Windows (Sensor)

1. **Abrir SSMS**
   - Conectar a: `localhost`
   - Autenticación: SQL Server Authentication
   - Login: `sa`
   - Password: `WindowsPass2026`

2. **Ejecutar script para crear base de datos del sensor**

```sql
-- Crear base de datos
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'SensorDB')
BEGIN
    CREATE DATABASE SensorDB;
    PRINT '✓ Base de datos SensorDB creada';
END
GO

USE SensorDB;
GO

-- Crear tabla de alertas
CREATE TABLE Live_Alerts (
    AlertID INT IDENTITY(1,1) PRIMARY KEY,
    TipoAtaque NVARCHAR(100) NOT NULL,
    IP_Origen VARCHAR(45) NOT NULL,
    Severidad NVARCHAR(20) NOT NULL CHECK (Severidad IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    Timestamp DATETIME DEFAULT GETDATE(),
    Puerto_Destino INT,
    Protocolo NVARCHAR(20),
    Estado_Alerta NVARCHAR(20) DEFAULT 'ACTIVA',
    
    INDEX IX_Timestamp NONCLUSTERED (Timestamp DESC),
    INDEX IX_Severidad NONCLUSTERED (Severidad)
);
GO

-- Insertar datos de prueba
INSERT INTO Live_Alerts (TipoAtaque, IP_Origen, Severidad, Puerto_Destino, Protocolo)
VALUES 
    ('SQL Injection', '192.168.1.105', 'HIGH', 3306, 'TCP'),
    ('XSS Attack', '10.0.0.45', 'MEDIUM', 80, 'HTTP'),
    ('Ransomware Beacon', '172.16.0.88', 'CRITICAL', 443, 'HTTPS');
GO

PRINT '✓ Configuración del sensor Windows completada';
GO
```

---

## 6️⃣ INSTALACIÓN DE LA APLICACIÓN WEB

### Paso 1: Copiar Archivos al Servidor Web

```bash
# En Fedora, copiar proyecto a directorio web
sudo mkdir -p /var/www/html/PROYECTOPARCIAL3
sudo cp -r ProyectoParcial3_Mejorado/* /var/www/html/PROYECTOPARCIAL3/

# Establecer permisos correctos
sudo chown -R apache:apache /var/www/html/PROYECTOPARCIAL3
sudo chmod -R 755 /var/www/html/PROYECTOPARCIAL3

# Verificar estructura
ls -la /var/www/html/PROYECTOPARCIAL3/
```

### Paso 2: Configurar database.php

```bash
sudo nano /var/www/html/PROYECTOPARCIAL3/config/database.php
```

**Actualizar con tus valores:**

```php
private $host = "127.0.0.1";
private $port = "1432";
private $db_name = "CentralSIEM";
private $username = "sa";
private $password = "CyberPass2026"; // TU CONTRASEÑA REAL
```

### Paso 3: Configurar permisos de SELinux (si aplica)

```bash
# Permitir a Apache conectarse a la red
sudo setsebool -P httpd_can_network_connect 1
sudo setsebool -P httpd_can_network_connect_db 1

# Establecer contexto correcto
sudo chcon -R -t httpd_sys_content_t /var/www/html/PROYECTOPARCIAL3/
sudo chcon -R -t httpd_sys_rw_content_t /var/www/html/PROYECTOPARCIAL3/api/
```

### Paso 4: Reiniciar Apache

```bash
sudo systemctl restart httpd
sudo systemctl status httpd
```

---

## 7️⃣ PRUEBAS Y VERIFICACIÓN

### Prueba 1: Verificar PHP y Extensiones

```bash
# Crear archivo de prueba
echo '<?php phpinfo(); ?>' | sudo tee /var/www/html/test.php

# Abrir en navegador
# http://localhost/test.php

# Buscar secciones: pdo_sqlsrv y sqlsrv
# Eliminar archivo después de verificar
sudo rm /var/www/html/test.php
```

### Prueba 2: Probar Conexión de Base de Datos

```bash
# Crear script de prueba
sudo nano /var/www/html/PROYECTOPARCIAL3/test_connection.php
```

**Contenido:**

```php
<?php
require_once 'config/database.php';

echo "<h1>Prueba de Conexión</h1>";

$database = Database::getInstance();
$db = $database->getConnection();

if ($db) {
    echo "✅ Conexión exitosa a CentralSIEM<br>";
    
    // Probar consulta local
    try {
        $stmt = $db->query("SELECT @@VERSION AS Version");
        $row = $stmt->fetch(PDO::FETCH_ASSOC);
        echo "Versión SQL Server: " . $row['Version'] . "<br><br>";
        
        // Probar Linked Server
        echo "Probando conexión a nodo remoto...<br>";
        $stmt = $db->query("SELECT COUNT(*) as Total FROM [SENSOR_REMOTO].[SensorDB].[dbo].[Live_Alerts]");
        $row = $stmt->fetch(PDO::FETCH_ASSOC);
        echo "✅ Alertas remotas encontradas: " . $row['Total'] . "<br>";
        
    } catch (Exception $e) {
        echo "❌ Error en consultas: " . $e->getMessage();
    }
} else {
    echo "❌ No se pudo conectar a la base de datos";
}
?>
```

**Probar en navegador:**
```
http://localhost/PROYECTOPARCIAL3/test_connection.php
```

### Prueba 3: Probar API get_alerts.php

```bash
# Desde terminal
curl http://localhost/PROYECTOPARCIAL3/api/get_alerts.php | jq

# Desde navegador (abrir DevTools → Console)
fetch('http://localhost/PROYECTOPARCIAL3/api/get_alerts.php')
    .then(r => r.json())
    .then(d => console.log(d))
```

**Respuesta esperada:**
```json
{
    "success": true,
    "data": {
        "live": [...],
        "history": [...]
    },
    "metadata": {...}
}
```

### Prueba 4: Probar Aplicación Completa

1. **Abrir navegador**
   ```
   http://localhost/PROYECTOPARCIAL3/
   ```

2. **Verificar que se carguen:**
   - Tablas con datos
   - Estado "🟢 Online"
   - Botones funcionales

3. **Probar botón "Simular Ataque"**
   - Click en botón
   - Verificar notificación de éxito
   - Ver nueva alerta en tabla Windows

4. **Probar botón "Archivar Logs"**
   - Click en botón
   - Verificar notificación de éxito
   - Ver logs movidos a tabla Fedora
   - Tabla Windows debe estar vacía

---

## 8️⃣ SOLUCIÓN DE PROBLEMAS

### Problema: Error 404 en las APIs

**Síntoma:**
```
GET http://localhost/PROYECTOPARCIAL3/api/get_alerts.php [HTTP/1.1 404 Not Found]
```

**Soluciones:**

1. Verificar que los archivos existen:
```bash
ls -la /var/www/html/PROYECTOPARCIAL3/api/
```

2. Verificar permisos:
```bash
sudo chmod 644 /var/www/html/PROYECTOPARCIAL3/api/*.php
```

3. Verificar configuración de Apache:
```bash
sudo nano /etc/httpd/conf/httpd.conf

# Verificar que exista:
<Directory "/var/www/html">
    Options Indexes FollowSymLinks
    AllowOverride None
    Require all granted
</Directory>
```

4. Reiniciar Apache:
```bash
sudo systemctl restart httpd
```

---

### Problema: Error de Conexión a Base de Datos

**Síntoma:**
```
Error de conexión a la base de datos
```

**Soluciones:**

1. Verificar que SQL Server está corriendo:
```bash
sudo systemctl status mssql-server
```

2. Verificar credenciales en database.php

3. Probar conexión manual:
```bash
sqlcmd -S localhost,1432 -U sa -P 'CyberPass2026' -C -Q "SELECT 1"
```

4. Verificar drivers PHP:
```bash
php -m | grep sqlsrv
```

---

### Problema: Linked Server No Funciona

**Síntoma:**
```
Could not find server 'SENSOR_REMOTO' in sys.servers
```

**Soluciones:**

1. Verificar conectividad de red:
```bash
ping 192.168.1.105
telnet 192.168.1.105 1433
```

2. Recrear Linked Server:
```sql
-- Eliminar si existe
EXEC sp_dropserver 'SENSOR_REMOTO', 'droplogins';
GO

-- Volver a crear con IP correcta
EXEC sp_addlinkedserver 
    @server = 'SENSOR_REMOTO',
    @srvproduct = '',
    @provider = 'SQLNCLI',
    @datasrc = '192.168.1.105,1433';
GO
```

3. Verificar firewall en Windows:
```powershell
Get-NetFirewallRule -DisplayName "SQL Server"
```

---

### Problema: Tablas No Se Cargan (JavaScript Error)

**Síntoma:**
```
Unexpected token '<' in JSON at position 0
```

**Causa:** PHP está generando salida HTML antes del JSON (echo en database.php)

**Solución:** Usar el código corregido de database.php que NO hace echo

---

### Problema: Driver sqlsrv No Se Instala

**Síntoma:**
```
ERROR: `phpize' failed
```

**Soluciones:**

1. Instalar dependencias:
```bash
sudo dnf install -y php-pear php-devel gcc gcc-c++ make
```

2. Instalar headers de unixODBC:
```bash
sudo dnf install -y unixODBC-devel
```

3. Actualizar PECL:
```bash
sudo pecl channel-update pecl.php.net
```

4. Intentar instalación nuevamente:
```bash
sudo pecl install sqlsrv
sudo pecl install pdo_sqlsrv
```

---

### Problema: SELinux Bloquea Apache

**Síntoma:**
```
Permission denied al acceder a las APIs
```

**Soluciones:**

1. Verificar modo de SELinux:
```bash
getenforce
```

2. Permitir conexiones de Apache:
```bash
sudo setsebool -P httpd_can_network_connect 1
sudo setsebool -P httpd_can_network_connect_db 1
```

3. Verificar contexto de archivos:
```bash
ls -Z /var/www/html/PROYECTOPARCIAL3/

# Corregir si es necesario
sudo restorecon -R /var/www/html/PROYECTOPARCIAL3/
```

---

## 📞 SOPORTE

### Logs Útiles

```bash
# Logs de Apache
sudo tail -f /var/log/httpd/error_log

# Logs de SQL Server
sudo tail -f /var/opt/mssql/log/errorlog

# Logs de PHP
sudo tail -f /var/log/php-fpm/error.log
```

### Comandos de Diagnóstico

```bash
# Verificar puertos abiertos
sudo netstat -tulpn | grep -E ':(1432|1433|80|443)'

# Verificar servicios activos
sudo systemctl status mssql-server httpd

# Verificar SELinux denials
sudo ausearch -m avc -ts recent

# Verificar conectividad SQL Server
sqlcmd -S localhost,1432 -U sa -P 'CyberPass2026' -C -Q "SELECT GETDATE()"
```

---

## ✅ CHECKLIST DE INSTALACIÓN COMPLETA

- [ ] SQL Server instalado en Fedora
- [ ] SQL Server instalado en Windows
- [ ] Drivers PHP sqlsrv instalados
- [ ] Apache configurado y funcionando
- [ ] Firewall configurado en ambos nodos
- [ ] Linked Server creado y probado
- [ ] Bases de datos creadas (CentralSIEM, SensorDB)
- [ ] Tablas creadas con índices
- [ ] Datos de prueba insertados
- [ ] Archivos web copiados y con permisos correctos
- [ ] database.php configurado con credenciales reales
- [ ] API get_alerts.php responde correctamente
- [ ] API actions.php responde correctamente
- [ ] Interfaz web carga correctamente
- [ ] Botón "Simular Ataque" funciona
- [ ] Botón "Archivar Logs" funciona
- [ ] Tablas se actualizan automáticamente cada 5 segundos

---

**¡Felicidades! Tu sistema SIEM distribuido está completamente instalado y funcionando.** 🎉

---

**Fecha:** 30 de enero de 2026  
**Versión:** 1.0  
**Autores:** [Tus nombres]
