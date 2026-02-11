<?php
// config/database.php
class Database {
    private $host = "127.0.0.1"; // Tu Docker local
    private $db_name = "CentralSIEM";
    private $username = "sa";
    private $password = "TU_CLAVE_AQUI"; // Tu pass fuerte
    public $conn;

public function getConnection() {
    $this->conn = null;
    try {
        $dsn = "sqlsrv:Server=127.0.0.1,1432;Database=CentralSIEM;TrustServerCertificate=true;Encrypt=false";
        $this->conn = new PDO($dsn, $this->username, $this->password);

        $this->conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    } catch(PDOException $exception) {
        // Esto es lo que estaba rompiendo tu JS
        echo "Error de conexión: " . $exception->getMessage();
    }
    return $this->conn;
}
}
?>
