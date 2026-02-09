-- =====================================================================
-- SCRIPT DE CONFIGURACIÓN: SISTEMA SIEM DISTRIBUIDO
-- Base de Datos Distribuida Heterogénea (SQL Server)
-- =====================================================================
-- Proyecto: Sistema de Monitoreo de Eventos de Seguridad (SIEM)
-- Arquitectura: Nodo Central (Fedora) + Nodo Remoto (Windows)
-- =====================================================================

-- =====================================================================
-- PARTE 1: CONFIGURACIÓN DEL SERVIDOR VINCULADO (LINKED SERVER)
-- =====================================================================
-- Ejecutar en el NODO CENTRAL (Fedora - 127.0.0.1:1432)

-- 1.1 Verificar servidores vinculados existentes
EXEC sp_linkedservers;
GO

-- 1.2 Eliminar servidor vinculado si existe (para reconfiguración)
IF EXISTS (SELECT * FROM sys.servers WHERE name = 'SENSOR_REMOTO')
BEGIN
    EXEC sp_dropserver 'SENSOR_REMOTO', 'droplogins';
    PRINT '✓ Servidor vinculado SENSOR_REMOTO eliminado';
END
GO

-- 1.3 Crear servidor vinculado al nodo remoto (Windows)
-- IMPORTANTE: Reemplazar 'IP_WINDOWS' con la IP real de la máquina Windows
EXEC sp_addlinkedserver 
    @server = 'SENSOR_REMOTO',
    @srvproduct = '',
    @provider = 'SQLNCLI',
    @datasrc = 'IP_WINDOWS,1433'; -- Cambiar IP_WINDOWS por IP real
GO

-- 1.4 Configurar credenciales de acceso al servidor remoto
EXEC sp_addlinkedsrvlogin 
    @rmtsrvname = 'SENSOR_REMOTO',
    @useself = 'false',
    @rmtuser = 'sa',
    @rmtpassword = 'WindowsPass2026'; -- Cambiar por password real de Windows
GO

-- 1.5 Probar conexión al servidor remoto
SELECT * FROM [SENSOR_REMOTO].[SensorDB].[dbo].[Live_Alerts];
GO

PRINT '✓ Configuración de servidor vinculado completada';
GO

-- =====================================================================
-- PARTE 2: CREACIÓN DE BASE DE DATOS LOCAL (FEDORA)
-- =====================================================================

-- 2.1 Crear base de datos central si no existe
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'CentralSIEM')
BEGIN
    CREATE DATABASE CentralSIEM;
    PRINT '✓ Base de datos CentralSIEM creada';
END
ELSE
BEGIN
    PRINT 'ℹ Base de datos CentralSIEM ya existe';
END
GO

-- 2.2 Usar base de datos CentralSIEM
USE CentralSIEM;
GO

-- 2.3 Crear tabla de logs forenses (almacenamiento local)
-- Implementa: Fragmentación horizontal, replicación
IF OBJECT_ID('dbo.Forense_Logs', 'U') IS NOT NULL
    DROP TABLE dbo.Forense_Logs;
GO

CREATE TABLE Forense_Logs (
    LogID INT IDENTITY(1,1) PRIMARY KEY,
    Original_AlertID INT NOT NULL,
    TipoAtaque NVARCHAR(100) NOT NULL,
    IP_Origen VARCHAR(45) NOT NULL,
    Severidad_Original NVARCHAR(20),
    Fecha_Archivado DATETIME DEFAULT GETDATE(),
    Hash_Integridad VARCHAR(64),
    Estado_Procesamiento NVARCHAR(20) DEFAULT 'PENDIENTE',
    
    -- Índices para optimización de consultas distribuidas
    INDEX IX_TipoAtaque NONCLUSTERED (TipoAtaque),
    INDEX IX_FechaArchivado NONCLUSTERED (Fecha_Archivado DESC),
    INDEX IX_IPOrigen NONCLUSTERED (IP_Origen)
);
GO

PRINT '✓ Tabla Forense_Logs creada con índices optimizados';
GO

-- 2.4 Crear tabla de auditoría de transacciones distribuidas
IF OBJECT_ID('dbo.Audit_Transacciones', 'U') IS NOT NULL
    DROP TABLE dbo.Audit_Transacciones;
GO

CREATE TABLE Audit_Transacciones (
    AuditID INT IDENTITY(1,1) PRIMARY KEY,
    TipoOperacion NVARCHAR(50) NOT NULL,
    FechaOperacion DATETIME DEFAULT GETDATE(),
    Usuario NVARCHAR(100),
    NodoOrigen NVARCHAR(50),
    NodoDestino NVARCHAR(50),
    RegistrosAfectados INT,
    Estado NVARCHAR(20),
    Mensaje NVARCHAR(500)
);
GO

PRINT '✓ Tabla de auditoría creada';
GO

-- =====================================================================
-- PARTE 3: CREACIÓN DE BASE DE DATOS REMOTA (WINDOWS)
-- =====================================================================
-- Ejecutar en el NODO REMOTO (Windows - IP_WINDOWS:1433)

-- 3.1 Crear base de datos del sensor si no existe
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'SensorDB')
BEGIN
    CREATE DATABASE SensorDB;
    PRINT '✓ Base de datos SensorDB creada en nodo Windows';
END
GO

USE SensorDB;
GO

-- 3.2 Crear tabla de alertas en tiempo real
IF OBJECT_ID('dbo.Live_Alerts', 'U') IS NOT NULL
    DROP TABLE dbo.Live_Alerts;
GO

CREATE TABLE Live_Alerts (
    AlertID INT IDENTITY(1,1) PRIMARY KEY,
    TipoAtaque NVARCHAR(100) NOT NULL,
    IP_Origen VARCHAR(45) NOT NULL,
    Severidad NVARCHAR(20) NOT NULL CHECK (Severidad IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    Timestamp DATETIME DEFAULT GETDATE(),
    Puerto_Destino INT,
    Protocolo NVARCHAR(20),
    Estado_Alerta NVARCHAR(20) DEFAULT 'ACTIVA',
    
    -- Índices para consultas de tiempo real
    INDEX IX_Timestamp NONCLUSTERED (Timestamp DESC),
    INDEX IX_Severidad NONCLUSTERED (Severidad)
);
GO

PRINT '✓ Tabla Live_Alerts creada en nodo Windows';
GO

-- =====================================================================
-- PARTE 4: DATOS DE PRUEBA
-- =====================================================================

-- 4.1 Insertar datos de prueba en nodo remoto (Windows)
USE SensorDB;
GO

INSERT INTO Live_Alerts (TipoAtaque, IP_Origen, Severidad, Puerto_Destino, Protocolo)
VALUES 
    ('SQL Injection', '192.168.1.105', 'HIGH', 3306, 'TCP'),
    ('XSS Attack', '10.0.0.45', 'MEDIUM', 80, 'HTTP'),
    ('Ransomware Beacon', '172.16.0.88', 'CRITICAL', 443, 'HTTPS'),
    ('SSH Brute Force', '203.0.113.50', 'HIGH', 22, 'SSH'),
    ('Port Scanning', '198.51.100.10', 'LOW', 0, 'ICMP');
GO

PRINT '✓ Datos de prueba insertados en nodo Windows';
GO

-- =====================================================================
-- PARTE 5: PROCEDIMIENTOS ALMACENADOS (STORED PROCEDURES)
-- =====================================================================

-- Volver al nodo central (Fedora)
USE CentralSIEM;
GO

-- 5.1 Procedimiento para archivar logs (implementa transacción distribuida)
IF OBJECT_ID('sp_ArchivarLogs', 'P') IS NOT NULL
    DROP PROCEDURE sp_ArchivarLogs;
GO

CREATE PROCEDURE sp_ArchivarLogs
    @UsuarioOperacion NVARCHAR(100) = 'SYSTEM'
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @RegistrosArchivados INT = 0;
    DECLARE @ErrorMessage NVARCHAR(500);
    
    BEGIN TRY
        -- Iniciar transacción distribuida
        BEGIN TRANSACTION;
        
        -- Copiar datos del nodo remoto al local
        INSERT INTO Forense_Logs (Original_AlertID, TipoAtaque, IP_Origen, Severidad_Original)
        SELECT 
            AlertID,
            TipoAtaque,
            IP_Origen,
            Severidad
        FROM [SENSOR_REMOTO].[SensorDB].[dbo].[Live_Alerts];
        
        SET @RegistrosArchivados = @@ROWCOUNT;
        
        -- Eliminar datos del nodo remoto
        DELETE FROM [SENSOR_REMOTO].[SensorDB].[dbo].[Live_Alerts];
        
        -- Registrar auditoría
        INSERT INTO Audit_Transacciones 
            (TipoOperacion, Usuario, NodoOrigen, NodoDestino, RegistrosAfectados, Estado, Mensaje)
        VALUES 
            ('ARCHIVADO', @UsuarioOperacion, 'SENSOR_REMOTO', 'CentralSIEM', 
             @RegistrosArchivados, 'EXITOSO', 'Archivado distribuido completado');
        
        -- Confirmar transacción
        COMMIT TRANSACTION;
        
        PRINT CONCAT('✓ ', @RegistrosArchivados, ' registros archivados exitosamente');
        
    END TRY
    BEGIN CATCH
        -- Revertir transacción en caso de error
        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION;
        
        SET @ErrorMessage = ERROR_MESSAGE();
        
        -- Registrar error en auditoría
        INSERT INTO Audit_Transacciones 
            (TipoOperacion, Usuario, Estado, Mensaje)
        VALUES 
            ('ARCHIVADO', @UsuarioOperacion, 'ERROR', @ErrorMessage);
        
        PRINT CONCAT('✗ Error en archivado: ', @ErrorMessage);
        
        -- Re-lanzar error
        THROW;
    END CATCH
END
GO

PRINT '✓ Procedimiento almacenado sp_ArchivarLogs creado';
GO

-- 5.2 Procedimiento para limpieza de logs antiguos
IF OBJECT_ID('sp_LimpiarLogsAntiguos', 'P') IS NOT NULL
    DROP PROCEDURE sp_LimpiarLogsAntiguos;
GO

CREATE PROCEDURE sp_LimpiarLogsAntiguos
    @DiasRetencion INT = 30
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @FechaLimite DATETIME = DATEADD(DAY, -@DiasRetencion, GETDATE());
    DECLARE @RegistrosEliminados INT;
    
    DELETE FROM Forense_Logs
    WHERE Fecha_Archivado < @FechaLimite;
    
    SET @RegistrosEliminados = @@ROWCOUNT;
    
    -- Registrar auditoría
    INSERT INTO Audit_Transacciones 
        (TipoOperacion, RegistrosAfectados, Estado, Mensaje)
    VALUES 
        ('LIMPIEZA', @RegistrosEliminados, 'EXITOSO', 
         CONCAT('Eliminados logs con más de ', @DiasRetencion, ' días'));
    
    PRINT CONCAT('✓ ', @RegistrosEliminados, ' registros antiguos eliminados');
END
GO

PRINT '✓ Procedimiento almacenado sp_LimpiarLogsAntiguos creado';
GO

-- =====================================================================
-- PARTE 6: VISTAS PARA CONSULTAS DISTRIBUIDAS
-- =====================================================================

-- 6.1 Vista consolidada de todas las alertas (locales y remotas)
IF OBJECT_ID('v_AlertasConsolidadas', 'V') IS NOT NULL
    DROP VIEW v_AlertasConsolidadas;
GO

CREATE VIEW v_AlertasConsolidadas AS
SELECT 
    'REMOTO' AS Nodo,
    AlertID AS ID,
    TipoAtaque,
    IP_Origen,
    Severidad AS Nivel,
    Timestamp AS Fecha,
    'ACTIVA' AS Estado
FROM [SENSOR_REMOTO].[SensorDB].[dbo].[Live_Alerts]

UNION ALL

SELECT 
    'LOCAL' AS Nodo,
    LogID AS ID,
    TipoAtaque,
    IP_Origen,
    Severidad_Original AS Nivel,
    Fecha_Archivado AS Fecha,
    'ARCHIVADA' AS Estado
FROM Forense_Logs;
GO

PRINT '✓ Vista v_AlertasConsolidadas creada';
GO

-- =====================================================================
-- PARTE 7: CONFIGURACIÓN DE SEGURIDAD Y PERMISOS
-- =====================================================================

-- 7.1 Crear usuario de aplicación (opcional)
IF NOT EXISTS (SELECT * FROM sys.sysusers WHERE name = 'app_siem')
BEGIN
    CREATE USER app_siem WITHOUT LOGIN;
    GRANT SELECT, INSERT, UPDATE ON Forense_Logs TO app_siem;
    GRANT EXECUTE ON sp_ArchivarLogs TO app_siem;
    GRANT EXECUTE ON sp_LimpiarLogsAntiguos TO app_siem;
    PRINT '✓ Usuario app_siem creado con permisos limitados';
END
GO

-- =====================================================================
-- PARTE 8: VERIFICACIÓN Y PRUEBAS
-- =====================================================================

-- 8.1 Verificar tablas creadas
SELECT 
    TABLE_SCHEMA,
    TABLE_NAME,
    TABLE_TYPE
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'dbo';
GO

-- 8.2 Consultar alertas remotas
SELECT TOP 5 * FROM [SENSOR_REMOTO].[SensorDB].[dbo].[Live_Alerts]
ORDER BY Timestamp DESC;
GO

-- 8.3 Consultar logs locales
SELECT TOP 5 * FROM Forense_Logs
ORDER BY Fecha_Archivado DESC;
GO

-- 8.4 Consultar vista consolidada
SELECT TOP 10 * FROM v_AlertasConsolidadas
ORDER BY Fecha DESC;
GO

PRINT '';
PRINT '========================================';
PRINT '✓ CONFIGURACIÓN COMPLETADA EXITOSAMENTE';
PRINT '========================================';
PRINT '';
PRINT 'SIGUIENTE PASO:';
PRINT '1. Verificar conectividad entre nodos';
PRINT '2. Configurar PHP con driver sqlsrv';
PRINT '3. Actualizar IPs en database.php';
PRINT '4. Probar APIs desde el navegador';
PRINT '';
GO
