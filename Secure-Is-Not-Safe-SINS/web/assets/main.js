/**
 * SIEM Monitoring System - Frontend Controller
 * Implementa arquitectura Cliente-Servidor para acceso a BD distribuidas
 */

// Configuración global
const CONFIG = {
    refreshInterval: 5000, // 5 segundos
    apiBaseUrl: 'api/',
    maxRetries: 3,
    retryDelay: 2000
};

// Estado de la aplicación
let appState = {
    isOnline: true,
    lastUpdate: null,
    retryCount: 0,
    autoRefresh: true
};

/**
 * Inicialización del sistema al cargar el DOM
 */
document.addEventListener("DOMContentLoaded", () => {
    console.log("🚀 Iniciando SIEM Monitoring System...");
    
    // Carga inicial de datos
    loadData();
    
    // Configurar actualización automática
    startAutoRefresh();
    
    // Event listeners para controles
    setupEventListeners();
    
    console.log("✓ Sistema inicializado correctamente");
});

/**
 * Configura event listeners para botones y controles
 */
function setupEventListeners() {
    // Botón de refresh manual
    const refreshBtn = document.getElementById('refresh-btn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', () => {
            console.log("🔄 Actualización manual solicitada");
            loadData();
        });
    }
}

/**
 * Inicia el sistema de actualización automática
 */
function startAutoRefresh() {
    setInterval(() => {
        if (appState.autoRefresh) {
            loadData();
        }
    }, CONFIG.refreshInterval);
}

/**
 * Carga datos desde las APIs (ambos nodos)
 * Implementa patrón de consultas distribuidas
 */
async function loadData() {
    try {
        console.log("📡 Consultando nodos distribuidos...");
        
        // Mostrar indicador de carga
        showLoadingState();
        
        // Realizar petición a la API
        const response = await fetch(`${CONFIG.apiBaseUrl}get_alerts.php`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        // Verificar respuesta
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        // Parsear respuesta JSON
        const data = await response.json();
        
        // Verificar estructura de datos
        if (!data.success) {
            throw new Error(data.error || "Error desconocido en la respuesta");
        }
        
        // Renderizar datos en tablas
        renderTable('live-table', data.data.live, [
            'AlertID', 
            'TipoAtaque', 
            'IP_Origen', 
            'Severidad'
        ]);
        
        renderTable('history-table', data.data.history, [
            'LogID', 
            'TipoAtaque', 
            'IP_Origen', 
            'Fecha_Archivado'
        ]);
        
        // Actualizar estado
        updateSystemStatus(true, data.metadata);
        appState.retryCount = 0;
        
        console.log(`✓ Datos cargados: ${data.metadata.live_count} alertas activas, ${data.metadata.history_count} en histórico`);
        
    } catch (error) {
        console.error("❌ Error al cargar datos:", error);
        handleLoadError(error);
    }
}

/**
 * Ejecuta una acción en el sistema (simulate, archive, cleanup)
 * @param {string} actionType - Tipo de acción a ejecutar
 */
async function triggerAction(actionType) {
    try {
        console.log(`⚡ Ejecutando acción: ${actionType}`);
        
        // Deshabilitar botones durante la operación
        disableActionButtons(true);
        
        // Realizar petición POST a la API
        const response = await fetch(`${CONFIG.apiBaseUrl}actions.php`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ action: actionType })
        });
        
        // Verificar respuesta
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        // Parsear respuesta
        const result = await response.json();
        
        // Verificar éxito
        if (result.success) {
            showNotification(result.message, 'success');
            console.log(`✓ Acción completada:`, result.data);
            
            // Recargar datos inmediatamente
            await loadData();
        } else {
            throw new Error(result.error || "Error desconocido");
        }
        
    } catch (error) {
        console.error(`❌ Error ejecutando acción ${actionType}:`, error);
        showNotification(`Error: ${error.message}`, 'error');
    } finally {
        // Rehabilitar botones
        disableActionButtons(false);
    }
}

/**
 * Renderiza datos en una tabla HTML
 * @param {string} tableId - ID de la tabla
 * @param {Array} data - Datos a renderizar
 * @param {Array} columns - Columnas a mostrar
 */
function renderTable(tableId, data, columns) {
    const tbody = document.querySelector(`#${tableId} tbody`);
    
    if (!tbody) {
        console.error(`❌ Tabla no encontrada: ${tableId}`);
        return;
    }
    
    // Limpiar contenido previo
    tbody.innerHTML = "";
    
    // Manejar caso sin datos
    if (!data || data.length === 0) {
        tbody.innerHTML = `
            <tr class="no-data">
                <td colspan="${columns.length}">
                    <span class="status-icon">ℹ️</span> Sin datos disponibles
                </td>
            </tr>
        `;
        return;
    }
    
    // Renderizar filas
    data.forEach((row, index) => {
        const tr = document.createElement('tr');
        tr.className = 'data-row';
        tr.style.animationDelay = `${index * 0.05}s`;
        
        columns.forEach(col => {
            const td = document.createElement('td');
            
            // Procesamiento especial según el tipo de columna
            if (col === 'Severidad') {
                td.innerHTML = getSeverityBadge(row[col]);
            } else if (col.includes('Fecha') || col === 'Timestamp') {
                td.textContent = formatDateTime(row[col]);
            } else {
                td.textContent = row[col] ?? 'N/A';
            }
            
            tr.appendChild(td);
        });
        
        tbody.appendChild(tr);
    });
}

/**
 * Genera un badge HTML para el nivel de severidad
 * @param {string} severity - Nivel de severidad
 * @returns {string} HTML del badge
 */
function getSeverityBadge(severity) {
    const badges = {
        'CRITICAL': '<span class="badge badge-critical">🔴 CRÍTICO</span>',
        'HIGH': '<span class="badge badge-high">🟠 ALTO</span>',
        'MEDIUM': '<span class="badge badge-medium">🟡 MEDIO</span>',
        'LOW': '<span class="badge badge-low">🟢 BAJO</span>'
    };
    
    return badges[severity] || `<span class="badge">${severity}</span>`;
}

/**
 * Formatea fecha y hora
 * @param {string|object} datetime - Fecha a formatear
 * @returns {string} Fecha formateada
 */
function formatDateTime(datetime) {
    if (!datetime) return 'N/A';
    
    // Si es un objeto de SQL Server
    if (typeof datetime === 'object' && datetime.date) {
        datetime = datetime.date;
    }
    
    try {
        // Remover microsegundos y zona horaria
        const cleanDate = datetime.split('.')[0];
        const date = new Date(cleanDate);
        
        if (isNaN(date.getTime())) {
            return datetime;
        }
        
        return date.toLocaleString('es-EC', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    } catch (e) {
        return datetime;
    }
}

/**
 * Actualiza el estado del sistema en la UI
 * @param {boolean} isOnline - Estado de conexión
 * @param {object} metadata - Metadatos adicionales
 */
function updateSystemStatus(isOnline, metadata = null) {
    const statusIcon = document.getElementById('status-icon');
    
    if (statusIcon) {
        if (isOnline) {
            statusIcon.innerHTML = '🟢 Online';
            statusIcon.className = 'status-online';
        } else {
            statusIcon.innerHTML = '🔴 Desconectado';
            statusIcon.className = 'status-offline';
        }
    }
    
    // Actualizar timestamp
    appState.lastUpdate = new Date();
    appState.isOnline = isOnline;
}

/**
 * Muestra estado de carga en las tablas
 */
function showLoadingState() {
    const tables = ['live-table', 'history-table'];
    
    tables.forEach(tableId => {
        const tbody = document.querySelector(`#${tableId} tbody`);
        if (tbody) {
            tbody.innerHTML = `
                <tr class="loading-row">
                    <td colspan="4">
                        <span class="loading-spinner">⏳</span> Cargando datos...
                    </td>
                </tr>
            `;
        }
    });
}

/**
 * Maneja errores de carga de datos
 * @param {Error} error - Error capturado
 */
function handleLoadError(error) {
    appState.retryCount++;
    
    if (appState.retryCount < CONFIG.maxRetries) {
        console.log(`🔄 Reintentando... (${appState.retryCount}/${CONFIG.maxRetries})`);
        setTimeout(loadData, CONFIG.retryDelay);
    } else {
        updateSystemStatus(false);
        showNotification('Error de conexión con el servidor. Verifique la configuración.', 'error');
        
        // Mostrar mensaje en tablas
        const tables = ['live-table', 'history-table'];
        tables.forEach(tableId => {
            const tbody = document.querySelector(`#${tableId} tbody`);
            if (tbody) {
                tbody.innerHTML = `
                    <tr class="error-row">
                        <td colspan="4">
                            ❌ Error de conexión: ${error.message}
                        </td>
                    </tr>
                `;
            }
        });
    }
}

/**
 * Muestra una notificación al usuario
 * @param {string} message - Mensaje a mostrar
 * @param {string} type - Tipo de notificación (success, error, info)
 */
function showNotification(message, type = 'info') {
    // Crear elemento de notificación
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Agregar al DOM
    document.body.appendChild(notification);
    
    // Animar entrada
    setTimeout(() => notification.classList.add('show'), 10);
    
    // Remover después de 3 segundos
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

/**
 * Deshabilita/habilita botones de acción
 * @param {boolean} disable - True para deshabilitar
 */
function disableActionButtons(disable) {
    const buttons = document.querySelectorAll('.controls button');
    buttons.forEach(btn => {
        btn.disabled = disable;
        if (disable) {
            btn.classList.add('disabled');
        } else {
            btn.classList.remove('disabled');
        }
    });
}

// Exponer funciones globales para uso desde HTML
window.triggerAction = triggerAction;
window.loadData = loadData;
