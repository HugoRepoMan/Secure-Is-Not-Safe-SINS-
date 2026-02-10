<?php
/**
 * API: Actions - Operaciones sobre bases de datos distribuidas
 *
 * Implementa:
 * - Transacciones distribuidas con control de concurrencia
 * - Bloqueo optimista (Optimistic Locking)
 * - Detección de conflictos
 * - Rollback manual
 * - Auditoría de transacciones
 */

// Configuración de headers CORS
header("Access-Control-Allow-Origin: *");
header("Content-Type: application/json; charset=UTF-8");
header("Access-Control-Allow-Methods: POST, OPTIONS");
header("Access-Control-Allow-Headers: Content-Type");

// Manejo de solicitudes OPTIONS (preflight)
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit();
}

// Incluir configuración de base de datos
require_once '../config/database.php';

// Obtener y validar datos de entrada
$input = file_get_contents("php://input");
$data = json_decode($input);

// Validar JSON
if (json_last_error() !== JSON_ERROR_NONE) {
    http_response_code(400);
    echo json_encode([
        "success" => false,
        "error" => "JSON inválido: " . json_last_error_msg()
    ]);
    exit();
}

$action = $data->action ?? '';

// Validar acción
if (empty($action)) {
    http_response_code(400);
    echo json_encode([
        "success" => false,
        "error" => "Se requiere el parámetro 'action'"
    ]);
    exit();
}

// Estructura de respuesta
$response = [
    "success" => false,
    "action" => $action,
    "message" => "",
    "data" => null,
    "timestamp" => date('Y-m-d H:i:s'),
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
    // ACCIÓN: SIMULATE - Simular ataque en nodo remoto
    // =================================================================
    if ($action === 'simulate') {
        // Tipos de ataques para simulación
        $attackTypes = [
            'SQL Injection',
            'XSS Attack',
            'Ransomware Beacon',
            'SSH Brute Force',
            'DDoS Attack',
            'Port Scanning',
            'Malware Detection',
            'Phishing Attempt'
        ];

        // Niveles de severidad
        $severityLevels = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'];

        // Generar datos aleatorios del ataque
        $attackType = $attackTypes[array_rand($attackTypes)];
        $sourceIP = long2ip(rand(0, 4294967295));
        $severity = $severityLevels[array_rand($severityLevels)];

        // Query con prepared statement (seguridad contra SQL injection)
        $sql = "
            INSERT INTO [SENSOR_REMOTO].[SensorDB].[dbo].[Live_Alerts]
            (TipoAtaque, IP_Origen, Severidad, Timestamp)
            VALUES (?, ?, ?, GETDATE())
        ";

        $stmt = $db->prepare($sql);
        $result = $stmt->execute([$attackType, $sourceIP, $severity]);

        if ($result) {
            $response["success"] = true;
            $response["message"] = "Ataque simulado exitosamente en nodo Windows";
            $response["data"] = [
                "attack_type" => $attackType,
                "source_ip" => $sourceIP,
                "severity" => $severity,
                "target_node" => "SENSOR_REMOTO (Windows)"
            ];
            http_response_code(201);
        } else {
            throw new Exception("Error al insertar ataque simulado");
        }
    }

    // =================================================================
    // ACCIÓN: ARCHIVE - Transacción distribuida con control de concurrencia
    // Implementa:
    // - Bloqueo optimista (Optimistic Locking)
    // - Control de concurrencia mediante timestamp checking
    // - Detección de conflictos
    // - Rollback manual en caso de escrituras concurrentes
    // - Auditoría de transacciones
    // - Replicación de datos
    // =================================================================
    elseif ($action === 'archive') {
        // Verificar si hay datos para archivar
        $checkSql = "SELECT COUNT(*) as total FROM [SENSOR_REMOTO].[SensorDB].[dbo].[Live_Alerts]";
        $checkStmt = $db->query($checkSql);
        $count = (int) $checkStmt->fetch(PDO::FETCH_ASSOC)['total'];

        if ($count === 0) {
            $response["success"] = true;
            $response["message"] = "No hay alertas para archivar";
            $response["data"] = ["archived_count" => 0];
            http_response_code(200);
        } else {
            // =========================================================
            // TRANSACCIÓN DISTRIBUIDA CON CONTROL DE CONCURRENCIA
            // Se ejecuta en SQL Server del HOST (Fedora) y coordina
            // operaciones locales + linked server remoto (Windows)
            // =========================================================
            $distributedTxStarted = false;

            try {
                // Iniciar transacción distribuida explícita en SQL Server
                $db->exec("BEGIN DISTRIBUTED TRANSACTION");
                $distributedTxStarted = true;

                // FASE 1: BLOQUEO OPTIMISTA - Capturar timestamp inicial
                $timestampCheck = $db->query(
                    "SELECT MAX(Timestamp) as LastMod FROM [SENSOR_REMOTO].[SensorDB].[dbo].[Live_Alerts]"
                )->fetch(PDO::FETCH_ASSOC)['LastMod'];

                // Marcador temporal de archivado para rollback manual seguro
                $archiveStartSql = "SELECT GETDATE() AS ArchiveStartedAt";
                $archiveStartedAt = $db->query($archiveStartSql)->fetch(PDO::FETCH_ASSOC)['ArchiveStartedAt'];

                // FASE 2: COPIAR DATOS (Windows → Fedora)
                $sqlCopy = "
                    INSERT INTO Forense_Logs
                    (Original_AlertID, TipoAtaque, IP_Origen, IP_Destino,
                     Puerto_Destino, Severidad_Original, Protocolo,
                     Fecha_Ataque_Original, Fecha_Archivado)
                    SELECT
                        AlertID,
                        TipoAtaque,
                        IP_Origen,
                        IP_Destino,
                        Puerto_Destino,
                        Severidad,
                        Protocolo,
                        Timestamp,
                        GETDATE()
                    FROM [SENSOR_REMOTO].[SensorDB].[dbo].[Live_Alerts]
                ";

                $copyResult = $db->exec($sqlCopy);

                // FASE 3: VERIFICAR CONCURRENCIA
                $timestampVerify = $db->query(
                    "SELECT MAX(Timestamp) as LastMod FROM [SENSOR_REMOTO].[SensorDB].[dbo].[Live_Alerts]"
                )->fetch(PDO::FETCH_ASSOC)['LastMod'];

                // CONTROL DE CONCURRENCIA: Detectar conflictos
                if ($timestampCheck !== $timestampVerify) {
                    // ROLLBACK MANUAL: Hubo escritura concurrente
                    $rollbackSql = "
                        DELETE FROM Forense_Logs
                        WHERE Fecha_Archivado >= ?
                    ";
                    $rollbackStmt = $db->prepare($rollbackSql);
                    $rollbackStmt->execute([$archiveStartedAt]);

                    throw new Exception(
                        "Conflicto de concurrencia detectado. " .
                        "Se detectaron nuevas alertas durante el archivado. " .
                        "Por favor reintente la operación."
                    );
                }

                // FASE 4: ELIMINAR DEL ORIGEN
                if ($copyResult > 0) {
                    $sqlDelete = "
                        DELETE FROM [SENSOR_REMOTO].[SensorDB].[dbo].[Live_Alerts]
                    ";
                    $deleteResult = $db->exec($sqlDelete);

                    // FASE 5: AUDITAR TRANSACCIÓN
                    $auditSql = "
                        INSERT INTO Audit_Transacciones
                        (TipoOperacion, NodoOrigen, NodoDestino,
                         RegistrosAfectados, Usuario, Estado, Detalles)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ";

                    $auditStmt = $db->prepare($auditSql);
                    $auditStmt->execute([
                        'ARCHIVADO',
                        'SENSOR_REMOTO (Windows)',
                        'FEDORA_CENTRAL',
                        $count,
                        'system',
                        'COMPLETADO',
                        'BEGIN DISTRIBUTED TRANSACTION + control de concurrencia optimista'
                    ]);

                    // Confirmar transacción distribuida
                    $db->exec("COMMIT TRANSACTION");
                    $distributedTxStarted = false;

                    $response["success"] = true;
                    $response["message"] = "Logs archivados exitosamente en Fedora Vault";
                    $response["data"] = [
                        "archived_count" => $count,
                        "copied" => $copyResult,
                        "deleted" => $deleteResult,
                        "source_node" => "SENSOR_REMOTO (Windows)",
                        "destination_node" => "Forense_Logs (Fedora)",
                        "concurrency_check" => "PASSED",
                        "transaction_type" => "BEGIN DISTRIBUTED TRANSACTION + Optimistic Locking"
                    ];
                    http_response_code(200);
                } else {
                    throw new Exception("No se pudieron copiar los registros");
                }
            } catch (Exception $e) {
                if ($distributedTxStarted) {
                    try {
                        $db->exec("ROLLBACK TRANSACTION");
                    } catch (Exception $rollbackException) {
                        error_log("Rollback distribuido falló: " . $rollbackException->getMessage());
                    }
                }

                throw new Exception("Error en transacción distribuida: " . $e->getMessage());
            }
        }
    }

    // =================================================================
    // ACCIÓN: CLEANUP - Limpiar logs antiguos (mantenimiento)
    // =================================================================
    elseif ($action === 'cleanup') {
        // Eliminar logs con más de 30 días
        $sqlCleanup = "
            DELETE FROM Forense_Logs
            WHERE Fecha_Archivado < DATEADD(day, -30, GETDATE())
        ";

        $deletedRows = $db->exec($sqlCleanup);

        // Auditar limpieza
        $auditSql = "
            INSERT INTO Audit_Transacciones
            (TipoOperacion, NodoOrigen, RegistrosAfectados, Estado)
            VALUES (?, ?, ?, ?)
        ";
        $auditStmt = $db->prepare($auditSql);
        $auditStmt->execute([
            'LIMPIEZA',
            'FEDORA_CENTRAL',
            $deletedRows,
            'COMPLETADO'
        ]);

        $response["success"] = true;
        $response["message"] = "Limpieza de logs antiguos completada";
        $response["data"] = [
            "deleted_count" => $deletedRows,
            "retention_days" => 30
        ];
        http_response_code(200);
    }

    // Acción no reconocida
    else {
        http_response_code(400);
        $response["error"] = "Acción no reconocida: " . $action;
        $response["available_actions"] = ["simulate", "archive", "cleanup"];
    }
} catch (PDOException $e) {
    // Manejo de errores de base de datos
    http_response_code(500);
    $response["error"] = "Error de base de datos";
    $response["error_details"] = $e->getMessage();
    error_log("PDO Error en actions.php: " . $e->getMessage());
} catch (Exception $e) {
    // Manejo de errores generales
    http_response_code(500);
    $response["error"] = $e->getMessage();
    error_log("Error en actions.php: " . $e->getMessage());
}

// Enviar respuesta JSON
echo json_encode($response, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE);
?>
