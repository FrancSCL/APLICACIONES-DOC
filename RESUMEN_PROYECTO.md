# RESUMEN DEL PROYECTO - LH-APLICACIONES-DOCS

## 📋 DESCRIPCIÓN GENERAL

Aplicación web Flask que genera documentos PDF para "La Hornilla Fruits". La aplicación permite:
1. **Cuadernos de Campo**: Selección y visualización de campos (fundos)
2. **Papeleta de Aplicación Fitosanitaria**: Generación de PDFs con información detallada de aplicaciones fitosanitarias

## 🛠️ TECNOLOGÍAS Y DEPENDENCIAS

### Backend
- **Python 3.9+**
- **Flask 3.0.3**: Framework web
- **mysql-connector-python 9.0.0**: Conexión a base de datos MySQL
- **pdfkit 1.0.0**: Generación de PDFs (wrapper para wkhtmltopdf)

### Herramientas Externas
- **wkhtmltopdf**: Binario necesario para convertir HTML a PDF (debe instalarse por separado)

## 📁 ESTRUCTURA DEL PROYECTO

```
LH-APLICACIONES-DOCS/
├── app.py                          # Aplicación principal Flask
├── requirements.txt                # Dependencias Python
├── README.md                       # Documentación básica
├── static/
│   ├── css/
│   │   └── styles.css              # Estilos CSS
│   └── images/
│       ├── logo_la_hornilla.png    # Logo de la empresa
│       ├── soleado.png             # Icono clima soleado
│       ├── parcialmente_nublado.png # Icono clima parcialmente nublado
│       ├── nublado.png             # Icono clima nublado
│       └── lluvia.png              # Icono clima lluvia
└── templates/
    ├── index.html                  # Página principal
    ├── cuadernos.html              # Vista de cuadernos de campo
    ├── papeleta.html               # Selector de papeleta
    └── papeleta_pdf.html           # Template HTML para PDF de papeleta
```

## 🗄️ BASE DE DATOS

### Configuración
- **Host**: 200.73.20.99 (configurable por variable de entorno)
- **Puerto**: 35026 (configurable por variable de entorno)
- **Usuario**: lahornilla_fsoto (configurable por variable de entorno)
- **Password**: Paine2024!+ (configurable por variable de entorno)
- **Base de datos**: lahornilla_LH_Operaciones (configurable por variable de entorno)

### Tablas/Vistas Principales Utilizadas

#### Tablas FACT (Hechos)
- `FACT_AREATECNICA_FITO_ APLICACION`: Datos principales de aplicaciones fitosanitarias
- `FACT_AREATECNICA_FITO_CUARTELESAAPLICAR`: Cuarteles asociados a cada aplicación
- `FACT_AREATECNICA_FITO_PRODUCTOSAAPLICAR`: Productos a aplicar en cada aplicación

#### Tablas DIM (Dimensiones)
- `DIM_GENERAL_SUCURSAL`: Información de sucursales/fundos
- `DIM_GENERAL_COLABORADOR`: Información de colaboradores
- `DIM_GENERAL_ESPECIE`: Especies de cultivos
- `DIM_AREATECNICA_FENOLOGIA_GRUPOESTADO`: Estados fenológicos
- `DIM_AREATECNICA_FITO_TIPOAPLICACION`: Tipos de aplicación
- `DIM_AREATECNICA_FITO_PRODUCTO`: Productos fitosanitarios
- `DIM_AREATECNICA_FITO_PROD_CARENCIA`: Carencias de productos por especie
- `DIM_GENERAL_UNIDAD`: Unidades de medida

#### Vistas
- `VISTA_APPSOP_MAQUINARIAACTIVA`: Vista de maquinaria activa
- `VISTA_AREATECNICA_CUADERNOCAMPO`: Vista para cuadernos de campo
- `GENERAL_CATASTRO_CUARTELES`: Catastro de cuarteles

## 🚀 FUNCIONALIDADES PRINCIPALES

### 1. Ruta Principal (`/`)
- Muestra página de inicio con opciones:
  - Cuadernos de Campo
  - Papeleta de Aplicación

### 2. Cuadernos de Campo (`/cuadernos`)
- Lista fundos únicos desde `VISTA_AREATECNICA_CUADERNOCAMPO`
- Permite seleccionar un campo y mostrar confirmación

### 3. Papeleta de Aplicación (`/papeleta`)
- **Paso 1**: Selecciona sucursal (solo productivas: IDs 2, 3, 4, 5, 6, 7, 8, 9, 27)
- **Paso 2**: Lista aplicaciones fitosanitarias de la sucursal seleccionada
- **Paso 3**: Genera PDF de la papeleta seleccionada

### 4. Generación de PDF (`/papeleta/pdf/<id_aplicacion>`)
Genera un PDF completo con:

#### Datos Generales
- Folio (formato: CYYYYNNNN o ID)
- Fecha de planificación (formato: M/D/YYYY)
- Temporada (formato: YY-YY)
- Fundo/Sucursal
- Especie
- Estado fenológico
- Modo de aplicación
- Mojamiento

#### Personal
- **Recomendado por** (Administrador):
  - Sucursales 4 y 8: "FELIPE LARRAIN"
  - Sucursales 3 y 5: "JUAN PABLO ALLENDES"
  - Otras: Busca colaborador con `id_cargo = 2` de esa sucursal
  
- **Encargado/a Aplicación** (Encargado de Riego):
  - Sucursales 4 y 8: "JUAN CARLOS ROMERO"
  - Otras: Busca colaborador con `id_cargo = 12` de esa sucursal
  
- **Dosificador/a**: Desde `id_dosificador` de la aplicación

#### Productos a Aplicar
- Lista de productos únicos (sin duplicados)
- Código Softland
- Nombre comercial
- Ingrediente activo
- Objetivo y actividad del producto
- Tiempo de reingreso
- Carencia (filtrada por especie)
- Dosis por 100L, por hectárea y por maquinaria

#### Detalle de Maquinadas
- Centro de costo (CODIGO del cuartel)
- Cuartel
- Variedad
- Hectáreas a aplicar
- Mezcla total por cuartel
- N° Maquinadas (calculado: Mezcla total / Capacidad maquinaria)
- Concho (residuo de maquinadas)
- Dosis teóricas por producto

#### Detalle de Maquinaria
- Operador (desde `id_aplicador` en cuarteles)
- Tractor (desde `id_tractor` en cuarteles)
- Maquinaria (desde `id_maquinaria` en cuarteles)
- Capacidad en litros

#### Características Técnicas del PDF
- **Orientación**: Horizontal (Landscape)
- **Tamaño**: A4
- **Imágenes**: Convertidas a base64 para embebidas en HTML
- **Logo**: "LA HORNILLA FRUITS" centrado en header
- **Iconos de clima**: Soleado, Parcialmente nublado, Nublado, Lluvia (horizontalmente alineados)

## 🔧 LÓGICA DE CÁLCULOS

### Capacidad de Maquinaria
1. Prioridad 1: Desde `FACT_AREATECNICA_FITO_CUARTELESAAPLICAR.id_maquinaria`
2. Prioridad 2: Desde `FACT_AREATECNICA_FITO_ APLICACION.seleccion_maquinarias` (primer ID)
3. Fallback: 1000 L

### N° Maquinadas
```
N° Maquinadas = (Mojamiento × Superficie) / Capacidad Maquinaria
```
- Se muestra con 2 decimales (ej: 7.00)

### Concho
```
Concho = (N° Maquinadas - Parte Entera) × Capacidad Maquinaria
```
- Se muestra como "0 L" si es 0 o muy cercano a 0

### Dosis por Hectárea
```
Dosis/ha = (Dosis_100 × Mojamiento) / 100
```
- Si >= 1000, se convierte a unidad estándar (ej: L → kL)

## ⚙️ CONFIGURACIÓN Y VARIABLES DE ENTORNO

### Variables de Entorno Opcionales
```bash
MYSQL_HOST=200.73.20.99          # Host de MySQL (default)
MYSQL_PORT=35026                  # Puerto de MySQL (default)
MYSQL_USER=lahornilla_fsoto       # Usuario MySQL (default)
MYSQL_PASSWORD=Paine2024!+        # Password MySQL (default)
MYSQL_DB=lahornilla_LH_Operaciones # Base de datos (default)
WKHTMLTOPDF_PATH=/ruta/a/wkhtmltopdf.exe  # Ruta a wkhtmltopdf (opcional)
PORT=8080                         # Puerto de la aplicación Flask (default)
```

## 📦 INSTALACIÓN Y EJECUCIÓN

### 1. Instalar Dependencias Python
```bash
pip install -r requirements.txt
```

### 2. Instalar wkhtmltopdf
**Windows:**
- Descargar desde: https://wkhtmltopdf.org/downloads.html
- Instalar y agregar al PATH, o definir variable `WKHTMLTOPDF_PATH`

**Linux:**
```bash
sudo apt-get install wkhtmltopdf
```

**macOS:**
```bash
brew install wkhtmltopdf
```

### 3. Configurar Variables de Entorno (Opcional)
```bash
# Windows PowerShell
$env:MYSQL_HOST="200.73.20.99"
$env:MYSQL_PORT="35026"
# ... etc

# Linux/macOS
export MYSQL_HOST="200.73.20.99"
export MYSQL_PORT="35026"
# ... etc
```

### 4. Ejecutar Aplicación
```bash
python app.py
```

La aplicación estará disponible en: `http://localhost:8080/`

## 🌐 DEPLOYMENT

### Consideraciones para Deployment

1. **Base de Datos**: Asegurar que el servidor de deployment tenga acceso a MySQL en `200.73.20.99:35026`

2. **wkhtmltopdf**: Debe estar instalado en el servidor de deployment

3. **Variables de Entorno**: Configurar en el entorno de producción:
   - `MYSQL_HOST`
   - `MYSQL_PORT`
   - `MYSQL_USER`
   - `MYSQL_PASSWORD`
   - `MYSQL_DB`
   - `WKHTMLTOPDF_PATH` (si no está en PATH)
   - `PORT` (si es necesario)

4. **Archivos Estáticos**: Las imágenes en `static/images/` deben estar presentes

5. **Servidor WSGI**: Para producción, usar un servidor WSGI como:
   - Gunicorn (Linux/macOS)
   - Waitress (Windows)
   - uWSGI

### Ejemplo con Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8080 app:app
```

### Ejemplo con Waitress (Windows)
```bash
pip install waitress
waitress-serve --host=0.0.0.0 --port=8080 app:app
```

## 🔒 SEGURIDAD

- Las credenciales de base de datos están hardcodeadas como valores por defecto, pero pueden sobrescribirse con variables de entorno
- En producción, **SIEMPRE** usar variables de entorno para credenciales
- Considerar usar un archivo `.env` con `python-dotenv` para desarrollo local

## 📝 NOTAS IMPORTANTES

1. **Sucursales Productivas**: Solo se muestran las sucursales con IDs: 2, 3, 4, 5, 6, 7, 8, 9, 27
2. **Productos Duplicados**: Se previene duplicación usando `GROUP BY pp.id_producto`
3. **Carencia**: Se filtra por especie usando `car.id_especie = %s`
4. **Imágenes**: Se convierten a base64 para evitar problemas con rutas de archivo en PDFs
5. **Formato de Fecha**: M/D/YYYY (sin ceros iniciales)
6. **Formato de Temporada**: YY-YY (ej: 25-26)

## 🐛 DEBUGGING

- Los errores se imprimen en consola con `print()`
- En producción, considerar usar un sistema de logging apropiado
- Verificar conexión a base de datos si hay errores
- Verificar que wkhtmltopdf esté instalado y accesible

## 📞 SOPORTE

Para problemas o preguntas sobre el proyecto, revisar:
- `app.py`: Lógica principal de la aplicación
- `templates/papeleta_pdf.html`: Template del PDF
- Logs de la aplicación en consola
