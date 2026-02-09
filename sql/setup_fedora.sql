-- =====================================================
-- CONFIGURACIÓN NODO CENTRAL (FEDORA LINUX)
-- SQL Server 2022 - Puerto 1432
-- =====================================================

USE master;
GO

-- Crear base de datos central
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'CentralSIEM')
BEGIN
    CREATE DATABASE CentralSIEM;
END
GO

USE CentralSIEM;
GO

-- Tabla de logs forenses (vault permanente)
CREATE TABLE Forense_Logs (
    LogID INT IDENTITY(1,1) PRIMARY KEY,
    Original_AlertID INT NOT NULL,
    TipoAtaque NVARCHAR(100) NOT NULL,
    IP_Origen VARCHAR(45) NOT NULL,
    IP_Destino VARCHAR(45),
    Puerto_Destino INT,
    Severidad_Original NVARCHAR(20),
    Protocolo NVARCHAR(20),
    Payload NVARCHAR(MAX),
    Fecha_Ataque_Original DATETIME,
    Fecha_Archivado DATETIME DEFAULT GETDATE(),
    Estado_Procesamiento NVARCHAR(20) DEFAULT 'PENDIENTE',
    INDEX IX_FechaArchivado NONCLUSTERED (Fecha_Archivado DESC),
    INDEX IX_TipoAtaque NONCLUSTERED (TipoAtaque),
    INDEX IX_IPOrigen NONCLUSTERED (IP_Origen)
);
GO

-- Tabla de auditoría de transacciones
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

PRINT '✓ Base de datos CentralSIEM creada en Fedora';
GO
