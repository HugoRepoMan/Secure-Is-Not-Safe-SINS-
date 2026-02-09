<?php
// Habilitar reporte de errores en pantalla
error_reporting(E_ALL);
ini_set('display_errors', 1);

echo "<h1>Diagnóstico de Conexión</h1>";

try {
    // 1. Datos de Conexión (IGUAL QUE EN TU DATABASE.PHP)
    $host = "127.0.0.1,1432";
    $dbname = "CentralSIEM";
    $user = "sa";
    $pass = "CyberPass2026"; // <--- Tu clave nueva

    echo "<p>Intentando conectar a: <strong>$host</strong>...</p>";

    // 2. Crear conexión
    $dsn = "sqlsrv:Server=$host;Database=$dbname;TrustServerCertificate=true;Encrypt=false";
    $conn = new PDO($dsn, $user, $pass);
    $conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

    echo "<h2 style='color:green'>✅ ¡ÉXITO TOTAL! La conexión PHP -> SQL funciona.</h2>";
    echo "<p>Si ves esto, el problema está en otro archivo (get_alerts.php).</p>";

} catch (PDOException $e) {
    echo "<h2 style='color:red'>❌ ERROR FATAL</h2>";
    echo "<p><strong>El servidor dice:</strong> " . $e->getMessage() . "</p>";
    
    // Pistas comunes basadas en el error
    if (strpos($e->getMessage(), 'Login failed') !== false) {
        echo "<p>👉 <strong>Pista:</strong> La contraseña en el archivo PHP no coincide con la del Docker.</p>";
    }
    if (strpos($e->getMessage(), 'TCP Provider') !== false) {
        echo "<p>👉 <strong>Pista:</strong> El puerto 1432 está cerrado o Docker no está corriendo.</p>";
    }
    if (strpos($e->getMessage(), 'could not find driver') !== false) {
        echo "<p>👉 <strong>Pista:</strong> Te faltan los drivers o reiniciar Apache.</p>";
    }
}
?>
