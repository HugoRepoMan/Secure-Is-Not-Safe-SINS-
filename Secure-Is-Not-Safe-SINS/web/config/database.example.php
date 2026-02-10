<?php
/**
 * Clase Database - Gestión de conexión a Base de Datos Distribuida
 * Implementa patrón Singleton para garantizar una única instancia de conexión
 * Soporta bases de datos heterogéneas (SQL Server distribuido)
 */
class Database {
    // Instancia única (Singleton)
    private static $instance = null;
    
    // Configuración de conexión - Nodo Central (Fedora)
    private $host = "127.0.0.1";
    private $port = "1432";
    private $db_name = "CentralSIEM";
    private $username = "sa";
    private $password = "CyberPass2026";
    
    // Conexión PDO
    public $conn;
    
    // Constructor privado para implementar Singleton
    private function __construct() {}
    
    /**
     * Obtiene la instancia única de Database (Patrón Singleton)
     * @return Database Instancia única
     */
    public static function getInstance() {
        if (self::$instance === null) {
            self::$instance = new self();
        }
        return self::$instance;
    }
    
    /**
     * Establece la conexión con la base de datos
     * @return PDO|null Conexión PDO o null en caso de error
     */
    public function getConnection() {
        if ($this->conn !== null) {
            return $this->conn;
        }
        
        try {
            // DSN para SQL Server con configuración segura
            $dsn = "sqlsrv:Server={$this->host},{$this->port};Database={$this->db_name};TrustServerCertificate=true;Encrypt=false";
            
            // Establecer conexión PDO
            $this->conn = new PDO($dsn, $this->username, $this->password);
            
            // Configurar atributos de PDO
            $this->conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
            $this->conn->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);
            $this->conn->setAttribute(PDO::ATTR_EMULATE_PREPARES, false);
            
            // Log de conexión exitosa (solo en desarrollo)
            if ($this->isDevEnvironment()) {
                error_log("✓ Conexión exitosa a {$this->db_name} en {$this->host}:{$this->port}");
            }
            
        } catch(PDOException $exception) {
            // Manejo de errores sin exponer información sensible en producción
            $errorMessage = "Error de conexión a la base de datos";
            
            if ($this->isDevEnvironment()) {
                // En desarrollo, mostrar detalles completos
                error_log("✗ Error de conexión: " . $exception->getMessage());
                error_log("DSN usado: " . $dsn);
            } else {
                // En producción, solo registrar en logs del servidor
                error_log("DB Connection Error: " . $exception->getMessage());
            }
            
            // NO hacer echo aquí - esto rompe el JSON en las APIs
            // El llamador debe manejar el null
            return null;
        }
        
        return $this->conn;
    }
    
    /**
     * Verifica si estamos en entorno de desarrollo
     * @return bool True si es desarrollo
     */
    private function isDevEnvironment() {
        return !isset($_SERVER['SERVER_NAME']) || 
               $_SERVER['SERVER_NAME'] === 'localhost' || 
               $_SERVER['SERVER_ADDR'] === '127.0.0.1';
    }
    
    /**
     * Cierra la conexión a la base de datos
     */
    public function closeConnection() {
        $this->conn = null;
    }
    
    /**
     * Previene la clonación del objeto (parte del patrón Singleton)
     */
    private function __clone() {}
    
    /**
     * Previene la deserialización del objeto (parte del patrón Singleton)
     */
    public function __wakeup() {
        throw new Exception("Cannot unserialize singleton");
    }
}
?>
