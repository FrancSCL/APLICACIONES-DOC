# 🚀 GUÍA RÁPIDA DE DEPLOYMENT - LH-APLICACIONES-DOCS

## 📋 CHECKLIST PRE-DEPLOYMENT

- [ ] Python 3.9+ instalado
- [ ] Dependencias instaladas (`pip install -r requirements.txt`)
- [ ] wkhtmltopdf instalado y en PATH
- [ ] Acceso a base de datos MySQL (200.73.20.99:35026)
- [ ] Variables de entorno configuradas
- [ ] Archivos estáticos presentes (`static/images/`)

## 🔧 OPCIONES DE DEPLOYMENT

### Opción 1: Servidor VPS/Linux (Recomendado)

#### 1. Instalar Dependencias del Sistema
```bash
sudo apt-get update
sudo apt-get install python3-pip python3-venv wkhtmltopdf
```

#### 2. Clonar/Subir Proyecto
```bash
cd /var/www  # o tu directorio preferido
# Subir archivos del proyecto aquí
```

#### 3. Crear Entorno Virtual
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 4. Instalar Servidor WSGI (Gunicorn)
```bash
pip install gunicorn
```

#### 5. Configurar Variables de Entorno
Crear archivo `.env` o configurar en sistema:
```bash
export MYSQL_HOST="200.73.20.99"
export MYSQL_PORT="35026"
export MYSQL_USER="lahornilla_fsoto"
export MYSQL_PASSWORD="Paine2024!+"
export MYSQL_DB="lahornilla_LH_Operaciones"
export PORT="8080"
```

#### 6. Ejecutar con Gunicorn
```bash
gunicorn -w 4 -b 0.0.0.0:8080 app:app
```

#### 7. Configurar Nginx (Opcional pero Recomendado)
```nginx
server {
    listen 80;
    server_name tu-dominio.com;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static {
        alias /ruta/a/tu/proyecto/static;
    }
}
```

#### 8. Usar systemd para Auto-inicio (Opcional)
Crear `/etc/systemd/system/lh-aplicaciones.service`:
```ini
[Unit]
Description=LH Aplicaciones Flask App
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/lh-aplicaciones-docs
Environment="PATH=/var/www/lh-aplicaciones-docs/venv/bin"
ExecStart=/var/www/lh-aplicaciones-docs/venv/bin/gunicorn -w 4 -b 127.0.0.1:8080 app:app

[Install]
WantedBy=multi-user.target
```

Activar servicio:
```bash
sudo systemctl enable lh-aplicaciones
sudo systemctl start lh-aplicaciones
```

---

### Opción 2: cPanel/Shared Hosting

#### 1. Subir Archivos
- Subir todos los archivos vía FTP/cPanel File Manager
- Asegurar que `app.py` esté en el directorio raíz o en `public_html`

#### 2. Crear archivo `.htaccess` (si usa Apache)
```apache
RewriteEngine On
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^(.*)$ app.py/$1 [L]
```

#### 3. Configurar Python App en cPanel
- Ir a "Setup Python App"
- Crear nueva aplicación
- Seleccionar Python 3.9+
- Configurar variables de entorno:
  - `MYSQL_HOST=200.73.20.99`
  - `MYSQL_PORT=35026`
  - `MYSQL_USER=lahornilla_fsoto`
  - `MYSQL_PASSWORD=Paine2024!+`
  - `MYSQL_DB=lahornilla_LH_Operaciones`

#### 4. Instalar Dependencias
```bash
pip3.9 install -r requirements.txt
```

#### 5. Verificar wkhtmltopdf
- Contactar al proveedor de hosting para instalar wkhtmltopdf
- O usar variable `WKHTMLTOPDF_PATH` si está en otra ubicación

---

### Opción 3: Google Cloud Run / AWS / Azure

#### 1. Crear `Dockerfile`
```dockerfile
FROM python:3.9-slim

# Instalar wkhtmltopdf
RUN apt-get update && apt-get install -y \
    wkhtmltopdf \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8080
EXPOSE 8080

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
```

#### 2. Crear `.dockerignore`
```
__pycache__
*.pyc
venv/
.env
*.md
```

#### 3. Build y Push (Ejemplo Google Cloud Run)
```bash
# Build
gcloud builds submit --tag gcr.io/TU-PROYECTO/lh-aplicaciones

# Deploy
gcloud run deploy lh-aplicaciones \
  --image gcr.io/TU-PROYECTO/lh-aplicaciones \
  --platform managed \
  --region us-central1 \
  --set-env-vars MYSQL_HOST=200.73.20.99,MYSQL_PORT=35026,MYSQL_USER=lahornilla_fsoto,MYSQL_PASSWORD=Paine2024!+,MYSQL_DB=lahornilla_LH_Operaciones
```

---

### Opción 4: Windows Server (IIS)

#### 1. Instalar Python y Dependencias
```powershell
# Instalar Python
# Descargar desde python.org

# Instalar dependencias
pip install -r requirements.txt
pip install waitress
```

#### 2. Instalar wkhtmltopdf
- Descargar e instalar desde https://wkhtmltopdf.org/downloads.html
- Agregar al PATH o configurar `WKHTMLTOPDF_PATH`

#### 3. Crear archivo `web.config` para IIS
```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
  <system.webServer>
    <handlers>
      <add name="PythonHandler" path="*" verb="*" modules="httpPlatformHandler" resourceType="Unspecified"/>
    </handlers>
    <httpPlatform processPath="C:\Python39\python.exe"
                  arguments="C:\ruta\a\tu\proyecto\app.py"
                  stdoutLogEnabled="true"
                  stdoutLogFile="C:\logs\python.log"
                  startupTimeLimit="60"
                  requestTimeout="00:04:00">
      <environmentVariables>
        <environmentVariable name="MYSQL_HOST" value="200.73.20.99" />
        <environmentVariable name="MYSQL_PORT" value="35026" />
        <environmentVariable name="MYSQL_USER" value="lahornilla_fsoto" />
        <environmentVariable name="MYSQL_PASSWORD" value="Paine2024!+" />
        <environmentVariable name="MYSQL_DB" value="lahornilla_LH_Operaciones" />
        <environmentVariable name="PORT" value="8080" />
      </environmentVariables>
    </httpPlatform>
  </system.webServer>
</configuration>
```

#### 4. Usar Waitress (Alternativa)
```powershell
# Crear archivo start.ps1
$env:MYSQL_HOST="200.73.20.99"
$env:MYSQL_PORT="35026"
$env:MYSQL_USER="lahornilla_fsoto"
$env:MYSQL_PASSWORD="Paine2024!+"
$env:MYSQL_DB="lahornilla_LH_Operaciones"
waitress-serve --host=0.0.0.0 --port=8080 app:app
```

---

## ✅ VERIFICACIÓN POST-DEPLOYMENT

1. **Probar Conexión a Base de Datos**
   - Acceder a `/papeleta` y verificar que carga sucursales

2. **Probar Generación de PDF**
   - Seleccionar una aplicación y generar PDF
   - Verificar que se genera correctamente

3. **Verificar Imágenes**
   - Verificar que logo e iconos de clima aparecen en PDF

4. **Verificar Logs**
   - Revisar logs de errores si algo falla

## 🔍 TROUBLESHOOTING

### Error: "wkhtmltopdf not found"
- Verificar instalación: `wkhtmltopdf --version`
- Configurar `WKHTMLTOPDF_PATH` con ruta completa

### Error: "Can't connect to MySQL"
- Verificar firewall permite conexión a 200.73.20.99:35026
- Verificar credenciales
- Verificar que el servidor de deployment tenga acceso a la red de la base de datos

### Error: "Images not showing in PDF"
- Verificar que archivos en `static/images/` existen
- Verificar permisos de lectura

### Error: "Module not found"
- Ejecutar `pip install -r requirements.txt` nuevamente
- Verificar que estás en el entorno virtual correcto

## 📞 SOPORTE

Para más detalles, ver `RESUMEN_PROYECTO.md`
