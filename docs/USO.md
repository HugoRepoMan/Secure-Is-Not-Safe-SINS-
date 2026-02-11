# 📘 Manual de Uso del Sistema SIEM

## Introducción

Este manual explica cómo operar el sistema SIEM una vez instalado correctamente.

## Componentes del Sistema

### 1. Detectores de Ataques (Python)
- **network_ids.py**: Detector principal de red
- **ssh_bruteforce.py**: Monitor de SSH
- **honeypot.py**: Servicios señuelo

### 2. Dashboard Web (PHP)
- Visualización de alertas en tiempo real
- Control de acciones (simular/archivar)

### 3. Generador de Ataques (Python)
- **attack_generator.py**: Para demostraciones

## Operación de Detectores

### Network IDS (Detector Principal)

#### Iniciar el detector
```bash
cd siem-distributed-security/detectors
sudo python3 network_ids.py eth0  # Reemplazar eth0 con tu interfaz
```

#### Salida esperada
```
🛡️ Network IDS iniciado en interfaz: eth0
📊 Conectado a base de datos: CentralSIEM
⏳ Monitoreando tráfico...

[Timestamp] Paquete capturado: TCP 192.168.1.5:54321 -> 192.168.1.10:80
[Timestamp] Paquete capturado: ICMP 192.168.1.1 -> 192.168.1.10
...
```

#### Cuando detecta un ataque
```
⚠️ ATAQUE DETECTADO ⚠️
Tipo: Port Scanning
Origen: 192.168.1.50
Descripción: 15 puertos escaneados en 5 segundos
Severidad: MEDIUM
✅ Registrado en base de datos
```

#### Detecciones disponibles

| Tipo de Ataque | Umbral | Severidad |
|----------------|--------|-----------|
| Port Scanning | 10+ puertos en 10s | MEDIUM |
| SYN Flood | 100+ SYN en 1s | CRITICAL |
| ICMP Flood | 50+ ICMP en 1s | MEDIUM |
| SQL Injection | Patrones maliciosos | CRITICAL |
| XSS Attack | Scripts en HTTP | HIGH |

#### Detener el detector
```bash
# Presionar Ctrl+C
# O enviar señal SIGTERM
sudo kill -15 <PID>
```

### SSH Brute Force Monitor

#### Iniciar el monitor
```bash
cd siem-distributed-security/detectors
sudo python3 ssh_bruteforce.py
```

#### Salida esperada
```
🔐 SSH Brute Force Monitor iniciado
📊 Conectado a base de datos: CentralSIEM
📁 Monitoreando: /var/log/auth.log
⏳ Esperando eventos SSH...
```

#### Cuando detecta fuerza bruta
```
⚠️ ATAQUE SSH BRUTE FORCE ⚠️
IP Origen: 192.168.1.75
Intentos fallidos: 8
Usuarios intentados: root, admin, user
Severidad: CRITICAL
✅ Registrado en base de datos
```

#### Configuración

Editar umbrales en `ssh_bruteforce.py`:
```python
FAILED_LOGIN_THRESHOLD = 5      # Intentos antes de alertar
TIME_WINDOW = 300               # Ventana de tiempo (segundos)
```

### Honeypot Multi-servicio

#### Iniciar honeypot
```bash
cd siem-distributed-security/detectors
sudo python3 honeypot.py
```

#### Salida esperada
```
🍯 Honeypot Multi-servicio iniciado
📊 Conectado a base de datos: CentralSIEM

Servicios activos:
  ✅ SSH (puerto 2222)
  ✅ HTTP (puerto 8080)
  ✅ MySQL (puerto 3306)
  ✅ PostgreSQL (puerto 5432)
  ✅ MSSQL (puerto 1433)
  ✅ FTP (puerto 21)

⏳ Esperando conexiones...
```

#### Cuando alguien se conecta
```
🚨 HONEYPOT TRIGGERED 🚨
Servicio: MySQL (3306)
IP Origen: 203.0.113.45
Timestamp: 2026-02-10 15:30:22
Tipo: Database Port Scanning
Severidad: MEDIUM
✅ Registrado en base de datos
```

#### Puertos configurados

| Puerto | Servicio | Banner |
|--------|----------|--------|
| 2222 | SSH | OpenSSH_8.0 |
| 8080 | HTTP | Apache/2.4 |
| 3306 | MySQL | MySQL 5.7 |
| 5432 | PostgreSQL | PostgreSQL 12 |
| 1433 | MSSQL | Microsoft SQL Server |
| 21 | FTP | vsftpd 3.0 |

## Uso del Dashboard Web

### Acceder al dashboard
```bash
# Abrir navegador
firefox http://localhost/siem-dashboard/
```

### Componentes del Dashboard

#### 1. Cabecera
- **Título**: SIEM MONITORING SYSTEM
- **Estado**: Indica si el nodo remoto está online

#### 2. Controles
- **⚠️ Simular Ataque**: Genera una alerta demo en Windows
- **🔒 Archivar Logs**: Mueve alertas de Windows a Fedora

#### 3. Panel Izquierdo: Alertas en Tiempo Real
Muestra alertas activas del nodo Windows (sensor):
- ID de la alerta
- Tipo de ataque
- IP de origen
- Nivel de severidad

#### 4. Panel Derecho: Evidencia Forense
Muestra logs archivados en Fedora:
- Log ID
- Tipo de ataque
- IP de origen
- Fecha de archivado

### Acciones del Dashboard

#### Simular Ataque
1. Click en botón "⚠️ Simular Ataque"
2. El sistema genera una alerta demo
3. Aparece en "Alertas en Tiempo Real"
4. Útil para verificar conectividad

#### Archivar Logs
1. Click en botón "🔒 Archivar Logs"
2. El sistema:
   - Copia alertas de Windows a Fedora
   - Marca alertas como archivadas
   - Ejecuta transacción distribuida 2PC
3. Los logs aparecen en "Evidencia Forense"
4. Las alertas originales se mantienen (no se eliminan)

### Actualización en Tiempo Real
- El dashboard se actualiza cada 3 segundos
- No requiere refrescar la página manualmente
- Las alertas nuevas aparecen automáticamente

## Generador de Ataques (Demo)

### ⚠️ ADVERTENCIA
**SOLO USAR PARA FINES ACADÉMICOS EN TU PROPIA RED**

### Uso básico
```bash
cd siem-distributed-security/scripts
sudo python3 attack_generator.py
```

### Proceso interactivo
```
🎯 GENERADOR DE ATAQUES PARA DEMOSTRACIÓN
⚠️  ADVERTENCIA: Solo usar en red propia para fines académicos

Configuración:
  Target: 127.0.0.1 (localhost)
  Interface: eth0

Ataques a generar:
  1. Port Scanning (Nmap)
  2. SYN Flood
  3. ICMP Flood
  4. SQL Injection
  5. XSS Attack
  6. SSH Brute Force
  7. Honeypot Connections

Escribe 'SI' para continuar o cualquier otra cosa para cancelar: SI

Generando ataques...
[1/7] Port Scanning... ✅
[2/7] SYN Flood... ✅
[3/7] ICMP Flood... ✅
[4/7] SQL Injection... ✅
[5/7] XSS Attack... ✅
[6/7] SSH Brute Force... ✅
[7/7] Honeypot Connections... ✅

✅ Ataques generados exitosamente
📊 Revisa el dashboard para ver las detecciones
```

### Personalizar ataques

Editar `attack_generator.py`:
```python
# Cambiar target
TARGET_IP = "192.168.1.10"  # IP de prueba

# Cambiar intensidad
SYN_FLOOD_COUNT = 200       # Número de paquetes SYN
ICMP_FLOOD_COUNT = 100      # Número de pings

# Cambiar puertos a escanear
SCAN_PORTS = [21, 22, 23, 80, 443, 3306, 5432]
```

## Escenarios de Uso

### Escenario 1: Monitoreo Pasivo

**Objetivo**: Detectar ataques reales en tu red

**Pasos**:
1. Iniciar todos los detectores
   ```bash
   # Terminal 1
   sudo python3 detectors/network_ids.py eth0
   
   # Terminal 2
   sudo python3 detectors/ssh_bruteforce.py
   
   # Terminal 3
   sudo python3 detectors/honeypot.py
   ```

2. Abrir dashboard
   ```bash
   firefox http://localhost/siem-dashboard/
   ```

3. Dejar corriendo y esperar eventos reales
   - Port scans de Internet
   - Intentos de brute force
   - Conexiones a honeypots

### Escenario 2: Demostración Controlada

**Objetivo**: Mostrar el sistema al profesor

**Pasos**:
1. Preparación (5 min antes)
   ```bash
   # Iniciar detectores
   sudo python3 detectors/network_ids.py eth0 &
   sudo python3 detectors/honeypot.py &
   
   # Abrir dashboard
   firefox http://localhost/siem-dashboard/
   ```

2. Durante presentación
   - Explicar arquitectura
   - Mostrar dashboard vacío
   - Ejecutar generador:
     ```bash
     sudo python3 scripts/attack_generator.py
     ```
   - Ver detecciones en tiempo real

3. Archivar logs
   - Click en "Archivar Logs"
   - Explicar transacción distribuida
   - Mostrar logs movidos

### Escenario 3: Ataque Real Externo

**Objetivo**: Demostrar detección desde otra máquina

**Requisitos**: Laptop o VM adicional en la misma red

**Desde máquina atacante**:
```bash
# Port scan
nmap -sS 192.168.1.XXX  # IP de tu Fedora

# O intento SSH
ssh intentos-multiples@192.168.1.XXX

# O conexión a honeypot
telnet 192.168.1.XXX 3306
```

**En el SIEM**:
- Ver detección en tiempo real
- IP real del atacante aparece
- Más impresionante que simulación

### Escenario 4: Análisis Forense

**Objetivo**: Revisar ataques históricos

**Consultas SQL útiles**:
```sql
-- Conectar a BD
sqlcmd -S localhost -U sa -P 'Password' -C

-- Ver todos los ataques
USE CentralSIEM;
SELECT * FROM [SENSOR_REMOTO].[SensorDB].[dbo].[Live_Alerts]
ORDER BY Timestamp DESC;
GO

-- Ataques por tipo
SELECT TipoAtaque, COUNT(*) as Total
FROM [SENSOR_REMOTO].[SensorDB].[dbo].[Live_Alerts]
GROUP BY TipoAtaque;
GO

-- Top IPs atacantes
SELECT IP_Origen, COUNT(*) as Intentos
FROM [SENSOR_REMOTO].[SensorDB].[dbo].[Live_Alerts]
GROUP BY IP_Origen
ORDER BY Intentos DESC;
GO

-- Ataques críticos
SELECT * FROM [SENSOR_REMOTO].[SensorDB].[dbo].[Live_Alerts]
WHERE Severidad = 'CRITICAL'
ORDER BY Timestamp DESC;
GO

-- Logs archivados
SELECT * FROM Forense_Logs
ORDER BY Fecha_Archivado DESC;
GO
```

## Monitoreo del Sistema

### Ver logs en tiempo real

#### Detector network_ids
```bash
# Ver salida en consola (ya corriendo)
# O redirigir a archivo
sudo python3 detectors/network_ids.py eth0 2>&1 | tee ids.log
```

#### Verificar conexiones activas
```bash
# Ver conexiones a honeypots
sudo netstat -tulpn | grep -E '2222|8080|3306|5432|1433|21'

# Ver conexiones SQL Server
sudo netstat -tulpn | grep 1432
```

#### Monitorear uso de recursos
```bash
# CPU y memoria de Python
top -p $(pgrep -f network_ids)

# O con htop
htop -p $(pgrep -f network_ids)
```

### Métricas del sistema

#### Alertas por hora
```sql
SELECT 
    DATEPART(HOUR, Timestamp) as Hora,
    COUNT(*) as Alertas
FROM [SENSOR_REMOTO].[SensorDB].[dbo].[Live_Alerts]
WHERE CAST(Timestamp AS DATE) = CAST(GETDATE() AS DATE)
GROUP BY DATEPART(HOUR, Timestamp)
ORDER BY Hora;
GO
```

#### Severidad de alertas
```sql
SELECT 
    Severidad,
    COUNT(*) as Total,
    CAST(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER() AS DECIMAL(5,2)) as Porcentaje
FROM [SENSOR_REMOTO].[SensorDB].[dbo].[Live_Alerts]
GROUP BY Severidad;
GO
```

## Mantenimiento

### Limpieza de alertas antiguas

```sql
-- Eliminar alertas de más de 30 días
DELETE FROM [SENSOR_REMOTO].[SensorDB].[dbo].[Live_Alerts]
WHERE Timestamp < DATEADD(DAY, -30, GETDATE());
GO

-- O archivar primero
-- (Usar botón del dashboard)
```

### Backup de base de datos

```bash
# Backup completo
sudo /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P 'Password' -C \
  -Q "BACKUP DATABASE [CentralSIEM] TO DISK = '/var/opt/mssql/backup/CentralSIEM.bak'"

# Restaurar si es necesario
sudo /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P 'Password' -C \
  -Q "RESTORE DATABASE [CentralSIEM] FROM DISK = '/var/opt/mssql/backup/CentralSIEM.bak'"
```

### Reiniciar servicios

```bash
# Reiniciar SQL Server
sudo systemctl restart mssql-server

# Reiniciar Apache (dashboard)
sudo systemctl restart httpd

# Reiniciar detectores
sudo pkill -f network_ids
sudo python3 detectors/network_ids.py eth0 &
```

## Mejores Prácticas

### ✅ DO (Hacer)
- Ejecutar detectores con `sudo` o configurar capabilities
- Revisar logs regularmente
- Archivar alertas periódicamente
- Documentar incidentes significativos
- Probar el sistema antes de la demo
- Usar interfaz de red correcta
- Mantener credenciales seguras

### ❌ DON'T (No hacer)
- Exponer honeypots directamente a Internet sin supervisión
- Usar attack_generator contra sistemas de terceros
- Dejar credenciales por defecto en producción
- Ignorar alertas críticas
- Ejecutar en red institucional sin permiso
- Modificar código sin entender el impacto

## Troubleshooting Operacional

### Problema: No se detectan ataques
```bash
# 1. Verificar interfaz
ip link show
sudo tcpdump -i eth0 -c 10

# 2. Generar tráfico de prueba
ping -c 5 google.com

# 3. Ejecutar con interfaz correcta
sudo python3 detectors/network_ids.py <TU_INTERFAZ>
```

### Problema: Dashboard no muestra alertas
```bash
# 1. Verificar BD tiene datos
sqlcmd -S localhost -U sa -P 'Password' -C
SELECT COUNT(*) FROM [SENSOR_REMOTO].[SensorDB].[dbo].[Live_Alerts];
GO

# 2. Verificar logs de Apache
sudo tail -f /var/log/httpd/error_log

# 3. Refrescar dashboard
# (Presionar F5 o Ctrl+R)
```

### Problema: Honeypot "Address already in use"
```bash
# 1. Ver qué usa el puerto
sudo netstat -tulpn | grep :8080

# 2. Matar proceso
sudo kill -9 <PID>

# 3. O cambiar puerto en honeypot.py
```

## Recursos Adicionales

- [Instalación](INSTALACION.md) - Configuración inicial
- [Arquitectura](ARQUITECTURA.md) - Diseño técnico
- [Demostración](DEMOSTRACION.md) - Script para presentar
- [Troubleshooting](TROUBLESHOOTING.md) - Solución de problemas

---

**¿Dudas?** Revisa la documentación completa o abre un issue en GitHub.
