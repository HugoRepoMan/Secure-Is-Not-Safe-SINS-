<?php
// api/actions.php
header("Content-Type: application/json; charset=UTF-8");
include_once '../config/database.php';

$data = json_decode(file_get_contents("php://input"));
$action = $data->action ?? '';

$database = new Database();
$db = $database->getConnection();

try {
    if ($action == 'simulate') {
        // Simular ataque insertando en REMOTO
        $types = ['SQL Injection', 'XSS Attack', 'Ransomware Beacon', 'SSH Brute Force'];
        $severities = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'];
        
        $sql = "INSERT INTO [SENSOR_REMOTO].[SensorDB].[dbo].[Live_Alerts] (TipoAtaque, IP_Origen, Severidad) VALUES (?, ?, ?)";
        $stmt = $db->prepare($sql);
        $stmt->execute([
            $types[array_rand($types)], 
            long2ip(rand(0, "4294967295")), 
            $severities[array_rand($severities)]
        ]);
        echo json_encode(["message" => "Ataque simulado enviado al sensor Windows."]);

    } elseif ($action == 'archive') {
        // TRANSACCIÓN DISTRIBUIDA (Copiar Local <- Remoto, luego Borrar Remoto)
        $db->beginTransaction();

        // 1. Copiar
        $sqlCopy = "INSERT INTO Forense_Logs (Original_AlertID, TipoAtaque, IP_Origen)
                    SELECT AlertID, TipoAtaque, IP_Origen 
                    FROM [SENSOR_REMOTO].[SensorDB].[dbo].[Live_Alerts]";
        $db->exec($sqlCopy);

        // 2. Borrar
        $sqlDelete = "DELETE FROM [SENSOR_REMOTO].[SensorDB].[dbo].[Live_Alerts]";
        $db->exec($sqlDelete);

        $db->commit();
        echo json_encode(["message" => "Logs archivados y asegurados en Fedora."]);
    }
} catch (Exception $e) {
    if ($db->inTransaction()) $db->rollBack();
    http_response_code(500);
    echo json_encode(["error" => $e->getMessage()]);
}
?>