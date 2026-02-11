-- =====================================================================
-- SCRIPT SQL ACTUALIZADO PARA SIEM CON ATAQUES REALES
-- =====================================================================
-- Este script configura las tablas para registrar ataques reales
-- detectados por los sistemas IDS/IPS y Honeypots
-- =====================================================================

-- =====================================================================
-- EN NODO WINDOWS (Sensor - Base de Datos Remota)
-- =====================================================================

USE SensorDB;
GO

-- Eliminar tabla existente si existe
IF OBJECT_ID('dbo.Live_Alerts', 'U') IS NOT NULL
    DROP TABLE dbo.Live_Alerts;
GO

-- Crear tabla mejorada para ataques reales
CREATE TABLE Live_Alerts (
    AlertID INT IDENTITY(1,1) PRIMARY KEY,
    
    -- Información del ataque
    TipoAtaque NVARCHAR(100) NOT NULL,
    IP_Origen VARCHAR(45) NOT NULL,
    IP_Destino VARCHAR(45) DEFAULT '0.0.0.0',
    Puerto_Origen INT DEFAULT 0,
    Puerto_Destino INT DEFAULT 0,
    
    -- Clasificación
    Severidad NVARCHAR(20) NOT NULL CHECK (Severidad IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    Protocolo NVARCHAR(20) DEFAULT 'TCP',
    
    -- Detalles técnicos
    Payload NVARCHAR(MAX),
    Firma_Ataque NVARCHAR(500),
    Paquetes_Detectados INT DEFAULT 1,
    Bytes_Transferidos BIGINT DEFAULT 0,
    
    -- Metadatos
    Timestamp DATETIME DEFAULT GETDATE(),
    Estado_Alerta NVARCHAR(20) DEFAULT 'ACTIVA' CHECK (Estado_Alerta IN ('ACTIVA', 'INVESTIGANDO', 'FALSO_POSITIVO', 'CONFIRMADA')),
    Fuente_Deteccion NVARCHAR(50) DEFAULT 'IDS', -- IDS, HONEYPOT, LOG_ANALYSIS
    
    -- Geolocalización (opcional para expansión futura)
    Pais_Origen NVARCHAR(50),
    Ciudad_Origen NVARCHAR(100),
    
    -- Índices para búsqueda rápida
    INDEX IX_Timestamp NONCLUSTERED (Timestamp DESC),
    INDEX IX_Severidad NONCLUSTERED (Severidad),
    INDEX IX_TipoAtaque NONCLUSTERED (TipoAtaque),
    INDEX IX_IPOrigen NONCLUSTERED (IP_Origen),
    INDEX IX_Estado NONCLUSTERED (Estado_Alerta)
);
GO

PRINT '✓ Tabla Live_Alerts (ataques reales) creada en Windows';
GO

-- =====================================================================
-- EN NODO FEDORA (Central - Base de Datos Local)
-- =====================================================================

USE CentralSIEM;
GO

-- Eliminar tabla existente si existe
IF OBJECT_ID('dbo.Forense_Logs', 'U') IS NOT NULL
    DROP TABLE dbo.Forense_Logs;
GO

-- Crear tabla mejorada para análisis forense
CREATE TABLE Forense_Logs (
    LogID INT IDENTITY(1,1) PRIMARY KEY,
    
    -- Referencia al ataque original
    Original_AlertID INT NOT NULL,
    
    -- Información del ataque
    TipoAtaque NVARCHAR(100) NOT NULL,
    IP_Origen VARCHAR(45) NOT NULL,
    IP_Destino VARCHAR(45),
    Puerto_Destino INT,
    
    -- Clasificación
    Severidad_Original NVARCHAR(20),
    Protocolo NVARCHAR(20),
    
    -- Análisis forense
    Payload NVARCHAR(MAX),
    Firma_Ataque NVARCHAR(500),
    Analisis_Realizado BIT DEFAULT 0,
    Notas_Analista NVARCHAR(MAX),
    
    -- Metadatos
    Fecha_Ataque_Original DATETIME,
    Fecha_Archivado DATETIME DEFAULT GETDATE(),
    Hash_Integridad VARCHAR(64),
    Estado_Procesamiento NVARCHAR(20) DEFAULT 'PENDIENTE' CHECK (Estado_Procesamiento IN ('PENDIENTE', 'EN_ANALISIS', 'ANALIZADO', 'REPORTADO')),
    
    -- Clasificación de amenaza
    Nivel_Amenaza INT DEFAULT 5, -- 1-10
    Es_Falso_Positivo BIT DEFAULT 0,
    Accion_Tomada NVARCHAR(200),
    
    -- Índices
    INDEX IX_FechaArchivado NONCLUSTERED (Fecha_Archivado DESC),
    INDEX IX_TipoAtaque NONCLUSTERED (TipoAtaque),
    INDEX IX_IPOrigen NONCLUSTERED (IP_Origen),
    INDEX IX_EstadoProcesamiento NONCLUSTERED (Estado_Procesamiento)
);
GO

PRINT '✓ Tabla Forense_Logs (análisis) creada en Fedora';
GO

-- =====================================================================
-- TABLA DE ESTADÍSTICAS DE ATAQUES
-- =====================================================================

IF OBJECT_ID('dbo.Estadisticas_Ataques', 'U') IS NOT NULL
    DROP TABLE dbo.Estadisticas_Ataques;
GO

CREATE TABLE Estadisticas_Ataques (
    EstadisticaID INT IDENTITY(1,1) PRIMARY KEY,
    Fecha DATE NOT NULL,
    Hora INT NOT NULL, -- 0-23
    
    -- Contadores
    Total_Ataques INT DEFAULT 0,
    Ataques_Criticos INT DEFAULT 0,
    Ataques_Altos INT DEFAULT 0,
    Ataques_Medios INT DEFAULT 0,
    Ataques_Bajos INT DEFAULT 0,
    
    -- Por tipo
    Port_Scans INT DEFAULT 0,
    Brute_Force INT DEFAULT 0,
    SQL_Injection INT DEFAULT 0,
    XSS_Attacks INT DEFAULT 0,
    DDoS_Attempts INT DEFAULT 0,
    
    -- IPs únicas atacantes
    IPs_Unicas_Atacantes INT DEFAULT 0,
    
    Timestamp DATETIME DEFAULT GETDATE(),
    
    INDEX IX_Fecha NONCLUSTERED (Fecha DESC, Hora DESC)
);
GO

PRINT '✓ Tabla Estadisticas_Ataques creada';
GO

-- =====================================================================
-- VISTA CONSOLIDADA DE ATAQUES REALES
-- =====================================================================

IF OBJECT_ID('v_AlertasConsolidadas_Real', 'V') IS NOT NULL
    DROP VIEW v_AlertasConsolidadas_Real;
GO

CREATE VIEW v_AlertasConsolidadas_Real AS
-- Ataques activos en nodo remoto
SELECT 
    'REMOTO' AS Nodo,
    'ACTIVA' AS Estado_General,
    AlertID AS ID,
    TipoAtaque,
    IP_Origen,
    IP_Destino,
    Puerto_Destino,
    Severidad AS Nivel,
    Protocolo,
    Fuente_Deteccion,
    Timestamp AS Fecha,
    Paquetes_Detectados,
    Estado_Alerta
FROM [SENSOR_REMOTO].[SensorDB].[dbo].[Live_Alerts]

UNION ALL

-- Ataques archivados en nodo local
SELECT 
    'LOCAL' AS Nodo,
    'ARCHIVADA' AS Estado_General,
    LogID AS ID,
    TipoAtaque,
    IP_Origen,
    IP_Destino,
    Puerto_Destino,
    Severidad_Original AS Nivel,
    Protocolo,
    'FORENSE' AS Fuente_Deteccion,
    Fecha_Archivado AS Fecha,
    NULL AS Paquetes_Detectados,
    Estado_Procesamiento AS Estado_Alerta
FROM Forense_Logs;
GO

PRINT '✓ Vista v_AlertasConsolidadas_Real creada';
GO

-- =====================================================================
-- PROCEDIMIENTO ALMACENADO: Archivado Mejorado
-- =====================================================================

IF OBJECT_ID('sp_ArchivarAtaquesReales', 'P') IS NOT NULL
    DROP PROCEDURE sp_ArchivarAtaquesReales;
GO

CREATE PROCEDURE sp_ArchivarAtaquesReales
    @UsuarioOperacion NVARCHAR(100) = 'SYSTEM',
    @SoloConfirmados BIT = 0
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @RegistrosArchivados INT = 0;
    DECLARE @ErrorMessage NVARCHAR(500);
    
    BEGIN TRY
        -- Iniciar transacción distribuida
        BEGIN TRANSACTION;
        
        -- Copiar datos del nodo remoto al local (con más campos)
        IF @SoloConfirmados = 1
        BEGIN
            -- Solo archivar ataques confirmados (no falsos positivos)
            INSERT INTO Forense_Logs 
            (Original_AlertID, TipoAtaque, IP_Origen, IP_Destino, Puerto_Destino, 
             Severidad_Original, Protocolo, Payload, Firma_Ataque, Fecha_Ataque_Original)
            SELECT 
                AlertID,
                TipoAtaque,
                IP_Origen,
                IP_Destino,
                Puerto_Destino,
                Severidad,
                Protocolo,
                Payload,
                Firma_Ataque,
                Timestamp
            FROM [SENSOR_REMOTO].[SensorDB].[dbo].[Live_Alerts]
            WHERE Estado_Alerta IN ('CONFIRMADA', 'INVESTIGANDO');
        END
        ELSE
        BEGIN
            -- Archivar todos los ataques
            INSERT INTO Forense_Logs 
            (Original_AlertID, TipoAtaque, IP_Origen, IP_Destino, Puerto_Destino, 
             Severidad_Original, Protocolo, Payload, Firma_Ataque, Fecha_Ataque_Original)
            SELECT 
                AlertID,
                TipoAtaque,
                IP_Origen,
                IP_Destino,
                Puerto_Destino,
                Severidad,
                Protocolo,
                Payload,
                Firma_Ataque,
                Timestamp
            FROM [SENSOR_REMOTO].[SensorDB].[dbo].[Live_Alerts];
        END
        
        SET @RegistrosArchivados = @@ROWCOUNT;
        
        -- Eliminar datos del nodo remoto (solo los archivados)
        IF @SoloConfirmados = 1
        BEGIN
            DELETE FROM [SENSOR_REMOTO].[SensorDB].[dbo].[Live_Alerts]
            WHERE Estado_Alerta IN ('CONFIRMADA', 'INVESTIGANDO');
        END
        ELSE
        BEGIN
            DELETE FROM [SENSOR_REMOTO].[SensorDB].[dbo].[Live_Alerts];
        END
        
        -- Registrar auditoría
        INSERT INTO Audit_Transacciones 
            (TipoOperacion, Usuario, NodoOrigen, NodoDestino, RegistrosAfectados, Estado, Mensaje)
        VALUES 
            ('ARCHIVADO_ATAQUES_REALES', @UsuarioOperacion, 'SENSOR_REMOTO', 'CentralSIEM', 
             @RegistrosArchivados, 'EXITOSO', 
             CONCAT('Archivado de ', @RegistrosArchivados, ' ataques reales'));
        
        -- Confirmar transacción
        COMMIT TRANSACTION;
        
        SELECT 
            @RegistrosArchivados AS Archivados,
            'EXITOSO' AS Estado,
            CONCAT('Se archivaron ', @RegistrosArchivados, ' ataques reales') AS Mensaje;
        
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
            ('ARCHIVADO_ATAQUES_REALES', @UsuarioOperacion, 'ERROR', @ErrorMessage);
        
        -- Re-lanzar error
        THROW;
    END CATCH
END
GO

PRINT '✓ Procedimiento sp_ArchivarAtaquesReales creado';
GO

-- =====================================================================
-- PROCEDIMIENTO: Análisis de Patrones de Ataque
-- =====================================================================

IF OBJECT_ID('sp_AnalizarPatronesAtaque', 'P') IS NOT NULL
    DROP PROCEDURE sp_AnalizarPatronesAtaque;
GO

CREATE PROCEDURE sp_AnalizarPatronesAtaque
    @Dias INT = 7
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @FechaInicio DATETIME = DATEADD(DAY, -@Dias, GETDATE());
    
    -- Top 10 IPs atacantes
    SELECT TOP 10
        IP_Origen,
        COUNT(*) AS Total_Ataques,
        SUM(CASE WHEN Severidad_Original = 'CRITICAL' THEN 1 ELSE 0 END) AS Ataques_Criticos,
        MIN(Fecha_Ataque_Original) AS Primer_Ataque,
        MAX(Fecha_Ataque_Original) AS Ultimo_Ataque
    FROM Forense_Logs
    WHERE Fecha_Archivado >= @FechaInicio
    GROUP BY IP_Origen
    ORDER BY Total_Ataques DESC;
    
    -- Tipos de ataque más comunes
    SELECT 
        TipoAtaque,
        COUNT(*) AS Frecuencia,
        AVG(CASE Severidad_Original 
            WHEN 'CRITICAL' THEN 4
            WHEN 'HIGH' THEN 3
            WHEN 'MEDIUM' THEN 2
            ELSE 1 END) AS Severidad_Promedio
    FROM Forense_Logs
    WHERE Fecha_Archivado >= @FechaInicio
    GROUP BY TipoAtaque
    ORDER BY Frecuencia DESC;
    
    -- Distribución por hora del día
    SELECT 
        DATEPART(HOUR, Fecha_Ataque_Original) AS Hora,
        COUNT(*) AS Ataques
    FROM Forense_Logs
    WHERE Fecha_Archivado >= @FechaInicio
    GROUP BY DATEPART(HOUR, Fecha_Ataque_Original)
    ORDER BY Hora;
    
END
GO

PRINT '✓ Procedimiento sp_AnalizarPatronesAtaque creado';
GO

-- =====================================================================
-- TRIGGER: Actualizar estadísticas automáticamente
-- =====================================================================

IF OBJECT_ID('tr_ActualizarEstadisticas', 'TR') IS NOT NULL
    DROP TRIGGER tr_ActualizarEstadisticas;
GO

CREATE TRIGGER tr_ActualizarEstadisticas
ON Forense_Logs
AFTER INSERT
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @Fecha DATE = CAST(GETDATE() AS DATE);
    DECLARE @Hora INT = DATEPART(HOUR, GETDATE());
    
    -- Actualizar o insertar estadísticas
    MERGE Estadisticas_Ataques AS target
    USING (SELECT @Fecha AS Fecha, @Hora AS Hora) AS source
    ON target.Fecha = source.Fecha AND target.Hora = source.Hora
    WHEN MATCHED THEN
        UPDATE SET
            Total_Ataques = Total_Ataques + 1,
            Timestamp = GETDATE()
    WHEN NOT MATCHED THEN
        INSERT (Fecha, Hora, Total_Ataques)
        VALUES (@Fecha, @Hora, 1);
END
GO

PRINT '✓ Trigger tr_ActualizarEstadisticas creado';
GO

-- =====================================================================
-- DATOS DE VERIFICACIÓN
-- =====================================================================

-- Verificar estructura de tablas
PRINT '';
PRINT 'Tablas creadas:';
SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'dbo';

-- Verificar índices
PRINT '';
PRINT 'Índices en Live_Alerts:';
SELECT name FROM sys.indexes WHERE object_id = OBJECT_ID('[SENSOR_REMOTO].[SensorDB].[dbo].[Live_Alerts]');

PRINT '';
PRINT '========================================';
PRINT '✓ CONFIGURACIÓN COMPLETADA';
PRINT '========================================';
PRINT '';
PRINT 'El sistema está listo para recibir ataques reales detectados por:';
PRINT '  • network_ids.py (Detector de red)';
PRINT '  • ssh_bruteforce.py (Detector SSH)';
PRINT '  • honeypot.py (Honeypots)';
PRINT '';
PRINT 'Siguiente paso:';
PRINT '1. Ejecutar detectores: sudo python3 detectors/network_ids.py eth0';
PRINT '2. O ejecutar honeypot: sudo python3 detectors/honeypot.py';
PRINT '3. Ver ataques en dashboard: http://localhost/PROYECTOPARCIAL3/';
PRINT '';
GO
