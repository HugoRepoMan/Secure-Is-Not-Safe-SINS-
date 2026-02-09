# 🎬 Guía de Demostración

## Script de Presentación (5 minutos)

### Minuto 1: Introducción
> "Presentamos un Sistema SIEM con Base de Datos Distribuida heterogénea implementado con SQL Server en Fedora Linux y Windows 11."

### Minuto 2: Arquitectura
> "Dos nodos: Central en Fedora (puerto 1432) y Sensor en Windows (puerto 1433), conectados mediante Linked Server sobre ZeroTier VPN."

**[Mostrar dashboard]**

### Minuto 3: Detección Real
> "Detectamos ataques REALES mediante honeypots - servicios señuelo."

**[Ejecutar]**
```bash
sudo python3 detectors/attack_generator.py
```

### Minuto 4: Consultas Distribuidas
> "El dashboard consulta datos del sensor Windows mediante Linked Server de forma transparente."

**[Mostrar alertas apareciendo]**

### Minuto 5: Transacción Distribuida
> "Archivamos los logs mediante operación Copy-Delete del nodo temporal al permanente."

**[Click en "Archivar Logs"]**

## Conceptos Clave

- **Fragmentación**: Datos separados por función (operacional vs analítico)
- **Replicación**: Copy-Delete entre nodos
- **Heterogeneidad**: Linux + Windows, diferentes puertos
- **Consultas distribuidas**: Linked Server transparente
