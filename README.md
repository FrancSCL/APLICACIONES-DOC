## Aplicación Flask - Cuadernos de Campo y Papeleta de Aplicación

Aplicación web muy simple en Flask para:

- **Cuadernos de Campo**: selección de campo desde la vista `VISTA_CAMPOS`.
- **Papeleta de Aplicación**: selección de aplicación desde la vista `VISTA_APLICACIONES_PDF` y generación de PDF en base a HTML.

### Requisitos

- Python 3.9+
- MySQL accesible desde la app
- En Windows, es necesario instalar `wkhtmltopdf` para la generación de PDFs.

Instala las dependencias Python:

```bash
pip install -r requirements.txt
```

En Windows también debes instalar `wkhtmltopdf`:

1. Descarga el instalador desde `https://wkhtmltopdf.org/downloads.html` (versión Windows 64-bit con instalador).
2. Instálalo y asegúrate de marcar la opción para agregarlo al `PATH` o toma nota de la ruta de instalación, por ejemplo:\
   `C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe`.\
3. Si no está en el `PATH`, define la variable de entorno antes de ejecutar la app:

   ```powershell
   $env:WKHTMLTOPDF_PATH="C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
   ```

### Variables de entorno para MySQL

Configura (por ejemplo en `.env` o en el entorno de despliegue):

```bash
export MYSQL_HOST=localhost
export MYSQL_PORT=3306
export MYSQL_USER=tu_usuario
export MYSQL_PASSWORD=tu_password
export MYSQL_DB=tu_basedatos
```

En Windows PowerShell sería algo como:

```powershell
$env:MYSQL_HOST="localhost"
$env:MYSQL_PORT="3306"
$env:MYSQL_USER="tu_usuario"
$env:MYSQL_PASSWORD="tu_password"
$env:MYSQL_DB="tu_basedatos"
```

### Ejecutar en local

```bash
python app.py
```

Luego abre en el navegador:

- `http://localhost:8080/`

### Pegar el HTML real del PDF

1. Abre `templates/papeleta_pdf.html`.
2. Sustituye TODO el contenido dentro de `<body>...</body>` por tu HTML definitivo.
3. Reemplaza cada placeholder `<< [campo] >>` por la variable Jinja2 que corresponda, por ejemplo:
   - `<< [folio] >>` → `{{ datos.folio }}`
   - `<< [fecha_planificacion] >>` → `{{ datos.fecha_planificacion }}`
4. Si necesitas más campos, añádelos en la consulta SQL de `papeleta_pdf` en `app.py` y referencia esos nombres en el template (`{{ datos.tu_campo }}`).

