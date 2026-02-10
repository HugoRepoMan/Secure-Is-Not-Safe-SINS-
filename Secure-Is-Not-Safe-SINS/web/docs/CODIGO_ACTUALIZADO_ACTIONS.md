# 🔧 CÓDIGO ACTUALIZADO - `actions.php`

Este documento detalla la versión actualizada del endpoint `web/api/actions.php`, incluyendo las mejoras de concurrencia, rollback manual y auditoría.

---

## Instrucciones de instalación

```bash
# 1) Editar el archivo en el servidor
sudo nano /var/www/html/PROYECTOPARCIAL3/api/actions.php

# 2) Reemplazar el contenido completo
# 3) Guardar cambios
```

---

## Código implementado (resumen funcional)

La nueva implementación incluye:

- Acción `simulate` con inserción segura usando prepared statements.
- Acción `archive` con:
  - `BEGIN DISTRIBUTED TRANSACTION` / `COMMIT` / `ROLLBACK` en SQL Server del host,
  - control de concurrencia optimista por `MAX(Timestamp)` (antes/después),
  - rollback manual cuando se detecta conflicto,
  - auditoría en `Audit_Transacciones`.
- Acción `cleanup` para limpieza de retención (30 días) y su auditoría.

> El código fuente completo está en: `web/api/actions.php`.

---


## Requisito clave de ejecución (máquina anfitrión)

- Este endpoint debe ejecutarse en la **máquina anfitrión (Fedora/SQL Server central)**, ya que ahí se inicia `BEGIN DISTRIBUTED TRANSACTION` y se coordina el linked server `SENSOR_REMOTO`.
- Ruta objetivo de despliegue en host: `/var/www/html/PROYECTOPARCIAL3/api/actions.php`.
- No ejecutar esta versión directamente en el nodo Windows remoto.

---

## Pasos de despliegue recomendados

### 1. Copiar archivo actualizado al servidor web

```bash
cd ~/SIEM-Final
sudo cp web/api/actions.php /var/www/html/PROYECTOPARCIAL3/api/
sudo chown apache:apache /var/www/html/PROYECTOPARCIAL3/api/actions.php
```

### 2. Verificar tabla de auditoría

```bash
sqlcmd -S localhost,1432 -U sa -P 'CyberPass2026' -C
```

```sql
USE CentralSIEM;
GO

SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'Audit_Transacciones';
GO

CREATE TABLE Audit_Transacciones (
    AuditID INT IDENTITY(1,1) PRIMARY KEY,
    TipoOperacion NVARCHAR(50) NOT NULL,
    NodoOrigen NVARCHAR(50),
    NodoDestino NVARCHAR(50),
    RegistrosAfectados INT,
    FechaOperacion DATETIME DEFAULT GETDATE(),
    Usuario NVARCHAR(100),
    Estado NVARCHAR(20),
    Detalles NVARCHAR(MAX)
);
GO
```

> Ejecuta el `CREATE TABLE` solo si la tabla no existe.

### 3. Prueba funcional mínima

```bash
# Generar datos de prueba
cd ~/SIEM-Final/detectors
sudo python3 attack_generator.py

# Abrir dashboard
firefox http://localhost/PROYECTOPARCIAL3/

# Verificar auditoría
sqlcmd -S localhost,1432 -U sa -P 'CyberPass2026' -C -Q "SELECT TOP 20 * FROM Audit_Transacciones ORDER BY AuditID DESC"
```

---

## Características implementadas

### ✅ Control de concurrencia optimista

- Captura `MAX(Timestamp)` antes de copiar.
- Revalida `MAX(Timestamp)` al terminar la copia.
- Si cambió el valor, hay escritura concurrente.

### ✅ Detección de conflictos

- Comparación temporal antes/después de la operación distribuida.
- Excepción clara para reintentar la operación.

### ✅ Rollback manual seguro

- Usa `Fecha_Archivado >= ?` con prepared statement y marca temporal de inicio.
- Evita SQL dinámico para rollback.

### ✅ Auditoría de transacciones

- Inserta registro `ARCHIVADO` al completar `archive`.
- Inserta registro `LIMPIEZA` al completar `cleanup`.

---

## Mensaje sugerido para la presentación

> "Se implementó control de concurrencia optimista con verificación de timestamp antes y después de la copia distribuida. Si se detectan escrituras concurrentes, se ejecuta rollback manual de los registros archivados en la ventana de la operación y se notifica el conflicto. Además, cada operación clave queda auditada para trazabilidad." 

---

## Checklist

- [ ] `actions.php` actualizado en servidor
- [ ] tabla `Audit_Transacciones` existente
- [ ] prueba de `simulate` exitosa
- [ ] prueba de `archive` exitosa
- [ ] registros visibles en auditoría
- [ ] cambios versionados en Git
