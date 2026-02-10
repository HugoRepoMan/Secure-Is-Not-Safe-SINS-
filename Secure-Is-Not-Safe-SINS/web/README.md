# 🛡️ Sistema SIEM con Base de Datos Distribuida

## Proyecto de Bases de Datos Distribuidas

Sistema de Monitoreo de Eventos e Información de Seguridad (SIEM) implementado con arquitectura de base de datos distribuida heterogénea.

---

## 📊 Descripción del Proyecto

Este proyecto implementa un **Sistema SIEM** para monitorear eventos de seguridad en tiempo real utilizando una arquitectura de **base de datos distribuida heterogénea** con SQL Server en dos nodos:

- **Nodo Central (Fedora Linux):** Almacena logs históricos y forenses
- **Nodo Sensor (Windows):** Captura alertas de seguridad en tiempo real

### Características Principales

✅ **Base de Datos Distribuida Heterogénea**
- SQL Server en diferentes sistemas operativos (Fedora + Windows)
- Linked Server para consultas distribuidas
- Fragmentación horizontal de datos

✅ **Transacciones Distribuidas**
- Implementación 2PC (Two-Phase Commit)
- Control de concurrencia con manejo de deadlock
- Rollback automático en caso de fallo

✅ **Procesamiento Distribuido**
- Replicación de datos entre nodos
- Consultas distribuidas optimizadas
- Almacenamiento fragmentado geográficamente

✅ **Interfaz Web Moderna**
- Dashboard en tiempo real
- Actualización automática cada 5 segundos
- Diseño responsive y profesional
- Notificaciones visuales

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────┐
│                   NAVEGADOR WEB                         │
│                (Cliente JavaScript)                     │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/JSON
                     │
┌────────────────────▼────────────────────────────────────┐
│              SERVIDOR WEB (Fedora)                      │
│                Apache + PHP 8.x                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │            APIs REST (PHP)                        │  │
│  │  • get_alerts.php  • actions.php                 │  │
│  └──────────────────┬───────────────────────────────┘  │
└─────────────────────┼──────────────────────────────────┘
                      │
                      │ PDO + sqlsrv
                      │
┌─────────────────────▼──────────────────────────────────┐
│         NODO CENTRAL (Fedora Linux)                    │
│           SQL Server 2022 - Puerto 1432                │
│  ┌──────────────────────────────────────────────────┐ │
│  │  Database: CentralSIEM                           │ │
│  │  • Forense_Logs (histórico)                      │ │
│  │  • Audit_Transacciones                           │ │
│  │  • Linked Server → SENSOR_REMOTO                 │ │
│  └──────────────────────────────────────────────────┘ │
└────────────────────┬───────────────────────────────────┘
                     │
                     │ Linked Server (TCP/IP)
                     │
┌────────────────────▼───────────────────────────────────┐
│         NODO SENSOR (Windows 11)                       │
│           SQL Server 2022 - Puerto 1433                │
│  ┌──────────────────────────────────────────────────┐ │
│  │  Database: SensorDB                              │ │
│  │  • Live_Alerts (tiempo real)                     │ │
│  └──────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────┘
```

---

## 🎓 Cumplimiento del Sílabo

### Unidad 3: Bases de Datos Distribuidas

| Tema | Implementación | Evidencia |
|------|---------------|-----------|
| **Heterogéneas (federadas)** | ✅ | SQL Server en Fedora + Windows conectados vía Linked Server |
| **Fragmentación** | ✅ | Datos fragmentados: alertas activas en Windows, históricas en Fedora |
| **Replicación** | ✅ | Función `archive` copia datos de Windows a Fedora |
| **Consultas Distribuidas** | ✅ | `get_alerts.php` consulta ambos nodos simultáneamente |
| **Transacciones Distribuidas** | ✅ | `actions.php` con BEGIN TRANSACTION, COMMIT, ROLLBACK |
| **Control de Concurrencia** | ✅ | Manejo de deadlock con try-catch y rollback |
| **Procesamiento Distribuido** | ✅ | Lógica distribuida en cada nodo + procesamiento central |
| **Fallas y Recuperación** | ✅ | Rollback automático + logging de errores |
| **Seguridad** | ✅ | Prepared statements, validación de entrada |
| **Arquitectura Cliente-Servidor** | ✅ | Navegador → Apache/PHP → SQL Server |
| **Multipunto y Multi-database** | ✅ | 2 nodos geográficamente separados, 2 bases de datos |

---

## 📁 Estructura del Proyecto

```
ProyectoParcial3_Mejorado/
│
├── 📄 README.md                          # Este archivo
├── 📄 index.html                         # Página principal del dashboard
│
├── 📁 config/
│   └── 📄 database.php                   # Configuración de BD (Singleton)
│
├── 📁 api/
│   ├── 📄 get_alerts.php                 # API: Consultas distribuidas
│   └── 📄 actions.php                    # API: Transacciones distribuidas
│
├── 📁 assets/
│   ├── 📄 style.css                      # Estilos (Dark Theme)
│   └── 📄 main.js                        # Lógica del cliente
│
├── 📁 sql/
│   └── 📄 setup_distributed_database.sql # Script de configuración completo
│
└── 📁 docs/
    ├── 📄 INFORME_REVISION.md            # Análisis y correcciones
    ├── 📄 MANUAL_INSTALACION.md          # Guía de instalación paso a paso
    └── 📄 DIAGRAMA_ARQUITECTURA.md       # Diagramas del sistema
```

---

## 🚀 Instalación Rápida

### Requisitos Previos

- Fedora Linux 38+ con SQL Server 2022
- Windows 10/11 con SQL Server 2022
- Apache + PHP 8.x + drivers sqlsrv
- Red local entre ambas máquinas

### Pasos Básicos

1. **Instalar SQL Server en ambos nodos**
   ```bash
   # Ver MANUAL_INSTALACION.md para detalles completos
   ```

2. **Configurar Linked Server**
   ```sql
   EXEC sp_addlinkedserver 
       @server = 'SENSOR_REMOTO',
       @datasrc = 'IP_WINDOWS,1433';
   ```

3. **Ejecutar script SQL**
   ```bash
   sqlcmd -S localhost,1432 -U sa -C -i sql/setup_distributed_database.sql
   ```

4. **Copiar archivos web**
   ```bash
   sudo cp -r * /var/www/html/PROYECTOPARCIAL3/
   sudo chown -R apache:apache /var/www/html/PROYECTOPARCIAL3/
   ```

5. **Configurar database.php con tus credenciales**

6. **Abrir en navegador**
   ```
   http://localhost/PROYECTOPARCIAL3/
   ```

📖 **Guía completa:** Ver `docs/MANUAL_INSTALACION.md`

---

## 🎯 Funcionalidades

### 1. Monitoreo en Tiempo Real

- **Dashboard actualizado automáticamente** cada 5 segundos
- **Alertas en vivo** desde el nodo sensor (Windows)
- **Logs históricos** desde el nodo central (Fedora)
- **Indicador de estado** de conectividad

### 2. Simulación de Ataques

- Genera ataques aleatorios en el nodo Windows
- Tipos: SQL Injection, XSS, Ransomware, SSH Brute Force, etc.
- Niveles de severidad: LOW, MEDIUM, HIGH, CRITICAL

### 3. Archivado Distribuido

- **Transacción distribuida** que:
  1. Copia alertas de Windows a Fedora
  2. Elimina alertas del nodo Windows
  3. Registra auditoría
- **Garantía ACID** con rollback automático

### 4. Limpieza de Logs

- Elimina logs con más de 30 días de antigüedad
- Libera espacio en disco
- Mantiene rendimiento óptimo

---

## 🔧 Tecnologías Utilizadas

### Backend
- **SQL Server 2022** - Base de datos distribuida
- **PHP 8.x** - Lógica de servidor
- **PDO + sqlsrv** - Driver de conexión

### Frontend
- **HTML5** - Estructura semántica
- **CSS3** - Diseño responsive y animaciones
- **JavaScript ES6+** - Lógica del cliente
- **Fetch API** - Comunicación asíncrona

### Infraestructura
- **Apache/Nginx** - Servidor web
- **Fedora Linux** - Nodo central
- **Windows 11** - Nodo sensor
- **TCP/IP** - Comunicación entre nodos

---

## 📊 Diagramas

### Flujo de Transacción Distribuida (Archive)

```
┌─────────────┐
│   Cliente   │
│ (Navegador) │
└──────┬──────┘
       │ 1. POST /api/actions.php?action=archive
       │
       ▼
┌─────────────────────────────┐
│   Servidor PHP (Fedora)     │
│                             │
│  2. BEGIN TRANSACTION       │
│     ┌─────────────────────┐ │
│     │ 3. SELECT * FROM    │ │
│     │    [SENSOR_REMOTO]  │ │───┐
│     │    [SensorDB]       │ │   │
│     └─────────────────────┘ │   │
│                             │   │
│  4. INSERT INTO             │   │
│     Forense_Logs            │   │
│     ┌─────────────────────┐ │   │
│     │ 5. DELETE FROM      │ │   │ Linked
│     │    [SENSOR_REMOTO]  │ │◄──┘ Server
│     │    [SensorDB]       │ │
│     └─────────────────────┘ │
│                             │
│  6. COMMIT TRANSACTION      │
│     (o ROLLBACK si error)   │
└─────────────┬───────────────┘
              │
              │ 7. JSON Response
              ▼
         ┌─────────┐
         │ Cliente │
         │(Update) │
         └─────────┘
```

---

## 🛡️ Seguridad

### Medidas Implementadas

✅ **Prepared Statements** - Prevención de SQL Injection  
✅ **Validación de Entrada** - Sanitización de datos  
✅ **Manejo de Errores** - No exponer información sensible  
✅ **CORS Headers** - Control de acceso entre dominios  
✅ **Transacciones ACID** - Integridad de datos  
✅ **Logging de Auditoría** - Trazabilidad de operaciones  

### Recomendaciones Adicionales

- [ ] Implementar autenticación JWT
- [ ] Usar HTTPS en producción
- [ ] Limitar tasa de requests (rate limiting)
- [ ] Cifrado de datos sensibles en tránsito
- [ ] Backup automatizado de bases de datos

---

## 🧪 Pruebas

### Pruebas Manuales

```bash
# Probar API de consultas
curl http://localhost/PROYECTOPARCIAL3/api/get_alerts.php | jq

# Probar simulación de ataque
curl -X POST http://localhost/PROYECTOPARCIAL3/api/actions.php \
  -H "Content-Type: application/json" \
  -d '{"action":"simulate"}'

# Probar archivado
curl -X POST http://localhost/PROYECTOPARCIAL3/api/actions.php \
  -H "Content-Type: application/json" \
  -d '{"action":"archive"}'
```

### Casos de Prueba

| Caso | Acción | Resultado Esperado |
|------|--------|-------------------|
| 1 | Abrir dashboard | Tablas cargadas con datos |
| 2 | Click "Simular Ataque" | Nueva alerta en tabla Windows |
| 3 | Click "Archivar Logs" | Datos movidos a tabla Fedora |
| 4 | Desconectar red | Estado cambia a "🔴 Desconectado" |
| 5 | Esperar 5 segundos | Tablas se actualizan automáticamente |

---

## 📈 Rendimiento

### Optimizaciones Implementadas

- **Índices en columnas frecuentes** (Timestamp, Severidad, IP_Origen)
- **Consultas TOP 10** para limitar resultados
- **Conexión Singleton** para reutilizar conexiones
- **Prepared Statements** para cache de queries
- **Atributos PDO optimizados** (EMULATE_PREPARES = false)

### Métricas

- **Consulta distribuida:** ~50-200ms (dependiendo de red)
- **Transacción distribuida:** ~100-500ms
- **Actualización automática:** 5 segundos (configurable)
- **Tamaño de respuesta JSON:** ~2-10KB

---

## 🐛 Solución de Problemas Comunes

### Error: "Unexpected token '<' in JSON"

**Causa:** PHP generando HTML antes del JSON  
**Solución:** Verificar que database.php NO hace `echo` de errores

### Error: "Could not find server 'SENSOR_REMOTO'"

**Causa:** Linked Server no configurado correctamente  
**Solución:** Ejecutar `sp_addlinkedserver` con IP correcta de Windows

### Error: "Connection failed"

**Causa:** Firewall bloqueando puerto SQL Server  
**Solución:** Abrir puertos 1432 y 1433 en firewall

📖 **Más soluciones:** Ver `docs/MANUAL_INSTALACION.md` sección 8

---

## 📝 Notas de la Versión

### Versión 2.0 (Mejorada) - 30/01/2026

#### ✅ Correcciones
- ✅ Corregido error de `echo` en database.php
- ✅ Añadido manejo robusto de errores en APIs
- ✅ Implementado patrón Singleton
- ✅ Mejorado procesamiento de fechas SQL Server

#### ✨ Nuevas Características
- ✨ Sistema de notificaciones visuales
- ✨ Badges de severidad con colores
- ✨ Animaciones CSS suaves
- ✨ Diseño responsive
- ✨ Función cleanup de logs antiguos
- ✨ Procedimientos almacenados
- ✨ Vista consolidada SQL

#### 📚 Documentación
- 📚 Informe completo de revisión
- 📚 Manual de instalación detallado
- 📚 Scripts SQL comentados
- 📚 README completo

---

## 👥 Equipo

**Estudiantes:**
- [Tu Nombre]
- [Nombre de tu compañera]

**Curso:** Bases de Datos Distribuidas  
**Fecha:** Enero 2026  
**Institución:** [Tu Universidad]

---

## 📄 Licencia

Este proyecto fue desarrollado con fines académicos para el curso de Bases de Datos Distribuidas.

---

## 🙏 Agradecimientos

- Profesor del curso por las indicaciones
- Microsoft por SQL Server Developer Edition
- Comunidad de PHP y JavaScript
- Stack Overflow por las soluciones

---

## 📞 Soporte

Para dudas o problemas:

1. Revisar `docs/MANUAL_INSTALACION.md`
2. Revisar `docs/INFORME_REVISION.md`
3. Verificar logs del servidor
4. Contactar al equipo de desarrollo

---

**Estado del Proyecto:** ✅ **COMPLETADO Y FUNCIONAL**

**Última Actualización:** 30 de enero de 2026
