# 📤 Guía para Subir el Proyecto a GitHub

## Preparación Inicial

### 1. Crear Repositorio en GitHub

1. Ve a https://github.com y haz login
2. Click en el botón "+" arriba a la derecha → "New repository"
3. Configuración:
   - **Repository name**: `siem-distributed-security`
   - **Description**: "Sistema SIEM Distribuido con Detección de Ataques Reales - Proyecto de Bases de Datos Distribuidas"
   - **Visibilidad**: Público o Privado (según prefieras)
   - **NO marcar** "Initialize this repository with a README" (ya tenemos uno)
4. Click en "Create repository"

### 2. Configurar Git Local

```bash
# Navegar al directorio del proyecto
cd siem-distributed-security

# Inicializar repositorio Git
git init

# Configurar tu información (si no lo has hecho antes)
git config --global user.name "Tu Nombre"
git config --global user.email "tu_email@ejemplo.com"
```

### 3. Preparar Archivos

```bash
# Verificar que .gitignore existe
cat .gitignore

# IMPORTANTE: Eliminar credenciales del código
# Editar cada archivo y reemplazar contraseñas reales por placeholders

# En detectors/network_ids.py, ssh_bruteforce.py, honeypot.py
# Cambiar:
#   'password': 'TuPasswordReal123'
# Por:
#   'password': 'TU_PASSWORD_AQUI'

# En dashboard/config/database.php
# Cambiar:
#   $pwd = "TuPasswordReal123";
# Por:
#   $pwd = "TU_PASSWORD_AQUI";
```

### 4. Agregar Archivos al Repositorio

```bash
# Agregar todos los archivos
git add .

# Verificar qué se va a subir
git status

# Crear el primer commit
git commit -m "Initial commit: SIEM Distribuido con detección de ataques reales"
```

### 5. Conectar con GitHub

```bash
# Reemplazar TU_USUARIO con tu nombre de usuario de GitHub
git remote add origin https://github.com/TU_USUARIO/siem-distributed-security.git

# Verificar que se agregó correctamente
git remote -v
```

### 6. Subir al Repositorio

```bash
# Subir el código (primera vez)
git push -u origin main

# O si usa 'master' en lugar de 'main':
git push -u origin master
```

## Estructura que se Subirá

```
siem-distributed-security/
├── README.md                    # ✅ Descripción principal
├── LICENSE                      # ✅ Licencia MIT
├── INICIO_RAPIDO.md            # ✅ Guía de inicio rápido
├── .gitignore                  # ✅ Archivos a ignorar
├── config.example.py           # ✅ Configuración de ejemplo
├── setup.sh                    # ✅ Script de configuración
│
├── dashboard/                  # ✅ Dashboard web
│   ├── index.html
│   ├── assets/
│   ├── api/
│   └── config/
│
├── detectors/                  # ✅ Detectores de ataques
│   ├── network_ids.py
│   ├── ssh_bruteforce.py
│   └── honeypot.py
│
├── database/                   # ✅ Scripts SQL
│   └── setup_real_attacks.sql
│
├── scripts/                    # ✅ Herramientas auxiliares
│   ├── install.sh
│   └── attack_generator.py
│
└── docs/                       # ✅ Documentación
    ├── INSTALACION.md
    ├── USO.md
    └── DEMOSTRACION.md
```

## Personalizar el Repositorio

### Crear un README atractivo

El README.md ya está creado, pero personaliza:

1. Reemplaza `[Tu Nombre]` con tu nombre real
2. Reemplaza `[Universidad]` con tu universidad
3. Reemplaza `[Nombre del profesor]` 
4. Reemplaza `[tu_email@ejemplo.com]`
5. Reemplaza `[@TU_USUARIO]` con tu usuario de GitHub

```bash
# Editar README.md
nano README.md

# Guardar cambios
git add README.md
git commit -m "Personalizar información del README"
git push
```

### Agregar Badges/Insignias

Edita README.md y agrega al inicio (después del título):

```markdown
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![SQL Server](https://img.shields.io/badge/SQL%20Server-2019+-red.svg)](https://www.microsoft.com/sql-server)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/TU_USUARIO/siem-distributed-security/graphs/commit-activity)
```

### Agregar Topics/Temas

En GitHub, en la página de tu repositorio:
1. Click en el ícono de engranaje ⚙️ junto a "About"
2. Agregar topics:
   - `siem`
   - `cybersecurity`
   - `intrusion-detection`
   - `distributed-database`
   - `sql-server`
   - `python`
   - `honeypot`
   - `network-security`

### Crear Releases (Opcional)

```bash
# Crear un tag para la versión 1.0
git tag -a v1.0 -m "Versión 1.0 - Proyecto final"
git push origin v1.0
```

Luego en GitHub:
1. Ve a "Releases"
2. Click en "Create a new release"
3. Selecciona el tag `v1.0`
4. Título: "v1.0 - Sistema SIEM Distribuido Completo"
5. Descripción: Lista de características
6. Click en "Publish release"

## Mantener el Repositorio

### Hacer cambios y actualizarlos

```bash
# Después de modificar archivos
git add .
git commit -m "Descripción de los cambios"
git push
```

### Crear ramas para nuevas funcionalidades

```bash
# Crear rama para nueva feature
git checkout -b feature/mejora-detectores

# Hacer cambios...
git add .
git commit -m "Mejorar algoritmo de detección"

# Subir rama
git push origin feature/mejora-detectores

# Luego crear Pull Request en GitHub
```

## Compartir el Repositorio

### Obtener el enlace

Tu repositorio estará en:
```
https://github.com/TU_USUARIO/siem-distributed-security
```

### Clonar desde otra máquina

Cualquier persona (si es público) puede clonar:
```bash
git clone https://github.com/TU_USUARIO/siem-distributed-security.git
```

### Agregar colaboradores

Si es privado y quieres agregar a tu compañero/a:
1. Settings → Manage access
2. Click "Invite a collaborator"
3. Ingresar username de GitHub

## Checklist Pre-Subida

Antes de hacer `git push` por primera vez, verifica:

- [ ] README.md personalizado con tu información
- [ ] Todas las contraseñas reemplazadas por placeholders
- [ ] .gitignore incluye archivos sensibles
- [ ] Licencia MIT incluida
- [ ] Documentación completa en /docs
- [ ] Scripts tienen permisos de ejecución
- [ ] No hay archivos .pyc o __pycache__
- [ ] No hay archivos .bak o temporales
- [ ] Todas las rutas son relativas (no absolutas)
- [ ] Comentarios en español/inglés consistentes

## Presentación del Repositorio al Profesor

### En tu presentación, menciona:

> "El código completo está disponible en GitHub en:
> https://github.com/TU_USUARIO/siem-distributed-security
>
> Incluye:
> - Documentación completa de instalación y uso
> - Todos los scripts de detectores
> - Dashboard web funcional
> - Scripts de configuración automatizada
> - Guía de demostración
>
> El repositorio está bajo licencia MIT y puede ser usado con fines académicos."

### Mostrar en pantalla (opcional):

Si tienes tiempo durante la demo, puedes:
1. Abrir el repositorio en GitHub
2. Mostrar la estructura de archivos
3. Mostrar el README bien formateado
4. Mencionar los commits y la actividad

## Mejoras Futuras para el Repo

Ideas para agregar después de la presentación:

- [ ] Agregar GitHub Actions para CI/CD
- [ ] Crear Wiki con documentación extendida
- [ ] Agregar Issues con TODOs
- [ ] Crear Projects para organizar tareas
- [ ] Agregar screenshots del dashboard
- [ ] Video demo en YouTube
- [ ] Documentación en inglés también
- [ ] Tests automatizados

## Comandos Útiles de Git

```bash
# Ver estado actual
git status

# Ver historial de commits
git log --oneline

# Ver diferencias antes de commit
git diff

# Deshacer cambios no commiteados
git checkout -- archivo.py

# Ver ramas
git branch

# Cambiar de rama
git checkout nombre-rama

# Actualizar desde GitHub
git pull

# Clonar en otra máquina
git clone https://github.com/TU_USUARIO/siem-distributed-security.git
```

## Solución de Problemas

### Error: "remote origin already exists"
```bash
git remote remove origin
git remote add origin https://github.com/TU_USUARIO/siem-distributed-security.git
```

### Error: "failed to push some refs"
```bash
# Si el repo remoto tiene cambios
git pull origin main --rebase
git push origin main
```

### Error: Archivos muy grandes
```bash
# Git tiene límite de 100MB por archivo
# Agregar a .gitignore si son archivos grandes innecesarios
echo "archivo_grande.iso" >> .gitignore
```

### Olvidaste remover contraseñas
```bash
# Editar archivo
nano detectors/network_ids.py

# Volver a commit
git add detectors/network_ids.py
git commit --amend --no-edit
git push --force  # ⚠️ Solo si nadie más usa el repo
```

---

## 🎉 ¡Listo!

Tu proyecto está ahora en GitHub, bien organizado y documentado.

**Próximos pasos:**
1. Comparte el enlace con tu profesor
2. Agrega el enlace en tu CV
3. Muéstralo en tu portafolio de proyectos

**Enlace de ejemplo:**
```
🔗 GitHub: github.com/TU_USUARIO/siem-distributed-security
```
