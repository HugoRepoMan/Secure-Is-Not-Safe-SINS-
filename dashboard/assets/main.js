// Variables globales para almacenar datos
let allLiveAlerts = [];
let allArchiveAlerts = [];
let currentFilter = 'all';
let currentSearchTerm = '';

// Mapeo de tipos de ataque (normalización)
const attackTypeMap = {
    'Port Scanning': 'Port Scanning',
    'port scanning': 'Port Scanning',
    'PORT SCAN': 'Port Scanning',
    'port_scan': 'Port Scanning',
    
    'SYN Flood': 'SYN Flood',
    'syn flood': 'SYN Flood',
    'SYN_FLOOD': 'SYN Flood',
    
    'ICMP Flood': 'ICMP Flood',
    'icmp flood': 'ICMP Flood',
    'ICMP_FLOOD': 'ICMP Flood',
    
    'SQL Injection': 'SQL Injection',
    'sql injection': 'SQL Injection',
    'SQL_INJECTION': 'SQL Injection',
    'SQLi': 'SQL Injection',
    
    'XSS': 'XSS',
    'xss': 'XSS',
    'Cross-Site Scripting': 'XSS',
    'XSS Attack': 'XSS',
    
    'SSH Brute Force': 'SSH Brute Force',
    'ssh brute force': 'SSH Brute Force',
    'SSH_BRUTE_FORCE': 'SSH Brute Force',
    'brute force': 'SSH Brute Force',
    
    'Honeypot': 'Honeypot',
    'honeypot': 'Honeypot',
    'HONEYPOT': 'Honeypot',
    'Honeypot Trigger': 'Honeypot'
};

document.addEventListener("DOMContentLoaded", () => {
    loadData();
    // Actualizar cada 5 segundos automáticamente
    setInterval(loadData, 5000); 
});

async function loadData() {
    try {
        const response = await fetch('api/get_alerts.php');
        const data = await response.json();
        
        // Guardar datos en variables globales
        allLiveAlerts = data.live || [];
        allArchiveAlerts = data.history || [];
        
        // Normalizar tipos de ataque
        allLiveAlerts = normalizeAttackTypes(allLiveAlerts);
        allArchiveAlerts = normalizeAttackTypes(allArchiveAlerts);
        
        // Actualizar contadores
        updateAttackCounts();
        updateSeverityCounts();
        updateBadges();
        
        // Renderizar tablas con filtros actuales
        applyFilters();
        
    } catch (error) {
        console.error("Error cargando datos:", error);
        document.querySelector('#status-icon').textContent = '🔴 Offline';
    }
}

function normalizeAttackTypes(alerts) {
    return alerts.map(alert => {
        const normalized = attackTypeMap[alert.TipoAtaque] || alert.TipoAtaque;
        return { ...alert, TipoAtaque: normalized };
    });
}

function updateAttackCounts() {
    const counts = {
        all: allLiveAlerts.length,
        'Port Scanning': 0,
        'SYN Flood': 0,
        'ICMP Flood': 0,
        'SQL Injection': 0,
        'XSS': 0,
        'SSH Brute Force': 0,
        'Honeypot': 0
    };
    
    allLiveAlerts.forEach(alert => {
        const type = alert.TipoAtaque;
        if (counts.hasOwnProperty(type)) {
            counts[type]++;
        }
    });
    
    // Actualizar contadores en botones
    document.getElementById('count-all').textContent = counts.all;
    document.getElementById('count-port').textContent = counts['Port Scanning'];
    document.getElementById('count-syn').textContent = counts['SYN Flood'];
    document.getElementById('count-icmp').textContent = counts['ICMP Flood'];
    document.getElementById('count-sql').textContent = counts['SQL Injection'];
    document.getElementById('count-xss').textContent = counts['XSS'];
    document.getElementById('count-ssh').textContent = counts['SSH Brute Force'];
    document.getElementById('count-honeypot').textContent = counts['Honeypot'];
}

function updateSeverityCounts() {
    const severityCounts = {
        CRITICAL: 0,
        HIGH: 0,
        MEDIUM: 0,
        LOW: 0
    };
    
    allLiveAlerts.forEach(alert => {
        const severity = (alert.Severidad || 'LOW').toUpperCase();
        if (severityCounts.hasOwnProperty(severity)) {
            severityCounts[severity]++;
        } else {
            severityCounts.LOW++;
        }
    });
    
    document.getElementById('critical-count').textContent = severityCounts.CRITICAL;
    document.getElementById('high-count').textContent = severityCounts.HIGH;
    document.getElementById('medium-count').textContent = severityCounts.MEDIUM;
    document.getElementById('low-count').textContent = severityCounts.LOW;
}

function updateBadges() {
    document.getElementById('live-badge').textContent = 
        `${allLiveAlerts.length} ${allLiveAlerts.length === 1 ? 'alerta' : 'alertas'}`;
    document.getElementById('archive-badge').textContent = 
        `${allArchiveAlerts.length} ${allArchiveAlerts.length === 1 ? 'archivado' : 'archivados'}`;
}

function filterByType(type) {
    currentFilter = type;
    
    // Actualizar botones activos
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.closest('.filter-btn').classList.add('active');
    
    // Aplicar filtros
    applyFilters();
}

function searchByIP() {
    currentSearchTerm = document.getElementById('search-input').value.toLowerCase();
    applyFilters();
}

function clearFilters() {
    currentFilter = 'all';
    currentSearchTerm = '';
    document.getElementById('search-input').value = '';
    
    // Resetear botón activo
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector('.filter-btn').classList.add('active');
    
    applyFilters();
}

function applyFilters() {
    // Filtrar alertas en vivo
    let filteredLive = allLiveAlerts;
    
    // Filtro por tipo
    if (currentFilter !== 'all') {
        filteredLive = filteredLive.filter(alert => 
            alert.TipoAtaque === currentFilter
        );
    }
    
    // Filtro por IP
    if (currentSearchTerm) {
        filteredLive = filteredLive.filter(alert => 
            (alert.IP_Origen || '').toLowerCase().includes(currentSearchTerm)
        );
    }
    
    // Filtrar alertas archivadas (solo por IP de búsqueda)
    let filteredArchive = allArchiveAlerts;
    if (currentSearchTerm) {
        filteredArchive = filteredArchive.filter(alert => 
            (alert.IP_Origen || '').toLowerCase().includes(currentSearchTerm)
        );
    }
    
    // Renderizar tablas
    renderTable('live-table', filteredLive, ['AlertID', 'TipoAtaque', 'IP_Origen', 'Severidad', 'Timestamp']);
    renderTable('history-table', filteredArchive, ['LogID', 'TipoAtaque', 'IP_Origen', 'Fecha_Archivado']);
}

async function triggerAction(actionType) {
    try {
        const response = await fetch('api/actions.php', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action: actionType })
        });
        const result = await response.json();
        alert(result.message || "Acción completada");
        loadData(); // Recargar tablas inmediatamente
    } catch (error) {
        alert("Error ejecutando acción");
    }
}

function renderTable(tableId, data, columns) {
    const tbody = document.querySelector(`#${tableId} tbody`);
    tbody.innerHTML = "";
    
    if(data.length === 0) {
        tbody.innerHTML = `<tr><td colspan='${columns.length}' class='no-data'>
            ${currentFilter !== 'all' || currentSearchTerm ? 
                '🔍 No hay resultados con los filtros aplicados' : 
                '📭 Sin datos...'}
        </td></tr>`;
        return;
    }

    data.forEach(row => {
        const tr = document.createElement('tr');
        
        // Agregar clase de severidad a la fila
        if (row.Severidad) {
            tr.classList.add(`severity-${row.Severidad.toLowerCase()}`);
        }
        
        columns.forEach(col => {
            const td = document.createElement('td');
            
            // Manejo especial para fechas de SQL Server
            if(typeof row[col] === 'object' && row[col] !== null && row[col].date){
                td.textContent = formatDate(row[col].date);
            } 
            // Agregar icono según tipo de ataque
            else if (col === 'TipoAtaque') {
                td.innerHTML = getAttackIcon(row[col]) + ' ' + row[col];
            }
            // Agregar badge de severidad
            else if (col === 'Severidad') {
                td.innerHTML = getSeverityBadge(row[col]);
            }
            // Resaltar IP si hay búsqueda activa
            else if (col === 'IP_Origen' && currentSearchTerm) {
                const ip = row[col] || '';
                const highlightedIP = ip.replace(
                    new RegExp(currentSearchTerm, 'gi'), 
                    match => `<mark>${match}</mark>`
                );
                td.innerHTML = highlightedIP;
            }
            else {
                td.textContent = row[col] || '-';
            }
            
            tr.appendChild(td);
        });
        tbody.appendChild(tr);
    });
}

function getAttackIcon(attackType) {
    const icons = {
        'Port Scanning': '🔍',
        'SYN Flood': '💥',
        'ICMP Flood': '📡',
        'SQL Injection': '💉',
        'XSS': '🔗',
        'SSH Brute Force': '🔐',
        'Honeypot': '🍯'
    };
    return icons[attackType] || '⚠️';
}

function getSeverityBadge(severity) {
    const badges = {
        'CRITICAL': '<span class="severity-badge critical">🔴 CRITICAL</span>',
        'HIGH': '<span class="severity-badge high">🟠 HIGH</span>',
        'MEDIUM': '<span class="severity-badge medium">🟡 MEDIUM</span>',
        'LOW': '<span class="severity-badge low">🟢 LOW</span>'
    };
    return badges[severity] || badges['LOW'];
}

function formatDate(dateString) {
    // Formato: 2026-02-10 15:30:22
    const parts = dateString.split('.')[0].split(' ');
    if (parts.length === 2) {
        const [date, time] = parts;
        const [year, month, day] = date.split('-');
        const [hour, minute] = time.split(':');
        return `${day}/${month} ${hour}:${minute}`;
    }
    return dateString.split('.')[0];
}

// Exportar datos (bonus feature)
function exportToCSV() {
    let csv = 'ID,Tipo de Ataque,IP Origen,Severidad,Timestamp\n';
    
    allLiveAlerts.forEach(alert => {
        csv += `${alert.AlertID},"${alert.TipoAtaque}",${alert.IP_Origen},${alert.Severidad},${alert.Timestamp}\n`;
    });
    
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `siem_alerts_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
}
