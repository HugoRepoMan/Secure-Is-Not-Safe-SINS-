# 📖 Guía de Instalación Detallada

## Instalación Paso a Paso

### Prerrequisitos

1. **Fedora Linux**: SQL Server 2022 instalado en puerto 1432
2. **Windows**: SQL Server 2022 instalado en puerto 1433
3. **Red**: Ambos en misma LAN o conectados vía ZeroTier

### Instalación en Fedora
```bash
# 1. Clonar repositorio
git clone https://github.com/HugoRepoMan/Secure-Is-Not-Safe-SINS-.git
cd Secure-Is-Not-Safe-SINS-

# 2. Ejecutar instalador
sudo ./scripts/install.sh

# 3. Configurar base de datos
sqlcmd -S localhost,1432 -U sa -P 'PASSWORD' -i sql/setup_fedora.sql

# 4. Configurar Linked Server (editar IP primero)
nano sql/setup_linked_server.sql
sqlcmd -S localhost,1432 -U sa -P 'PASSWORD' -i sql/setup_linked_server.sql

# 5. Configurar honeypot
cp detectors/config.example.py detectors/config.py
nano detectors/config.py  # Editar IP de Windows
```

### Instalación en Windows
```cmd
REM 1. Ejecutar script SQL
sqlcmd -S localhost -U sa -P "PASSWORD" -i sql\setup_windows.sql

REM 2. Configurar firewall
powershell -Command "New-NetFirewallRule -DisplayName 'SQL Server' -Direction Inbound -Protocol TCP -LocalPort 1433 -Action Allow"
```

## Verificación
```bash
# Probar Linked Server
sqlcmd -S localhost,1432 -U sa -P 'PASSWORD' -C -Q \
  "SELECT * FROM [SENSOR_REMOTO].[SensorDB].[dbo].[Live_Alerts]"

# Acceder a dashboard
firefox http://localhost/PROYECTOPARCIAL3/
```
