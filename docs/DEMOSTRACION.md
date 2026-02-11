# 🎥 Guía de Demostración para el Profesor

## ⏱️ Timing: 10-15 minutos total

## Preparación (5 minutos ANTES de la presentación)

### 1. Verificar que todo funciona
```bash
# Verificar SQL Server
sudo systemctl status mssql-server

# Verificar Apache
sudo systemctl status httpd
```

### 2. Iniciar detectores
```bash
# Terminal 1: Network IDS
cd ~/siem-distributed-security/detectors
sudo python3 network_ids.py eth0 &

# Terminal 2: Honeypot
sudo python3 honeypot.py &
```

### 3. Abrir dashboard
```bash
firefox http://localhost/siem-dashboard/
```

### 4. Tener listo el generador
```bash
# En otra terminal, navegar al directorio
cd ~/siem-distributed-security/scripts
# NO ejecutar todavía
```

## Script de Presentación

### PARTE 1: Introducción (2 minutos)

**Lo que vas a decir:**

> "Buenos días/tardes profesor. Hoy presentamos nuestro Sistema SIEM Distribuido con detección de ataques reales.
>
> El proyecto implementa una arquitectura de base de datos distribuida heterogénea usando SQL Server en dos nodos: uno en Fedora (servidor central) y otro simulando Windows (sensor remoto).
>
> Pero lo especial de nuestro proyecto es que no solo cumple con los requisitos del sílabo de bases de datos distribuidas, sino que detecta ATAQUES REALES de ciberseguridad."

**Mostrar mientras hablas:**
- Diagrama de arquitectura (tener imagen preparada)
- Dashboard vacío o con pocas alertas

### PARTE 2: Arquitectura (2 minutos)

**Lo que vas a decir:**

> "La arquitectura implementa:
>
> 1. **Fragmentación horizontal**: Las alertas activas se almacenan en el nodo Windows (sensor remoto), mientras que los logs archivados están en Fedora (forense).
>
> 2. **Linked Server**: Configuramos un linked server para realizar consultas distribuidas entre ambos nodos.
>
> 3. **Transacciones distribuidas**: Cuando archivamos logs, usamos transacciones 2PC para garantizar consistencia entre nodos.
>
> 4. **Procesamiento distribuido**: Los detectores de ataques procesan datos localmente y los envían a la base de datos distribuida."

**Mostrar mientras hablas:**
- Conexión de linked server (opcional, en terminal):
```sql
SELECT * FROM [SENSOR_REMOTO].[SensorDB].[sys].[tables];
GO
```

### PARTE 3: Componentes de Detección (2 minutos)

**Lo que vas a decir:**

> "Implementamos tres tipos de detectores:
>
> 1. **Network IDS**: Captura tráfico de red en tiempo real usando Scapy. Detecta:
>    - Port scanning
>    - SYN floods
>    - ICMP floods
>    - SQL injection en tráfico HTTP
>    - Ataques XSS
>
> 2. **SSH Brute Force Monitor**: Analiza logs de autenticación para detectar intentos de fuerza bruta en SSH.
>
> 3. **Honeypot**: Servicios señuelo que atraen atacantes. Cualquier conexión a estos puertos es automáticamente sospechosa."

**Mostrar mientras hablas:**
- Terminal con detector corriendo
- Ver líneas de monitoreo

### PARTE 4: Demostración en Vivo (5 minutos)

**Lo que vas a decir:**

> "Ahora vamos a demostrar el sistema detectando ataques reales. Ejecutaré nuestro generador de ataques que simula 7 tipos diferentes de amenazas."

**Ejecutar:**
```bash
sudo python3 attack_generator.py
# Escribir: SI
```

**Mientras se ejecuta, explicar:**
> "El generador está lanzando:
> - Port scans con Nmap
> - Ataques de denegación de servicio
> - Intentos de inyección SQL
> - Intentos de XSS
> - Brute force en SSH
> - Conexiones a nuestros honeypots"

**Cambiar a la terminal del detector:**
> "Como pueden ver, el detector está capturando estos ataques en tiempo real."

**Leer alguna detección:**
> "Aquí detectó un Port Scanning desde la IP [X], escaneó [N] puertos, severidad MEDIUM."

**Cambiar al dashboard:**
> "Y automáticamente se registran en nuestra base de datos distribuida."

**Refrescar (F5) si es necesario.**

**Señalar la tabla:**
> "Aquí vemos las alertas en tiempo real del nodo Windows. Cada alerta muestra:
> - Tipo de ataque
> - IP de origen
> - Nivel de severidad
> - Descripción"

### PARTE 5: Archivado Distribuido (2 minutos)

**Lo que vas a decir:**

> "Ahora demostraré la transacción distribuida. Vamos a archivar estas alertas, moviéndolas del nodo Windows al nodo Fedora."

**Hacer clic en "🔒 Archivar Logs"**

**Mientras procesa:**
> "El sistema está ejecutando una transacción distribuida de dos fases:
> 1. INSERT en la tabla Forense_Logs de Fedora
> 2. UPDATE en Live_Alerts de Windows marcándolas como archivadas
> 3. Si ambas operaciones tienen éxito, hace COMMIT en ambos nodos
> 4. Si alguna falla, hace ROLLBACK en ambos"

**Cuando termine:**
> "Y ahora vemos los logs archivados en el panel derecho - Evidencia Forense del nodo Fedora."

### PARTE 6: Consulta Distribuida (1 minuto) [OPCIONAL]

**Si tienes tiempo, mostrar en terminal:**

```bash
sqlcmd -S localhost -U sa -P 'TuPassword' -C
```

```sql
-- Consulta distribuida
SELECT 
    L.ID,
    L.TipoAtaque,
    L.IP_Origen,
    L.Timestamp,
    'Activa' as Estado
FROM [SENSOR_REMOTO].[SensorDB].[dbo].[Live_Alerts] L
WHERE L.Archivado = 0
UNION ALL
SELECT 
    F.AlertID,
    F.TipoAtaque,
    F.IP_Origen,
    F.Timestamp,
    'Archivada' as Estado
FROM [CentralSIEM].[dbo].[Forense_Logs] F
ORDER BY Timestamp DESC;
GO
```

**Explicar:**
> "Esta es una consulta distribuida que une datos de ambos nodos - alertas activas de Windows y archivadas de Fedora - en un solo resultado."

### PARTE 7: Conclusión (1 minuto)

**Lo que vas a decir:**

> "En resumen, nuestro proyecto implementa:
>
> ✅ Base de datos distribuida heterogénea
> ✅ Fragmentación de datos
> ✅ Replicación mediante archivado
> ✅ Consultas distribuidas con linked server
> ✅ Transacciones distribuidas con 2PC
> ✅ Procesamiento distribuido
> ✅ Control de concurrencia
>
> Y como plus, detecta ataques reales de ciberseguridad, demostrando una aplicación práctica de estos conceptos.
>
> ¿Alguna pregunta?"

## Posibles Preguntas del Profesor

### P: "¿Cómo garantizan la consistencia en la transacción distribuida?"

**R:** "Usamos el protocolo de commit de dos fases (2PC). Primero, ambos nodos confirman que pueden realizar la operación (fase de preparación). Solo si ambos responden afirmativamente, se ejecuta el commit en ambos nodos. Si alguno falla, se hace rollback en ambos, garantizando que ambos nodos queden en estado consistente."

### P: "¿Qué pasa si el nodo Windows cae durante una transacción?"

**R:** "El linked server detectaría el fallo y devolvería un error. Nuestra transacción está envuelta en un try-catch que detecta esto y hace rollback automático en el nodo Fedora, evitando estados inconsistentes. Las alertas quedarían en el estado original."

### P: "¿Cómo manejan la concurrencia si múltiples detectores escriben simultáneamente?"

**R:** "SQL Server maneja esto automáticamente con bloqueos a nivel de fila. Además, cada alerta tiene un ID único auto-incremental que previene conflictos. Los timestamps también ayudan a ordenar eventos cronológicamente."

### P: "¿Por qué usaron SQL Server en Linux en lugar de PostgreSQL o MySQL?"

**R:** "Queríamos demostrar heterogeneidad real. SQL Server en Linux con linked server a SQL Server en Windows simula un escenario empresarial realista donde diferentes sucursales usan el mismo SGBD en diferentes sistemas operativos. Además, SQL Server tiene excelente soporte para transacciones distribuidas."

### P: "¿Los detectores de ataques son reales o simulados?"

**R:** "Son REALES. El network IDS usa Scapy para capturar paquetes reales de la interfaz de red. El SSH monitor lee logs auténticos de /var/log/auth.log. Los honeypots abren puertos reales. Si alguien en la red escaneara nuestra máquina ahora mismo, lo detectaríamos."

### P: "¿Esto se podría usar en producción?"

**R:** "Con algunas mejoras sí. Necesitaríamos:
- Cifrado en las comunicaciones entre nodos
- Autenticación más robusta
- Manejo de alta disponibilidad
- Particionamiento de datos históricos
- Monitoreo de rendimiento
Pero la arquitectura base es sólida y escalable."

## Backup Plan (Si algo falla)

### Si los detectores no arrancan:
> "Tenemos capturas de pantalla de detecciones previas..." (tener screenshots preparados)

### Si el dashboard no carga:
> "Podemos ver las alertas directamente en la base de datos..." (ir a sqlcmd)

### Si no hay red:
> "El generador puede ejecutarse en localhost..." (attack_generator.py ya usa 127.0.0.1)

### Si SQL Server falla:
> "Tenemos un backup de la base de datos que podemos restaurar rápidamente..." (tener backup .bak preparado)

## Checklist Pre-Demostración

- [ ] SQL Server corriendo en ambos nodos
- [ ] Linked server configurado y probado
- [ ] Tablas creadas con datos de prueba
- [ ] Detectores funcionando (probados 5 min antes)
- [ ] Dashboard accesible
- [ ] Attack generator probado al menos una vez
- [ ] Credenciales anotadas (por si acaso)
- [ ] Screenshots de respaldo guardados
- [ ] Diagrama de arquitectura visible
- [ ] Terminal con tamaño de fuente grande (para que se vea)
- [ ] Navegador sin tabs personales (solo SIEM)
- [ ] Batería del laptop cargada / conectado a corriente

## Timing Detallado

| Minuto | Actividad |
|--------|-----------|
| 0-2 | Introducción y contexto |
| 2-4 | Explicar arquitectura distribuida |
| 4-6 | Mostrar componentes de detección |
| 6-11 | Demo en vivo (generar ataques) |
| 11-13 | Archivado distribuido |
| 13-14 | Consulta distribuida (opcional) |
| 14-15 | Conclusión |
| 15+ | Preguntas |

## Tips Finales

✅ **Práctica antes**: Ensaya al menos 2 veces completo
✅ **Habla claro**: No te apures, explica con calma
✅ **Señala**: Usa el cursor para señalar cosas en pantalla
✅ **Entusiasmo**: Demuestra que te apasiona el proyecto
✅ **Honestidad**: Si no sabes algo, di "no estoy seguro pero investigaré"
✅ **Contacto visual**: No leas la pantalla todo el tiempo

❌ **Evita**:
- Decir "espero que funcione"
- Disculparte por adelantado
- Improvisar completamente
- Leer diapositivas textualmente
- Ir muy rápido

---

**¡Mucha suerte! 🚀**
