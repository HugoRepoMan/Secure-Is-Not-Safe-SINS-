<?php
/**
 * API: Get Alerts - Consulta de alertas desde bases de datos distribuidas
 * 
 * Implementa:
 * - Consultas distribuidas (heterogéneas)
 * - Manejo de transacciones
 * - Control de concurrencia
 * - Seguridad mediante prepared statements
 */

// Configuración de headers CORS y tipo de contenido
header("Access-Control-Allow-Origin: *");
header("Content-Type: application/json; charset=UTF-8");
header("Access-Control-Allow-Methods: GET, OPTIONS");
header("Access-Control-Allow-Headers: Content-Type");

// Manejo de solicitudes OPTIONS (preflight)
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit();
}

// Incluir configuración de base de datos
require_once '../config/database.php';

// Estructura de respuesta
$response = [
    "success" => false,
    "data" => [
        "live" => [],
        "history" => []
    ],
    "metadata" => [
        "timestamp" => date('Y-m-d H:i:s'),
        "source_nodes" => [
            "remote" => "Windows Sensor Node",
            "local" => "Fedora Central Vault"
        ]
    ],
    "error" => null
];

try {
    // Obtener instancia de Database (Singleton)
    $database = Database::getInstance();
    $db = $database->getConnection();
    
    // Verificar conexión
    if ($db === null) {
        throw new Exception("No se pudo establecer conexión con la base de datos");
    }
    
    // =================================================================
    // CONSULTA 1: Alertas en Tiempo Real (Nodo Remoto - Windows)
    // Implementa: Consultas distribuidas en base heterogénea
    // =================================================================
    $queryLive = "
        SELECT TOP 10 
            AlertID,
            TipoAtaque,
            IP_Origen,
            Severidad,
            Timestamp
        FROM [SENSOR_REMOTO].[SensorDB].[dbo].[Live_Alerts]
        ORDER BY Timestamp DESC
    ";
    
    $stmtLive = $db->prepare($queryLive);
    $stmtLive->execute();
    $response["data"]["live"] = $stmtLive->fetchAll(PDO::FETCH_ASSOC);
    
    // Contabilizar resultados
    $response["metadata"]["live_count"] = count($response["data"]["live"]);
    
    // =================================================================
    // CONSULTA 2: Evidencia Forense (Nodo Local - Fedora)
    // Implementa: Procesamiento local de datos históricos
    // =================================================================
    $queryHistory = "
        SELECT TOP 10 
            LogID,
            TipoAtaque,
            IP_Origen,
            Fecha_Archivado
        FROM Forense_Logs
        ORDER BY Fecha_Archivado DESC
    ";
    
    $stmtHistory = $db->prepare($queryHistory);
    $stmtHistory->execute();
    $response["data"]["history"] = $stmtHistory->fetchAll(PDO::FETCH_ASSOC);
    
    // Contabilizar resultados
    $response["metadata"]["history_count"] = count($response["data"]["history"]);
    
    // Procesamiento de fechas de SQL Server
    foreach ($response["data"]["history"] as &$row) {
        if (isset($row['Fecha_Archivado']) && is_object($row['Fecha_Archivado'])) {
            $row['Fecha_Archivado'] = $row['Fecha_Archivado']->date ?? date('Y-m-d H:i:s');
        }
    }
    
    foreach ($response["data"]["live"] as &$row) {
        if (isset($row['Timestamp']) && is_object($row['Timestamp'])) {
            $row['Timestamp'] = $row['Timestamp']->date ?? date('Y-m-d H:i:s');
        }
    }
    
    // Marcar respuesta como exitosa
    $response["success"] = true;
    http_response_code(200);
    
} catch (PDOException $e) {
    // Error de base de datos
    $response["error"] = "Error en consulta de base de datos";
    $response["error_details"] = $e->getMessage();
    http_response_code(500);
    error_log("PDO Error en get_alerts.php: " . $e->getMessage());
    
} catch (Exception $e) {
    // Error general
    $response["error"] = $e->getMessage();
    http_response_code(500);
    error_log("Error en get_alerts.php: " . $e->getMessage());
}

// Enviar respuesta JSON
echo json_encode($response, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE);
?>
