# 🛡️ Sistema SIEM Distribuido con Detección de Ataques Reales

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![SQL Server](https://img.shields.io/badge/SQL%20Server-2019+-red.svg)](https://www.microsoft.com/sql-server)

## 📋 Descripción del Proyecto

Sistema de Información de Seguridad y Gestión de Eventos (SIEM) distribuido que combina:
- **Base de datos distribuida heterogénea** (SQL Server en Windows + Fedora)
- **Detección de ataques reales** (IDS, Honeypots, análisis de logs)
- **Dashboard web en tiempo real** para monitoreo
- **Arquitectura fragmentada** con replicación y archivado automático

### 🎯 Objetivo Académico
Demostrar conceptos avanzados de bases de datos distribuidas mediante un sistema funcional de ciberseguridad.

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                    SISTEMA SIEM DISTRIBUIDO                  │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐           ┌──────────────┐                │
│  │ NODO FEDORA  │◄─────────►│ NODO WINDOWS │                │
│  │  (Master)    │  Linked   │  (Sensor)    │                │
│  │              │  Server   │              │                │
│  │ SQL Server   │           │ SQL Server   │                │
│  │ Puerto 1432  │           │  Simulado    │                │
│  └──────┬───────┘           └──────┬───────┘                │
│         │                          │                         │
│  ┌──────▼───────┐           ┌──────▼───────┐                │
│  │ Forense_Logs │           │ Live_Alerts  │                │
│  │ (Archivo)    │           │ (Tiempo Real)│                │
│  └──────────────┘           └──────────────┘                │
│         ▲                          │                         │
│         │                          │                         │
│         │     ┌────────────────────▼──────┐                 │
│         │     │   Dashboard Web (PHP)     │                 │
│         └─────┤   - Visualización          │                 │
│               │   - Control de acciones    │                 │
│               └────────────────────────────┘                 │
│                          │                                    │
│  ┌───────────────────────▼──────────────────────┐           │
│  │        DETECTORES DE ATAQUES REALES          │           │
│  ├──────────────────────────────────────────────┤           │
│  │ • Network IDS (Scapy)                        │           │
│  │ • SSH Brute Force Monitor                    │           │
│  │ • Honeypot Multi-servicio                    │           │
│  │ • Attack Generator (Demo)                    │           │
│  └──────────────────────────────────────────────┘           │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Estructura del Repositorio

```
siem-distributed-security/
│
├── 📂 dashboard/              # Dashboard web PHP
│   ├── index.html            # Interfaz principal
│   ├── assets/
│   │   ├── style.css         # Estilos del dashboard
│   │   └── main.js           # Lógica JavaScript
│   ├── api/
│   │   ├── get_alerts.php    # API para obtener alertas
│   │   └── actions.php       # API para acciones (simular/archivar)
│   └── config/
│       └── database.php      # Configuración de BD
│
├── 📂 detectors/              # Detectores de ataques en Python
│   ├── network_ids.py        # IDS de red (Scapy)
│   ├── ssh_bruteforce.py     # Monitor SSH
│   └── honeypot.py           # Honeypot multi-puerto
│
├── 📂 database/               # Scripts SQL
│   └── setup_real_attacks.sql # Schema de base de datos
│
├── 📂 scripts/                # Herramientas auxiliares
│   ├── install.sh            # Instalador de dependencias
│   └── attack_generator.py   # Generador de ataques demo
│
├── 📂 docs/                   # Documentación
│   ├── INSTALACION.md        # Guía de instalación completa
│   ├── USO.md                # Manual de uso
│   └── ARQUITECTURA.md       # Diseño técnico detallado
│
├── README.md                  # Este archivo
├── LICENSE                    # Licencia MIT
└── .gitignore                # Archivos ignorados por Git
```

## 🚀 Inicio Rápido

### Prerrequisitos

- **Sistema Operativo**: Fedora Linux (o similar)
- **Base de datos**: SQL Server 2019+ en ambos nodos
- **Python**: 3.8 o superior
- **Permisos**: Root/sudo para captura de paquetes
- **Red**: Conectividad entre nodos Fedora y Windows

### Instalación en 3 Pasos

#### 1. Clonar el repositorio
```bash
git clone https://github.com/TU_USUARIO/siem-distributed-security.git
cd siem-distributed-security
```

#### 2. Instalar dependencias
```bash
cd scripts
sudo chmod +x install.sh
sudo ./install.sh
```

#### 3. Configurar base de datos
```bash
# Editar credenciales en cada detector
nano detectors/network_ids.py
nano detectors/ssh_bruteforce.py
nano detectors/honeypot.py

# Configurar dashboard
nano dashboard/config/database.php
```

Ver la [**Guía de Instalación Completa**](docs/INSTALACION.md) para más detalles.

## 💻 Uso del Sistema

### Ejecutar Detectores

```bash
# Terminal 1: Detector de red
sudo python3 detectors/network_ids.py eth0

# Terminal 2: Monitor SSH
sudo python3 detectors/ssh_bruteforce.py

# Terminal 3: Honeypot
sudo python3 detectors/honeypot.py
```

### Acceder al Dashboard

1. Abrir navegador: `http://localhost/siem-distributed-security/dashboard/`
2. Ver alertas en tiempo real
3. Usar botones para:
   - ⚠️ Simular ataque (genera alerta demo)
   - 🔒 Archivar logs (mueve datos de Windows a Fedora)

### Generar Ataques Demo

```bash
# Solo para demostración académica
sudo python3 scripts/attack_generator.py
```

Ver el [**Manual de Uso**](docs/USO.md) para escenarios completos.

## 🎯 Ataques Detectados

El sistema detecta **7 tipos de ataques reales**:

| Tipo | Descripción | Severidad | Detector |
|------|-------------|-----------|----------|
| 🔍 **Port Scanning** | Escaneo de puertos con Nmap | MEDIUM | network_ids |
| 💥 **SYN Flood** | Ataque de denegación de servicio | CRITICAL | network_ids |
| 📡 **ICMP Flood** | Flooding de pings | MEDIUM | network_ids |
| 💉 **SQL Injection** | Inyección SQL en HTTP | CRITICAL | network_ids |
| 🔗 **XSS Attack** | Cross-Site Scripting | HIGH | network_ids |
| 🔐 **SSH Brute Force** | Fuerza bruta en SSH | CRITICAL | ssh_bruteforce |
| 🍯 **Honeypot Trigger** | Conexión a servicio señuelo | MEDIUM-HIGH | honeypot |

## 📊 Conceptos de BD Distribuida Implementados

✅ **Fragmentación de datos**
- Alertas activas en nodo Windows (sensor remoto)
- Logs históricos en nodo Fedora (forense)

✅ **Replicación**
- Archivado distribuido con transacciones 2PC
- Linked Server para consultas remotas

✅ **Consultas distribuidas**
- Dashboard consulta ambos nodos simultáneamente
- JOIN entre tablas remotas

✅ **Transacciones distribuidas**
- Archivado con COMMIT en ambos nodos
- Rollback automático en caso de fallo

✅ **Control de concurrencia**
- Bloqueos optimistas en alertas
- Timestamps para evitar conflictos

✅ **Heterogeneidad**
- Windows + Linux con mismo SGBD
- Diferentes versiones y configuraciones

## 🎓 Justificación Académica

Este proyecto cumple **100% del sílabo** de Bases de Datos Distribuidas:

1. ✅ Arquitectura distribuida heterogénea
2. ✅ Fragmentación horizontal (alertas vs archivo)
3. ✅ Replicación asíncrona (archivado)
4. ✅ Consultas distribuidas (dashboard)
5. ✅ Transacciones distribuidas (2PC)
6. ✅ Procesamiento distribuido (detectores)
7. ✅ Seguridad (detección de amenazas)

**PLUS**: Aplicación real de ciberseguridad, IDS/IPS, honeypots.

## 🔧 Tecnologías Utilizadas

### Backend
- **Python 3.8+**: Detectores de ataques
- **Scapy**: Captura y análisis de paquetes
- **pymssql**: Conexión a SQL Server
- **PHP 7.4+**: API del dashboard

### Base de Datos
- **SQL Server 2019+**: Nodos distribuidos
- **Linked Servers**: Consultas remotas
- **Transacciones 2PC**: Archivado distribuido

### Frontend
- **HTML5/CSS3**: Interfaz del dashboard
- **JavaScript vanilla**: Sin frameworks
- **AJAX**: Actualización en tiempo real

### Sistema Operativo
- **Fedora Linux**: Nodo principal
- **Windows Server** (simulado): Nodo sensor

## 🧪 Demostración para el Profesor

### Escenario Completo (10 minutos)

1. **Preparación** (2 min)
   - Iniciar detectores
   - Abrir dashboard
   - Mostrar arquitectura

2. **Demo en vivo** (5 min)
   - Ejecutar `attack_generator.py`
   - Ver detecciones en tiempo real
   - Mostrar alertas en dashboard

3. **Archivado** (2 min)
   - Click en "Archivar Logs"
   - Explicar transacción distribuida
   - Mostrar datos movidos entre nodos

4. **Opcional: Ataque real** (1 min)
   - Desde otra máquina: `nmap <IP_FEDORA>`
   - Ver detección con IP real

Ver [**Guía de Demostración**](docs/DEMOSTRACION.md) con script completo.

## 🔒 Consideraciones de Seguridad

⚠️ **IMPORTANTE**:
- Solo usar en red privada/académica
- NO atacar sistemas de terceros
- Informar al administrador de red
- Solo fines educativos

✅ **Buenas prácticas**:
- Documentar todos los ataques de prueba
- Configurar firewall correctamente
- Supervisar honeypots si están expuestos
- Mantener logs de actividades

## 🐛 Solución de Problemas

### Error común: "Permission denied"
```bash
sudo python3 detectors/network_ids.py eth0
```

### Error: "Cannot connect to database"
```bash
# Verificar SQL Server
sudo systemctl status mssql-server

# Probar conexión
sqlcmd -S localhost,1432 -U sa -P 'Password' -C -Q "SELECT 1"
```

### No se detectan ataques
```bash
# Verificar interfaz correcta
ip link show
sudo python3 detectors/network_ids.py <TU_INTERFAZ>
```

Ver [**Troubleshooting completo**](docs/TROUBLESHOOTING.md).

## 📚 Documentación Adicional

- [📖 Guía de Instalación](docs/INSTALACION.md)
- [📘 Manual de Uso](docs/USO.md)
- [📗 Arquitectura Técnica](docs/ARQUITECTURA.md)
- [📕 Guía de Demostración](docs/DEMOSTRACION.md)
- [🔧 Troubleshooting](docs/TROUBLESHOOTING.md)

## 🤝 Contribuciones

Este es un proyecto académico. Si encuentras mejoras o bugs:

1. Fork el repositorio
2. Crea una rama: `git checkout -b feature/mejora`
3. Commit: `git commit -m 'Añadir mejora'`
4. Push: `git push origin feature/mejora`
5. Abre un Pull Request

## ✍️ Autores

- **Hugo Armijos** - Desarrollo principal
- **Shadya Reyes** - Colaboración

**Institución**: Universidad de las Fuerzas Armadas ESPE sede Santo Domingo   
**Curso**: Bases de Datos Distribuidas  
**Profesor**: Ing. Kevin Chuquitarco
**Fecha**: Febrero 2026

## 🙏 Agradecimientos

- Profesor Ing.Kevin Chuquitarco por la guía en el curso
- Comunidad de Scapy por la documentación
- Microsoft SQL Server por las herramientas
- Compañeros de clase por el feedback


⭐ Si este proyecto te ayudó, considera darle una estrella en GitHub

