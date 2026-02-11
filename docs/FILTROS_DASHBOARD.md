# 🔍 Sistema de Filtros del Dashboard SIEM - Documentación

## 📋 Nuevas Funcionalidades

El dashboard ahora incluye un **sistema completo de filtros** para analizar los ataques detectados por tipo específico.

## 🎯 Tipos de Ataque Soportados

El sistema puede filtrar por los siguientes 7 tipos de ataque:

### 1. 🔍 Port Scanning
- **Descripción**: Escaneo de puertos para detectar servicios abiertos
- **Severidad típica**: MEDIUM
- **Generado por**: network_ids.py, attack_generator.py
- **Ejemplo**: Escaneo de puertos 22, 80, 443, 3306, etc.

### 2. 💥 SYN Flood
- **Descripción**: Ataque de denegación de servicio mediante paquetes SYN
- **Severidad típica**: CRITICAL
- **Generado por**: network_ids.py, attack_generator.py
- **Ejemplo**: 100+ paquetes SYN por segundo

### 3. 📡 ICMP Flood
- **Descripción**: Flooding de paquetes ICMP (ping)
- **Severidad típica**: MEDIUM
- **Generado por**: network_ids.py, attack_generator.py
- **Ejemplo**: 50+ pings por segundo

### 4. 💉 SQL Injection
- **Descripción**: Intentos de inyección SQL en tráfico HTTP
- **Severidad típica**: CRITICAL
- **Generado por**: network_ids.py, attack_generator.py
- **Ejemplo**: Payloads como `' OR '1'='1`, `UNION SELECT`, etc.

### 5. 🔗 XSS (Cross-Site Scripting)
- **Descripción**: Intentos de inyección de scripts maliciosos
- **Severidad típica**: HIGH
- **Generado por**: network_ids.py, attack_generator.py
- **Ejemplo**: `<script>alert('XSS')</script>`, etc.

### 6. 🔐 SSH Brute Force
- **Descripción**: Múltiples intentos de login SSH fallidos
- **Severidad típica**: CRITICAL
- **Generado por**: ssh_bruteforce.py, attack_generator.py
- **Ejemplo**: 10+ intentos fallidos en 5 minutos

### 7. 🍯 Honeypot
- **Descripción**: Conexiones a servicios señuelo
- **Severidad típica**: MEDIUM-HIGH
- **Generado por**: honeypot.py, attack_generator.py
- **Ejemplo**: Conexión a puerto 2222 (SSH falso)

## 🎨 Características del Dashboard Mejorado

### Sección de Filtros
```
┌─────────────────────────────────────────────┐
│ 🔍 Filtrar Alertas por Tipo de Ataque      │
├─────────────────────────────────────────────┤
│ [📊 Todos (45)] [🔍 Port Scanning (12)]    │
│ [💥 SYN Flood (5)] [📡 ICMP Flood (3)]     │
│ [💉 SQL Injection (15)] [🔗 XSS (8)]       │
│ [🔐 SSH Brute Force (10)] [🍯 Honeypot (2)]│
│                                             │
│ 🔎 [Buscar por IP origen...]  [✖ Limpiar]  │
└─────────────────────────────────────────────┘
```

### Estadísticas por Severidad
```
┌───────────┬───────────┬───────────┬───────────┐
│     15    │     8     │     12    │     10    │
│ 🔴 Crítico│ 🟠 Alto   │ 🟡 Medio  │ 🟢 Bajo   │
└───────────┴───────────┴───────────┴───────────┘
```

### Tabla Mejorada
```
┌────┬─────────────────┬──────────────┬──────────┬────────────┐
│ ID │ Tipo de Ataque  │ IP Origen    │ Severidad│ Timestamp  │
├────┼─────────────────┼──────────────┼──────────┼────────────┤
│ 15 │🔍 Port Scanning │ 192.168.1.50 │🔴 CRITICAL│10/02 15:30│
│ 14 │💉 SQL Injection │ 203.0.113.45 │🟠 HIGH    │10/02 15:28│
│ 13 │🍯 Honeypot      │ 10.0.0.100   │🟡 MEDIUM  │10/02 15:25│
└────┴─────────────────┴──────────────┴──────────┴────────────┘
```

## 🔧 Funcionalidades

### 1. Filtrado por Tipo de Ataque

**Cómo usar**:
- Click en cualquier botón de tipo de ataque
- La tabla se actualiza mostrando solo ese tipo
- El contador muestra cuántos hay de cada tipo

**Ejemplo**:
```javascript
// Click en "💉 SQL Injection (15)"
// Resultado: Solo muestra las 15 alertas de SQL Injection
```

### 2. Búsqueda por IP

**Cómo usar**:
- Escribir IP (completa o parcial) en el campo de búsqueda
- Los resultados se filtran en tiempo real
- Las IPs coincidentes se resaltan en amarillo

**Ejemplo**:
```
Búsqueda: "192.168"
Resultado: Muestra todas las alertas de IPs 192.168.x.x
          con "192.168" resaltado
```

### 3. Filtros Combinados

**Puedes combinar**:
- Filtro de tipo + Búsqueda de IP
- Ejemplo: "SSH Brute Force" desde "192.168.1.x"

**Cómo funciona**:
```javascript
Filtro activo: SSH Brute Force (10 alertas)
Búsqueda activa: "192.168.1"
Resultado: Muestra solo SSH Brute Force desde 192.168.1.x (3 alertas)
```

### 4. Limpiar Filtros

**Botón "✖ Limpiar Filtros"**:
- Resetea a "Todos"
- Limpia búsqueda de IP
- Muestra todas las alertas

### 5. Contadores en Tiempo Real

**Se actualizan automáticamente cada 5 segundos**:
- Contador de cada tipo de ataque
- Estadísticas de severidad
- Badge de total de alertas

## 🎨 Códigos de Color

### Por Severidad
- 🔴 **CRITICAL**: Rojo - Ataques críticos (SYN Flood, SQL Injection, SSH Brute Force)
- 🟠 **HIGH**: Naranja - Ataques de alta prioridad (XSS, algunos Honeypots)
- 🟡 **MEDIUM**: Amarillo - Ataques de prioridad media (Port Scanning, ICMP Flood)
- 🟢 **LOW**: Verde - Ataques de baja prioridad

### Bordes de Tarjetas
- **Rojo**: Alertas en Tiempo Real (Sensor Windows)
- **Verde**: Evidencia Forense (Vault Fedora)

## 📊 Normalización de Tipos de Ataque

El sistema normaliza automáticamente variaciones de nombres:

```javascript
// Todas estas se convierten a "Port Scanning":
"Port Scanning" → "Port Scanning"
"port scanning" → "Port Scanning"
"PORT SCAN"     → "Port Scanning"
"port_scan"     → "Port Scanning"

// Todas estas se convierten a "SSH Brute Force":
"SSH Brute Force"   → "SSH Brute Force"
"ssh brute force"   → "SSH Brute Force"
"SSH_BRUTE_FORCE"   → "SSH Brute Force"
"brute force"       → "SSH Brute Force"
```

**Ventaja**: Los detectores pueden usar diferentes formatos y el dashboard los agrupa correctamente.

## 🚀 Uso en Demo

### Escenario 1: Mostrar Filtros
```
1. Abrir dashboard
2. Ejecutar attack_generator.py
3. Esperar a que se detecten ataques
4. Mostrar botones con contadores actualizados
5. Click en "SQL Injection" → muestra solo SQLi
6. Explicar: "Podemos filtrar por tipo específico"
```

### Escenario 2: Búsqueda por IP
```
1. Tener ataques desde diferentes IPs
2. Escribir IP específica en búsqueda
3. Ver cómo se filtran resultados
4. Explicar: "Útil para análisis forense de un atacante específico"
```

### Escenario 3: Estadísticas
```
1. Mostrar cards de severidad
2. Explicar distribución:
   - "15 ataques críticos requieren atención inmediata"
   - "12 medios pueden esperar"
3. Relacionar con respuesta a incidentes
```

## 💻 Implementación Técnica

### Variables Globales
```javascript
let allLiveAlerts = [];       // Todas las alertas
let currentFilter = 'all';     // Filtro activo
let currentSearchTerm = '';    // Término de búsqueda
```

### Función Principal de Filtrado
```javascript
function applyFilters() {
    let filtered = allLiveAlerts;
    
    // Filtrar por tipo
    if (currentFilter !== 'all') {
        filtered = filtered.filter(alert => 
            alert.TipoAtaque === currentFilter
        );
    }
    
    // Filtrar por IP
    if (currentSearchTerm) {
        filtered = filtered.filter(alert => 
            alert.IP_Origen.includes(currentSearchTerm)
        );
    }
    
    renderTable('live-table', filtered, columns);
}
```

### Actualización Automática
```javascript
// Se ejecuta cada 5 segundos
setInterval(loadData, 5000);

function loadData() {
    // 1. Fetch datos de API
    // 2. Normalizar tipos
    // 3. Actualizar contadores
    // 4. Aplicar filtros
    // 5. Renderizar
}
```

## 🎯 Ventajas para el Proyecto

### Académicas
1. **Demuestra procesamiento de datos**: Filtrado, búsqueda, normalización
2. **UI/UX profesional**: Interfaz moderna y funcional
3. **Análisis en tiempo real**: Estadísticas dinámicas
4. **Separación de responsabilidades**: HTML, CSS, JS bien organizados

### Prácticas
1. **Análisis rápido**: Identificar tipos de ataque predominantes
2. **Investigación forense**: Buscar ataques de IP específica
3. **Priorización**: Ver severidades de un vistazo
4. **Monitoreo efectivo**: Actualización automática sin recargar

### De Presentación
1. **Visual atractivo**: Colores, iconos, animaciones
2. **Interactivo**: El profesor puede hacer click y explorar
3. **Profesional**: Parece un SIEM comercial
4. **Diferenciador**: Otros proyectos no tendrán esto

## 📝 Notas Importantes

### Base de Datos
El sistema espera estos campos en la tabla `Live_Alerts`:
- `AlertID` (int)
- `TipoAtaque` (varchar)
- `IP_Origen` (varchar)
- `Severidad` (varchar: CRITICAL, HIGH, MEDIUM, LOW)
- `Timestamp` (datetime)

### API
El archivo `get_alerts.php` debe retornar JSON con:
```json
{
  "live": [
    {
      "AlertID": 15,
      "TipoAtaque": "Port Scanning",
      "IP_Origen": "192.168.1.50",
      "Severidad": "MEDIUM",
      "Timestamp": "2026-02-10 15:30:22"
    }
  ],
  "history": [...]
}
```

### Compatibilidad
- ✅ Chrome/Edge (recomendado)
- ✅ Firefox
- ✅ Safari
- ⚠️ IE11 (no soportado)

## 🐛 Troubleshooting

### Los filtros no funcionan
```javascript
// Verificar en consola del navegador (F12):
console.log(allLiveAlerts);  // Debe mostrar array de alertas
console.log(currentFilter);   // Debe mostrar filtro activo
```

### Contadores en cero
- Verificar que hay datos en la BD
- Verificar que `get_alerts.php` retorna datos
- Ver respuesta en Network tab (F12)

### Tipos no se normalizan
- Verificar que `attackTypeMap` incluye todas las variaciones
- Agregar nuevas variaciones según necesites

## 🎓 Explicación para el Profesor

> "El dashboard incluye un **sistema de filtros avanzado** que permite analizar los ataques por tipo específico. Implementamos:
>
> 1. **7 categorías de ataque** basadas en el framework MITRE ATT&CK
> 2. **Normalización de datos** para agrupar variaciones de nombres
> 3. **Búsqueda dinámica** por dirección IP del atacante
> 4. **Estadísticas en tiempo real** por severidad
> 5. **Actualización automática** cada 5 segundos sin recargar
>
> Esto demuestra **procesamiento distribuido** ya que los detectores (Python) generan datos en diferentes formatos que el dashboard (JavaScript) normaliza y presenta de forma unificada."

---

**Versión**: 2.0  
**Última actualización**: Febrero 2026  
**Compatibilidad**: Todos los navegadores modernos
