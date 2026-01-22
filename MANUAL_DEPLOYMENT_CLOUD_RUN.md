# 📘 MANUAL COMPLETO: Deployment de Aplicación Flask en Google Cloud Run

## 📋 ÍNDICE

1. [Preparación del Proyecto](#1-preparación-del-proyecto)
2. [Configuración de Git y GitHub](#2-configuración-de-git-y-github)
3. [Creación del Dockerfile](#3-creación-del-dockerfile)
4. [Configuración de Cloud Run](#4-configuración-de-cloud-run)
5. [Solución de Problemas Comunes](#5-solución-de-problemas-comunes)
6. [Checklist Final](#6-checklist-final)

---

## 1. PREPARACIÓN DEL PROYECTO

### 1.1 Estructura del Proyecto

Asegúrate de tener esta estructura básica:

```
tu-proyecto/
├── app.py                 # Aplicación Flask principal
├── requirements.txt       # Dependencias Python
├── Dockerfile            # Configuración Docker (lo crearemos)
├── .gitignore           # Archivos a ignorar en Git
└── static/              # Archivos estáticos (CSS, imágenes, etc.)
    ├── css/
    └── images/
└── templates/           # Templates HTML
    └── *.html
```

### 1.2 Verificar requirements.txt

Asegúrate de tener todas las dependencias necesarias:

```txt
Flask==3.0.3
mysql-connector-python==9.0.0
pdfkit==1.0.0
```

### 1.3 Verificar app.py

Al final de `app.py` debe tener:

```python
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
```

**⚠️ IMPORTANTE:**
- `host="0.0.0.0"` (no `localhost`)
- Usar `os.environ.get("PORT", 8080)` (no `os.getenv()`)
- Sin `debug=True` en producción

---

## 2. CONFIGURACIÓN DE GIT Y GITHUB

### 2.1 Inicializar Repositorio Git

```bash
# Navegar a tu proyecto
cd ruta/a/tu/proyecto

# Inicializar Git
git init

# Crear .gitignore (si no existe)
```

### 2.2 Crear .gitignore

Crea un archivo `.gitignore` con este contenido:

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/
.venv

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Environment variables
.env
.env.local

# Logs
*.log
logs/

# OS
.DS_Store
Thumbs.db
desktop.ini

# Flask
instance/
.webassets-cache
```

### 2.3 Crear Repositorio en GitHub

1. Ve a https://github.com
2. Haz clic en **"New repository"** o **"Nuevo repositorio"**
3. Nombre: `tu-proyecto` (o el que prefieras)
4. **NO** marques "Initialize with README"
5. Haz clic en **"Create repository"**

### 2.4 Subir Código a GitHub

```bash
# Agregar archivos
git add .

# Primer commit
git commit -m "Initial commit: Aplicación Flask"

# Agregar remote (reemplaza USERNAME y REPO con tus datos)
git remote add origin https://github.com/USERNAME/REPO.git

# Renombrar rama a main (si es necesario)
git branch -M main

# Subir código
git push -u origin main
```

### 2.5 Verificar en GitHub

- Ve a tu repositorio en GitHub
- Verifica que todos los archivos estén presentes
- Verifica que la rama se llame `main` (no `master`)

---

## 3. CREACIÓN DEL DOCKERFILE

### 3.1 Crear Dockerfile en la Raíz

Crea un archivo llamado exactamente `Dockerfile` (sin extensión) en la raíz del proyecto.

### 3.2 Estructura Básica del Dockerfile

```dockerfile
FROM python:3.11-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    [DEPENDENCIAS_NECESARIAS] \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar e instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY . .

# Variables de entorno
ENV PORT=8080
EXPOSE 8080

# Comando para ejecutar la aplicación
CMD ["python", "app.py"]
```

### 3.3 Dependencias Comunes del Sistema

#### Para aplicaciones Flask básicas:
```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*
```

#### Para aplicaciones que usan wkhtmltopdf (PDFs):
```dockerfile
# Instalar dependencias del sistema necesarias para wkhtmltopdf
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    xvfb \
    libxrender1 \
    libxext6 \
    libfontconfig1 \
    fontconfig \
    libjpeg62-turbo \
    libx11-6 \
    ca-certificates \
    fonts-dejavu-core \
    xfonts-75dpi \
    xfonts-base \
    libssl3 \
    && rm -rf /var/lib/apt/lists/*

# Instalar wkhtmltopdf (requiere libssl1.1 desde Debian Bullseye)
RUN echo "deb http://deb.debian.org/debian bullseye main" > /etc/apt/sources.list.d/bullseye.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends -t bullseye libssl1.1 && \
    wget -q https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-3/wkhtmltox_0.12.6.1-3.bullseye_amd64.deb -O /tmp/wkhtmltopdf.deb && \
    dpkg -i /tmp/wkhtmltopdf.deb && \
    rm /tmp/wkhtmltopdf.deb && \
    rm /etc/apt/sources.list.d/bullseye.list && \
    rm -rf /var/lib/apt/lists/* && \
    wkhtmltopdf --version
```

#### Para aplicaciones que usan MySQL:
```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*
```

### 3.4 Ejemplo Completo de Dockerfile

```dockerfile
FROM python:3.11-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    xvfb \
    libxrender1 \
    libxext6 \
    libfontconfig1 \
    fontconfig \
    libjpeg62-turbo \
    libx11-6 \
    ca-certificates \
    fonts-dejavu-core \
    xfonts-75dpi \
    xfonts-base \
    libssl3 \
    && rm -rf /var/lib/apt/lists/*

# Instalar wkhtmltopdf
RUN echo "deb http://deb.debian.org/debian bullseye main" > /etc/apt/sources.list.d/bullseye.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends -t bullseye libssl1.1 && \
    wget -q https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-3/wkhtmltox_0.12.6.1-3.bullseye_amd64.deb -O /tmp/wkhtmltopdf.deb && \
    dpkg -i /tmp/wkhtmltopdf.deb && \
    rm /tmp/wkhtmltopdf.deb && \
    rm /etc/apt/sources.list.d/bullseye.list && \
    rm -rf /var/lib/apt/lists/* && \
    wkhtmltopdf --version

WORKDIR /app

# Instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Variables de entorno
ENV PORT=8080
EXPOSE 8080

# Ejecutar aplicación
CMD ["python", "app.py"]
```

### 3.5 Subir Dockerfile a GitHub

```bash
git add Dockerfile
git commit -m "Agregar Dockerfile para Cloud Run"
git push
```

---

## 4. CONFIGURACIÓN DE CLOUD RUN

### 4.1 Acceder a Google Cloud Console

1. Ve a: https://console.cloud.google.com
2. Selecciona tu proyecto (o créalo si no existe)
3. Asegúrate de tener facturación habilitada

### 4.2 Habilitar APIs Necesarias

1. Ve a: https://console.cloud.google.com/apis/library
2. Busca y habilita:
   - **Cloud Run API**
   - **Cloud Build API**
   - **Container Registry API** (si es necesario)

### 4.3 Crear Servicio en Cloud Run

#### Paso 1: Ir a Cloud Run
- Ve a: https://console.cloud.google.com/run
- Haz clic en **"Crear servicio"** o **"Create Service"**

#### Paso 2: Configuración Básica

**Nombre del servicio:**
- Escribe un nombre (ej: `mi-aplicacion`)

**Región:**
- Selecciona una región cercana (ej: `us-central1`, `europe-west1`)

**Autenticación:**
- Selecciona: **"Permitir tráfico no autenticado"** o **"Allow unauthenticated invocations"**
  - Esto permite acceso público sin autenticación

Haz clic en **"Siguiente"** o **"Next"**

#### Paso 3: Implementación Continua (IMPORTANTE)

1. **Habilitar implementación continua:**
   - Activa el toggle o checkbox de **"Implementación continua"** o **"Continuous deployment"**

2. **Conectar repositorio:**
   - Si es la primera vez: **"Conectar repositorio"** o **"Connect repository"**
   - Selecciona **"GitHub (Cloud Build)"**
   - Autoriza la conexión si es necesario
   - Selecciona tu repositorio: `USERNAME/REPO`

3. **Configuración del repositorio:**
   - **Branch pattern:** `^main$` ⚠️ **MUY IMPORTANTE: Debe ser exactamente `^main$`**
     - No uses `main` sin los símbolos `^` y `$`
     - No uses un commit específico
   - **Dockerfile path:** `Dockerfile` (solo el nombre, sin ruta)
   - **Docker context:** `.` (un punto, significa raíz del proyecto)

Haz clic en **"Siguiente"** o **"Next"**

#### Paso 4: Configuración del Contenedor

**Puerto:**
- Puerto del contenedor: `8080` (o el que uses en tu app)

**Variables de entorno:**
Haz clic en **"Agregar variable"** o **"Add variable"** y agrega todas las variables que necesites:

Ejemplo:
- `MYSQL_HOST` = `tu-host`
- `MYSQL_PORT` = `3306`
- `MYSQL_USER` = `tu-usuario`
- `MYSQL_PASSWORD` = `tu-password`
- `MYSQL_DB` = `tu-database`

**Recursos:**
- CPU: Deja el valor por defecto (1 CPU)
- Memoria: Deja el valor por defecto (512 MiB) o aumenta si es necesario

Haz clic en **"Siguiente"** o **"Next"**

#### Paso 5: Escalamiento

**Número mínimo de instancias:**
- `0` (para ahorrar costos cuando no hay tráfico)

**Número máximo de instancias:**
- `10` (o el valor que prefieras)

**Tiempo de espera de solicitudes:**
- `300` segundos (5 minutos)

**Concurrencia:**
- `80` (valor por defecto, está bien)

Haz clic en **"Siguiente"** o **"Next"**

#### Paso 6: Seguridad y Redes

- Deja los valores por defecto
- Haz clic en **"Siguiente"** o **"Next"**

#### Paso 7: Revisar y Crear

1. **Revisa toda la configuración:**
   - Nombre del servicio
   - Región
   - **Branch pattern:** `^main$` ⚠️ **VERIFICA ESTO**
   - Dockerfile: `Dockerfile`
   - Puerto: `8080`
   - Variables de entorno: Todas las que agregaste

2. **Si todo está correcto:**
   - Haz clic en **"Crear"** o **"Create"**

#### Paso 8: Esperar el Despliegue

- ⏱️ **Espera 3-5 minutos** mientras Cloud Run:
  - Crea el activador de Cloud Build
  - Clona el repositorio
  - Construye la imagen Docker
  - Despliega el servicio

### 4.4 Verificar el Despliegue

1. **Ver el progreso:**
   - En la página de detalles del servicio
   - Observa la sección **"Configurando implementación continua"**
   - Deberías ver:
     - ✔ "Creando activador de Cloud Build" - Completado
     - ⏳ "Compilando e implementando a partir del repositorio" - En progreso

2. **Verificar que funciona:**
   - Espera a que el estado cambie a **"Completado"** o **"Completed"**
   - Verás la **URL** del servicio: `https://tu-servicio-XXXXX.region.run.app`
   - Haz clic en la URL para probar que funciona

---

## 5. SOLUCIÓN DE PROBLEMAS COMUNES

### 5.1 Error: "No se encontró ninguna rama que coincida con el patrón"

**Problema:** Cloud Run está buscando una rama que no existe o el patrón está mal configurado.

**Solución:**
1. Ve a Cloud Build Triggers: https://console.cloud.google.com/cloud-build/triggers
2. Busca el trigger de tu servicio
3. Edita el trigger
4. Verifica que **"Branch"** sea exactamente `^main$`
5. Guarda los cambios

**Verificación:**
```bash
# Verificar ramas en GitHub
git branch -a

# Asegurarse de que existe la rama main
git branch -M main
git push -u origin main
```

### 5.2 Error: "Dockerfile no encontrado"

**Problema:** El Dockerfile no está en la raíz o el path está mal configurado.

**Solución:**
1. Verifica que el Dockerfile esté en la raíz del proyecto
2. En Cloud Run, verifica que **"Dockerfile path"** sea exactamente `Dockerfile` (sin ruta)
3. Verifica en GitHub que el Dockerfile esté presente

**Verificación:**
```bash
# Verificar que Dockerfile existe
ls -la Dockerfile

# Verificar en GitHub
# Ve a: https://github.com/USERNAME/REPO/blob/main/Dockerfile
```

### 5.3 Error: "Build failed" - Dependencias faltantes

**Problema:** Faltan dependencias del sistema en el Dockerfile.

**Solución:**
1. Revisa los logs del build en Cloud Build
2. Identifica qué dependencia falta
3. Agrega la dependencia al Dockerfile
4. Haz commit y push

**Ejemplo para wkhtmltopdf:**
```dockerfile
# Si falta libssl1.1, instálalo desde Debian Bullseye
RUN echo "deb http://deb.debian.org/debian bullseye main" > /etc/apt/sources.list.d/bullseye.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends -t bullseye libssl1.1 && \
    # ... resto de instalación
```

### 5.4 Error: "Module not found" en Python

**Problema:** Falta una dependencia en `requirements.txt`.

**Solución:**
1. Agrega la dependencia a `requirements.txt`
2. Haz commit y push
3. Cloud Run reconstruirá automáticamente

**Verificación:**
```bash
# Verificar requirements.txt
cat requirements.txt

# Instalar localmente para probar
pip install -r requirements.txt
```

### 5.5 Error: "Can't connect to MySQL"

**Problema:** La base de datos no es accesible desde Cloud Run o las variables de entorno están mal.

**Solución:**
1. Verifica que las variables de entorno estén configuradas en Cloud Run
2. Verifica que la IP de la base de datos permita conexiones desde Cloud Run
3. Verifica que el firewall permita conexiones desde Cloud Run

**Verificación:**
- Ve a Cloud Run → Tu servicio → Pestaña "Contenedores"
- Verifica que las variables de entorno estén presentes

### 5.6 Error: "Port already in use" o "Port 8080 not found"

**Problema:** La aplicación no está escuchando en el puerto correcto.

**Solución:**
1. Verifica que `app.py` use `host="0.0.0.0"` y `port=8080`
2. Verifica que el Dockerfile tenga `EXPOSE 8080`
3. Verifica que en Cloud Run el puerto esté configurado como `8080`

**Código correcto en app.py:**
```python
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
```

### 5.7 El servicio usa un commit antiguo

**Problema:** Cloud Run está usando un commit antiguo en lugar del más reciente.

**Solución:**
1. Verifica que el trigger esté configurado para usar la rama `main` (no un commit específico)
2. Haz un commit vacío para forzar el trigger:
   ```bash
   git commit --allow-empty -m "Force Cloud Run rebuild"
   git push
   ```

### 5.8 Ver Logs del Build

**Para ver qué está fallando:**

1. Ve a Cloud Build: https://console.cloud.google.com/cloud-build/builds
2. Busca el build más reciente
3. Haz clic en el build para ver los detalles
4. Revisa la sección "Logs" o "Registros"
5. El error generalmente está al final de los logs

---

## 6. CHECKLIST FINAL

### Antes de Crear el Servicio

- [ ] Proyecto tiene estructura correcta
- [ ] `requirements.txt` tiene todas las dependencias
- [ ] `app.py` tiene el código correcto al final (`host="0.0.0.0"`, `port=8080`)
- [ ] `Dockerfile` está en la raíz del proyecto
- [ ] `.gitignore` está configurado
- [ ] Código está en GitHub en la rama `main`
- [ ] Dockerfile está en GitHub

### Al Crear el Servicio

- [ ] Nombre del servicio configurado
- [ ] Región seleccionada
- [ ] Autenticación: "Permitir tráfico no autenticado"
- [ ] **Branch pattern:** `^main$` (con ^ y $)
- [ ] **Dockerfile path:** `Dockerfile` (sin ruta)
- [ ] **Puerto:** `8080`
- [ ] Variables de entorno agregadas (todas las necesarias)

### Después del Despliegue

- [ ] Build completado sin errores
- [ ] Servicio desplegado correctamente
- [ ] URL funciona y muestra la aplicación
- [ ] Variables de entorno están configuradas
- [ ] La aplicación se conecta a la base de datos (si aplica)

---

## 7. COMANDOS ÚTILES

### Git

```bash
# Ver estado
git status

# Ver commits recientes
git log --oneline -5

# Agregar cambios
git add .

# Hacer commit
git commit -m "Descripción del cambio"

# Subir cambios
git push

# Forzar rebuild en Cloud Run
git commit --allow-empty -m "Force Cloud Run rebuild"
git push
```

### Verificar Dockerfile Localmente (Opcional)

```bash
# Construir imagen localmente
docker build -t mi-aplicacion .

# Ejecutar contenedor localmente
docker run -p 8080:8080 -e PORT=8080 mi-aplicacion

# Probar en navegador
# http://localhost:8080
```

---

## 8. ACTUALIZACIONES FUTURAS

### Hacer Cambios y Actualizar

1. **Hacer cambios en tu código local**
2. **Probar localmente** (si es posible)
3. **Hacer commit y push:**
   ```bash
   git add .
   git commit -m "Descripción de los cambios"
   git push
   ```
4. **Cloud Run detectará automáticamente** el cambio (30-60 segundos)
5. **Se construirá una nueva imagen** automáticamente
6. **Se desplegará la nueva versión** automáticamente

### Verificar Actualización

1. Ve a Cloud Run → Tu servicio
2. Pestaña **"Revisiones"** (Revisions)
3. Deberías ver una nueva revisión en construcción
4. Espera a que se complete
5. Prueba la URL para verificar los cambios

---

## 9. RECURSOS Y ENLACES ÚTILES

### Google Cloud

- **Cloud Run Console:** https://console.cloud.google.com/run
- **Cloud Build:** https://console.cloud.google.com/cloud-build/builds
- **Cloud Build Triggers:** https://console.cloud.google.com/cloud-build/triggers
- **Documentación Cloud Run:** https://cloud.google.com/run/docs

### GitHub

- **Tu repositorio:** https://github.com/USERNAME/REPO
- **Ver Dockerfile:** https://github.com/USERNAME/REPO/blob/main/Dockerfile

### Docker

- **Documentación Dockerfile:** https://docs.docker.com/engine/reference/builder/
- **Python Official Image:** https://hub.docker.com/_/python

---

## 10. RESUMEN RÁPIDO

### Pasos Esenciales

1. ✅ **Preparar proyecto** (app.py, requirements.txt, estructura)
2. ✅ **Crear Dockerfile** en la raíz
3. ✅ **Subir a GitHub** (rama `main`)
4. ✅ **Crear servicio en Cloud Run** con:
   - Branch pattern: `^main$`
   - Dockerfile: `Dockerfile`
   - Puerto: `8080`
   - Variables de entorno
5. ✅ **Esperar despliegue** (3-5 minutos)
6. ✅ **Verificar que funciona**

### Puntos Críticos

- ⚠️ **Branch pattern:** Debe ser `^main$` (no `main`, no un commit)
- ⚠️ **Dockerfile path:** Debe ser `Dockerfile` (sin ruta)
- ⚠️ **Puerto:** Debe ser `8080` (o el que uses)
- ⚠️ **app.py:** Debe usar `host="0.0.0.0"` y `port=8080`
- ⚠️ **Variables de entorno:** Agregar todas las necesarias

---

## 🎉 ¡LISTO!

Con este manual deberías poder hacer deployment de cualquier aplicación Flask en Cloud Run. Si tienes problemas, revisa la sección de "Solución de Problemas Comunes" o los logs del build en Cloud Build.

**¡Éxito con tus deployments!** 🚀
