<?php
// api/get_alerts.php
header("Content-Type: application/json; charset=UTF-8");
include_once '../config/database.php';

$database = new Database();
$db = $database->getConnection();

$response = ["live" => [], "history" => []];

try {
    // 1. Consultar Alertas Vivas (Remoto - Windows)
    // Nota el uso de [SENSOR_REMOTO] que configuramos antes
    $queryLive = "SELECT TOP 10 AlertID, TipoAtaque, IP_Origen, Severidad, Timestamp 
                  FROM [SENSOR_REMOTO].[SensorDB].[dbo].[Live_Alerts] 
                  ORDER BY Timestamp DESC";
    $stmt = $db->prepare($queryLive);
    $stmt->execute();
    $response["live"] = $stmt->fetchAll(PDO::FETCH_ASSOC);

    // 2. Consultar Histórico (Local - Fedora)
    $queryHist = "SELECT TOP 10 LogID, TipoAtaque, IP_Origen, Fecha_Archivado 
                  FROM Forense_Logs 
                  ORDER BY Fecha_Archivado DESC";
    $stmt = $db->prepare($queryHist);
    $stmt->execute();
    $response["history"] = $stmt->fetchAll(PDO::FETCH_ASSOC);

    echo json_encode($response);

} catch (Exception $e) {
    http_response_code(500);
    echo json_encode(["error" => $e->getMessage()]);
}
?>