# 📚 Wordlists para Attack Generator

Este directorio contiene wordlists profesionales para diferentes tipos de ataques de seguridad.

## 📁 Archivos Incluidos

### common_ports.txt
Lista de los puertos TCP más comunes escaneados en auditorías de seguridad.
- **Formato**: `puerto,servicio,descripción`
- **Total**: 35+ puertos comunes
- **Uso**: Port scanning realista
- **Fuente**: Basado en escaneos Nmap y IANA registry

### usernames.txt
Nombres de usuario comunes encontrados en ataques de fuerza bruta.
- **Total**: 40+ usuarios
- **Uso**: SSH/FTP/Telnet brute force
- **Incluye**: Usuarios de sistema, servicios, y administrativos
- **Fuente**: Análisis de ataques reales y honeypots

### passwords.txt
Las 100 contraseñas más comunes de bases de datos filtradas.
- **Total**: 100 contraseñas
- **Uso**: Brute force attacks
- **Categorías**: 
  - Contraseñas numéricas
  - Palabras comunes
  - Patrones de teclado
  - Defaults de sistemas
- **Fuente**: Recopilación de brechas de datos públicas
- **⚠️ ADVERTENCIA**: NUNCA usar estas contraseñas en sistemas reales

### sql_injection.txt
Payloads de SQL Injection de nivel profesional.
- **Total**: 70+ payloads
- **Técnicas incluidas**:
  - Boolean-based blind
  - Union-based
  - Error-based
  - Time-based blind
  - Stacked queries
  - Second-order injection
  - NoSQL injection
- **Bases de datos**: MySQL, PostgreSQL, MSSQL, Oracle
- **Fuente**: OWASP, SQLMap, investigación de seguridad

### xss_payloads.txt
Vectores de Cross-Site Scripting (XSS) avanzados.
- **Total**: 90+ payloads
- **Tipos incluidos**:
  - Reflected XSS
  - Stored XSS
  - DOM-based XSS
  - Template injection (Angular, Vue, React)
  - Filter bypass techniques
  - Polyglot XSS
  - Cookie stealing
  - Keyloggers
- **Fuente**: OWASP XSS Filter Evasion, PortSwigger, investigación propia

## 🎯 Uso

### En el Attack Generator

El script `attack_generator_v2.py` carga automáticamente estas wordlists:

```python
from wordlist_loader import WordlistLoader

loader = WordlistLoader('wordlists')

# Cargar listas
ports = loader.load_ports()
users = loader.load_usernames()
passwords = loader.load_passwords()
sql_payloads = loader.load_sql_payloads()
xss_payloads = loader.load_xss_payloads()
```

### Formato de Archivos

- **Codificación**: UTF-8
- **Líneas que comienzan con #**: Comentarios (ignorados)
- **Líneas vacías**: Ignoradas
- **Un elemento por línea**: Para facilitar lectura

### Personalización

Puedes agregar tus propias entradas:

```bash
# Agregar puerto personalizado
echo "9999,CustomApp,My Custom Application" >> common_ports.txt

# Agregar usuario
echo "miusuario" >> usernames.txt

# Agregar contraseña
echo "MiPassword123!" >> passwords.txt
```

## 🔒 Consideraciones de Seguridad

### ⚠️ IMPORTANTE

1. **Solo uso educativo**: Estas wordlists son para aprendizaje y testing autorizado
2. **No usar contraseñas reales**: Las contraseñas en passwords.txt son DÉBILES
3. **Autorización requerida**: Solo usar en sistemas propios o con permiso explícito
4. **Confidencialidad**: No compartir resultados de escaneos sin autorización

### 🛡️ Buenas Prácticas

```bash
# Limitar permisos de lectura
chmod 600 wordlists/*.txt

# Hacer backup antes de modificar
cp wordlists/passwords.txt wordlists/passwords.txt.backup

# Usar solo en red aislada
# Documentar todos los tests realizados
```

## 📊 Estadísticas

| Wordlist | Entradas | Tamaño | Uso Principal |
|----------|----------|--------|---------------|
| common_ports.txt | 35+ | ~2KB | Port scanning |
| usernames.txt | 40+ | ~500B | Brute force |
| passwords.txt | 100+ | ~1.5KB | Brute force |
| sql_injection.txt | 70+ | ~3KB | SQLi testing |
| xss_payloads.txt | 90+ | ~5KB | XSS testing |

## 🔄 Actualización

Para mantener las wordlists actualizadas:

```bash
# Descargar wordlists adicionales de SecLists
git clone https://github.com/danielmiessler/SecLists.git

# Fusionar con nuestras listas
cat SecLists/Passwords/Common-Credentials/10-million-password-list-top-100.txt >> passwords.txt

# Eliminar duplicados
sort -u passwords.txt -o passwords.txt
```

## 📚 Recursos Adicionales

### Fuentes de Wordlists Profesionales

- **SecLists**: https://github.com/danielmiessler/SecLists
- **PayloadsAllTheThings**: https://github.com/swisskyrepo/PayloadsAllTheThings
- **FuzzDB**: https://github.com/fuzzdb-project/fuzzdb
- **OWASP**: https://owasp.org/www-community/attacks/

### Herramientas que usan Wordlists

- **Nmap**: Port scanning
- **Hydra**: Brute force
- **SQLMap**: SQL injection
- **Burp Suite**: Web application testing
- **OWASP ZAP**: Security scanning

## 📝 Notas

- Las wordlists se cargan en memoria al inicio del script para mejor rendimiento
- Los comentarios (#) permiten documentar cada entrada
- El formato CSV en common_ports.txt facilita la generación de reportes
- Todas las listas pueden ser extendidas sin modificar el código

## ⚖️ Licencia y Atribución

- **Licencia**: MIT (solo uso educativo)
- **Atribución**: Basado en investigación de seguridad pública
- **Disclaimer**: Los autores no se responsabilizan por uso indebido

---

**Última actualización**: Febrero 2026  
**Mantenido por**: Equipo SIEM Project
