-- =====================================================
-- CONFIGURACIÓN NODO SENSOR (WINDOWS)
-- SQL Server 2022 - Puerto 1433
-- =====================================================

USE master;
GO

-- Crear base de datos sensor
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'SensorDB')
BEGIN
    CREATE DATABASE SensorDB;
END
GO

USE SensorDB;
GO

-- Tabla de alertas en tiempo real (temporal)
CREATE TABLE Live_Alerts (
    AlertID INT IDENTITY(1,1) PRIMARY KEY,
    TipoAtaque NVARCHAR(100) NOT NULL,
    IP_Origen VARCHAR(45) NOT NULL,
    IP_Destino VARCHAR(45) DEFAULT '0.0.0.0',
    Puerto_Origen INT DEFAULT 0,
    Puerto_Destino INT DEFAULT 0,
    Severidad NVARCHAR(20) NOT NULL CHECK (Severidad IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    Protocolo NVARCHAR(20) DEFAULT 'TCP',
    Payload NVARCHAR(MAX),
    Firma_Ataque NVARCHAR(500),
    Paquetes_Detectados INT DEFAULT 1,
    Bytes_Transferidos BIGINT DEFAULT 0,
    Timestamp DATETIME DEFAULT GETDATE(),
    Estado_Alerta NVARCHAR(20) DEFAULT 'ACTIVA',
    Fuente_Deteccion NVARCHAR(50) DEFAULT 'IDS',
    Pais_Origen NVARCHAR(50),
    Ciudad_Origen NVARCHAR(100),
    INDEX IX_Timestamp NONCLUSTERED (Timestamp DESC),
    INDEX IX_Severidad NONCLUSTERED (Severidad),
    INDEX IX_TipoAtaque NONCLUSTERED (TipoAtaque),
    INDEX IX_IPOrigen NONCLUSTERED (IP_Origen)
);
GO

PRINT '✓ Base de datos SensorDB creada en Windows';
GO
