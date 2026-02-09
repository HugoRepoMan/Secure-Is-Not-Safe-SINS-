<?php
// ACTIVAR TODOS LOS ERRORES VISIBLES
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

echo "<h1>🕵️‍♂️ Diagnóstico Final del Sistema</h1>";

// 1. VERIFICAR ARCHIVO DE CONFIGURACIÓN
$configFile = 'config/database.php';
if (!file_exists($configFile)) {
    die("<h3 style='color:red'>❌ FATAL: No encuentro el archivo config/database.php</h3>");
}
echo "<p>✅ Archivo database.php encontrado.</p>";

require_once $configFile;

try {
    // 2. PROBAR CONEXIÓN LOCAL (FEDORA)
    $database = new Database();
    $db = $database->getConnection();
    
    if ($db) {
        echo "<p style='color:green'>✅ <strong>Conexión Local (Docker):</strong> EXITOSA.</p>";
    } else {
        throw new Exception("El objeto de conexión es nulo.");
    }

    // 3. PROBAR TABLA LOCAL (FORENSE)
    echo "<p>🔍 Verificando tabla local 'Forense_Logs'...</p>";
    $queryLocal = "SELECT COUNT(*) as total FROM Forense_Logs";
    $stmt = $db->prepare($queryLocal);
    $stmt->execute();
    $row = $stmt->fetch(PDO::FETCH_ASSOC);
    echo "<p style='color:green'>✅ Tabla Forense_Logs existe. Tiene <strong>" . $row['total'] . "</strong> registros.</p>";

    // 4. PROBAR CONEXIÓN REMOTA (WINDOWS DE ELLA)
    echo "<p>📡 Intentando contactar al Windows de tu compañera ([SENSOR_REMOTO])...</p>";
    echo "<ul><li>Si esto tarda mucho, es el Firewall de ella.</li><li>Si da error inmediato, es la configuración del Linked Server.</li></ul>";
    
    // Consulta simple para ver si responde
    $queryRemote = "SELECT TOP 1 ID FROM [SENSOR_REMOTO].[SensorDB].[dbo].[Live_Alerts]";
    $stmtRemote = $db->prepare($queryRemote);
    $stmtRemote->execute();
    $resultRemote = $stmtRemote->fetch(PDO::FETCH_ASSOC);

    if ($resultRemote) {
        echo "<h2 style='color:green'>🎉 ¡TODO FUNCIONA!</h2>";
        echo "<p>El sistema está leyendo datos de Windows correctamente. ID detectado: " . $resultRemote['ID'] . "</p>";
    } else {
        echo "<h3 style='color:orange'>⚠️ Conexión establecida, pero la tabla remota está vacía.</h3>";
    }

} catch (PDOException $e) {
    echo "<h2 style='color:red'>❌ ERROR DE BASE DE DATOS</h2>";
    echo "<pre>" . $e->getMessage() . "</pre>";
    
    if (strpos($e->getMessage(), 'Login failed') !== false) {
        echo "<p>👉 <strong>Solución:</strong> La contraseña en database.php no coincide con la del Docker.</p>";
    }
    if (strpos($e->getMessage(), 'Invalid object name') !== false) {
        echo "<p>👉 <strong>Solución:</strong> No has creado la tabla o el Linked Server no se llama [SENSOR_REMOTO].</p>";
    }
    if (strpos($e->getMessage(), 'Could not find server') !== false || strpos($e->getMessage(), 'Login timeout') !== false) {
        echo "<p>👉 <strong>Solución:</strong> El Windows de ella no responde (Firewall o IP incorrecta en Linked Server).</p>";
    }
} catch (Exception $e) {
    echo "<h2 style='color:red'>❌ ERROR GENERAL</h2>";
    echo "<pre>" . $e->getMessage() . "</pre>";
}
?>
