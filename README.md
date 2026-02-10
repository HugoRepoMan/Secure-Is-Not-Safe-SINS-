# 🛡️ SIEM con Base de Datos Distribuida

Sistema de Monitoreo de Eventos e Información de Seguridad (SIEM) implementado con arquitectura de base de datos distribuida heterogénea usando SQL Server en Fedora Linux y Windows.

[![GitHub](https://img.shields.io/badge/GitHub-SIEM--Distribuido-blue?logo=github)](https://github.com/HugoRepoMan/Secure-Is-Not-Safe-SINS-)

## 📋 Tabla de Contenidos

- [Características](#características)
- [Arquitectura](#arquitectura)
- [Requisitos](#requisitos)
- [Instalación Rápida](#instalación-rápida)
- [Uso](#uso)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Demostración](#demostración)
- [Autores](#autores)

## ✨ Características

- ✅ **Base de Datos Distribuida Heterogénea** (Linux + Windows)
- ✅ **Linked Server** para consultas distribuidas transparentes
- ✅ **Fragmentación horizontal** por función (temporal vs permanente)
- ✅ **Replicación de datos** con operaciones Copy-Delete
- ✅ **Detección de ataques reales** con honeypots
- ✅ **Dashboard web** en tiempo real
- ✅ **Comunicación segura** vía ZeroTier VPN
- ✅ **Análisis forense** con cadena de custodia

## 🏗️ Arquitectura
```
┌─────────────────────────────────────────────────────────────┐
│                    ARQUITECTURA DISTRIBUIDA                  │
└─────────────────────────────────────────────────────────────┘

┌──────────────────────┐         ZeroTier VPN        ┌──────────────────────┐
│   NODO CENTRAL       │◄────────────────────────────►│    NODO SENSOR       │
│   (Fedora Linux)     │                              │    (Windows 11)      │
├──────────────────────┤                              ├──────────────────────┤
│ SQL Server 2022      │                              │ SQL Server 2022      │
│ Puerto: 1432         │                              │ Puerto: 1433         │
│                      │                              │                      │
│ Base de Datos:       │                              │ Base de Datos:       │
│ └─ CentralSIEM       │      Linked Server           │ └─ SensorDB          │
│    └─ Forense_Logs   │◄─────────────────────────────│    └─ Live_Alerts    │
│    └─ Audit_Trans... │                              │                      │
│                      │                              │ Honeypots:           │
│ Apache + PHP         │                              │ - SSH (2222)         │
│ Dashboard Web        │                              │ - HTTP (8080)        │
│                      │                              │ - MySQL (3306)       │
│ IP: 10.0.90.43       │                              │ IP: 10.0.90.66       │
└──────────────────────┘                              └──────────────────────┘
```

### Flujo de Datos

1. **Captura**: Honeypots detectan ataques → Guardan en `Live_Alerts` (Windows)
2. **Consulta**: Dashboard consulta via Linked Server → Muestra alertas en tiempo real
3. **Archivado**: Operación distribuida → Copia a `Forense_Logs` (Fedora) → Elimina de Windows
4. **Análisis**: Logs permanentes en Fedora para análisis forense

## 📦 Requisitos

### Nodo Central (Fedora)
- Fedora Linux 38+
- SQL Server 2022 para Linux
- Apache 2.4+
- PHP 8.0+ con extensiones sqlsrv
- Python 3.9+ con pymssql, scapy, requests

### Nodo Sensor (Windows)
- Windows 10/11
- SQL Server 2022 Developer/Express
- ZeroTier (opcional, para conexión remota)

### Red
- Ambos nodos en la misma red (LAN o ZeroTier VPN)
- Puertos abiertos: 1432, 1433, 80, 2222, 8080, 3306, 5432, 21

## 🚀 Instalación Rápida

### 1. Clonar repositorio
```bash
git clone https://github.com/HugoRepoMan/Secure-Is-Not-Safe-SINS-.git
cd Secure-Is-Not-Safe-SINS-
```

### 2. Ejecutar instalador (Fedora)
```bash
sudo chmod +x scripts/install.sh
sudo ./scripts/install.sh
```

### 3. Configurar SQL Server en Fedora
```bash
# Crear base de datos central
sqlcmd -S localhost,1432 -U sa -P 'TU_PASSWORD' -i sql/setup_fedora.sql
```

### 4. Configurar SQL Server en Windows
```cmd
REM Crear base de datos sensor
sqlcmd -S localhost -U sa -P "TU_PASSWORD" -i sql\setup_windows.sql
```

### 5. Configurar Linked Server (Fedora)
```bash
# Editar sql/setup_linked_server.sql con la IP de Windows
nano sql/setup_linked_server.sql

# Ejecutar
sqlcmd -S localhost,1432 -U sa -P 'TU_PASSWORD' -i sql/setup_linked_server.sql
```

### 6. Configurar detectores
```bash
# Copiar configuración de ejemplo
cp detectors/config.example.py detectors/config.py

# Editar con IP real de Windows
nano detectors/config.py
```

### 7. Iniciar honeypot
```bash
sudo python3 detectors/honeypot.py
```

### 8. Acceder al dashboard
```
http://localhost/PROYECTOPARCIAL3/
```

## 📖 Uso

### Generar ataques de prueba
```bash
cd detectors
sudo python3 attack_generator.py
```

### Archivar logs

1. Abrir dashboard: `http://localhost/PROYECTOPARCIAL3/`
2. Ver alertas en tabla "Sensor Windows"
3. Click en botón **"🔒 Archivar Logs"**
4. Logs se mueven a tabla "Vault Fedora"

### Ver logs en base de datos
```bash
# Alertas activas en Windows
sqlcmd -S localhost,1432 -U sa -P 'PASSWORD' -C -Q \
  "SELECT * FROM [SENSOR_REMOTO].[SensorDB].[dbo].[Live_Alerts]"

# Logs archivados en Fedora
sqlcmd -S localhost,1432 -U sa -P 'PASSWORD' -Q \
  "SELECT * FROM Forense_Logs"
```

## 📁 Estructura del Proyecto
```
├── detectors/              # Detectores de ataques
│   ├── honeypot.py         # Honeypot multi-servicio
│   ├── attack_generator.py # Generador de ataques de prueba
│   └── config.example.py   # Configuración de ejemplo
├── sql/                    # Scripts SQL
│   ├── setup_fedora.sql    # Configuración nodo central
│   ├── setup_windows.sql   # Configuración nodo sensor
│   └── setup_linked_server.sql # Linked Server
├── web/                    # Aplicación web
│   ├── index.html          # Dashboard principal
│   ├── config/             # Configuración PHP
│   ├── api/                # APIs REST
│   └── assets/             # CSS, JS, imágenes
├── scripts/                # Scripts de instalación
│   └── install.sh          # Instalador automático
├── docs/                   # Documentación adicional
│   ├── INSTALL.md          # Guía de instalación detallada
│   ├── API.md              # Documentación de APIs
│   └── DEMO.md             # Guía de demostración
└── README.md               # Este archivo
```

## 🎬 Demostración

Ver [docs/DEMO.md](docs/DEMO.md) para el script completo de presentación.

### Demostración rápida (5 minutos)

1. **Mostrar arquitectura**: Dashboard con 2 tablas (Windows + Fedora)
2. **Generar ataques**: `sudo python3 detectors/attack_generator.py`
3. **Observar detección**: Alertas aparecen en tiempo real
4. **Archivar logs**: Click en botón, datos se mueven entre nodos
5. **Explicar conceptos**: Fragmentación, replicación, consultas distribuidas

## 👥 Autores

- **Hugo Armijos** - Nodo Central (Fedora) - [GitHub](https://github.com/HugoRepoMan)
- **Shadya Reyes** - Nodo Sensor (Windows)

## 📚 Cumplimiento del Sílabo

✅ Bases de datos heterogéneas (federadas)  
✅ Fragmentación y particionamiento horizontal  
✅ Replicación de datos  
✅ Consultas distribuidas (Linked Server)  
✅ Transacciones distribuidas  
✅ Control de concurrencia  
✅ Procesamiento distribuido  
✅ Seguridad (Prepared Statements, honeypots)  
✅ Arquitectura Cliente-Servidor  

## 📄 Licencia

Proyecto académico - Universidad De las fuerzas Armadas ESPE
Bases de Datos Distribuidas - Febrero 2026

## 🙏 Agradecimientos

- Profesor: Inge. Kevin Jair Chucquitarco Velasco
- Curso: Bases de Datos Distribuidas
- Tecnologías: Microsoft SQL Server, Apache, PHP, Python
