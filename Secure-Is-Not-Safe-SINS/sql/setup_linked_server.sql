-- =====================================================
-- CONFIGURAR LINKED SERVER (EJECUTAR EN FEDORA)
-- Conecta nodo Fedora con nodo Windows
-- =====================================================

USE master;
GO

-- Eliminar linked server si existe
IF EXISTS (SELECT * FROM sys.servers WHERE name = 'SENSOR_REMOTO')
BEGIN
    EXEC sp_dropserver 'SENSOR_REMOTO', 'droplogins';
    PRINT '✓ Linked Server anterior eliminado';
END
GO

-- Crear linked server
EXEC sp_addlinkedserver 
    @server = 'SENSOR_REMOTO',
    @srvproduct = '',
    @provider = 'SQLNCLI',
    @datasrc = '10.0.90.66,1433';  
GO

-- Configurar credenciales
EXEC sp_addlinkedsrvlogin 
    @rmtsrvname = 'SENSOR_REMOTO',
    @useself = 'false',
    @rmtuser = 'chadi',      
    @rmtpassword = 'pass';  
GO

-- Verificar linked server
EXEC sp_linkedservers;
GO

-- Probar conexión
PRINT 'Probando conexión al nodo remoto...';
SELECT * FROM [SENSOR_REMOTO].master.sys.databases;
GO

-- Probar consulta a SensorDB
SELECT COUNT(*) as TotalAlertas 
FROM [SENSOR_REMOTO].[SensorDB].[dbo].[Live_Alerts];
GO

PRINT '✓ Linked Server configurado correctamente';
GO
