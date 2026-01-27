# 🚀 GUÍA PASO A PASO: Crear Servicio Cloud Run desde Cero

## 📋 PASO 1: Eliminar el Servicio Actual

### 1.1 Ir a Cloud Run
1. Abre tu navegador
2. Ve a: https://console.cloud.google.com/run?project=gestion-la-hornilla
3. Asegúrate de que el proyecto "Gestion-La-Hornilla" esté seleccionado

### 1.2 Seleccionar el Servicio
1. En la lista de servicios, busca **"aplicaciones-doc"**
2. Haz clic en el nombre del servicio para abrirlo

### 1.3 Eliminar el Servicio
1. En la parte superior de la página, busca el menú de tres puntos (⋮) o el botón **"Eliminar"** o **"Delete"**
2. Haz clic en **"Eliminar servicio"** o **"Delete Service"**
3. Confirma la eliminación escribiendo el nombre del servicio: `aplicaciones-doc`
4. Haz clic en **"Eliminar"** o **"Delete"**

⏱️ **Espera 1-2 minutos** para que se complete la eliminación

---

## 📋 PASO 2: Crear Nuevo Servicio

### 2.1 Iniciar Creación
1. En la página de Cloud Run, haz clic en el botón **"Crear servicio"** o **"Create Service"** (arriba a la izquierda)

### 2.2 Configuración Básica

#### Pestaña "Configurar el servicio" o "Configure the service"

**Nombre del servicio:**
- Escribe: `aplicaciones-doc`

**Región:**
- Selecciona: `europe-west1` (o la región que prefieras)

**Autenticación:**
- Selecciona: **"Permitir tráfico no autenticado"** o **"Allow unauthenticated invocations"**
  - Esto permite que cualquiera pueda acceder a la URL sin autenticación

Haz clic en **"Siguiente"** o **"Next"**

---

### 2.3 Implementación Continua (IMPORTANTE)

#### En la sección "Implementación continua" o "Continuous deployment":

1. **Habilitar implementación continua:**
   - Activa el toggle o checkbox de **"Implementación continua"** o **"Continuous deployment"**

2. **Conectar repositorio:**
   - Si es la primera vez, haz clic en **"Conectar repositorio"** o **"Connect repository"**
   - Selecciona **"GitHub (Cloud Build)"**
   - Autoriza la conexión si es necesario
   - Selecciona el repositorio: `FrancSCL/APLICACIONES-DOC`

3. **Configuración del repositorio:**
   - **Branch pattern:** `^main$` ⚠️ **MUY IMPORTANTE: Debe ser exactamente `^main$`**
   - **Dockerfile path:** `Dockerfile` (debe estar en la raíz)
   - **Docker context:** `.` (punto, significa raíz del proyecto)

4. **Configuración de compilación:**
   - Deja los valores por defecto (Cloud Build los manejará automáticamente)

Haz clic en **"Siguiente"** o **"Next"**

---

### 2.4 Configuración del Contenedor

#### En la sección "Contenedor" o "Container":

**Puerto:**
- Puerto del contenedor: `8080`

**Variables de entorno:**
Haz clic en **"Agregar variable"** o **"Add variable"** y agrega estas variables una por una:

1. **MYSQL_HOST**
   - Valor: `200.73.20.99`

2. **MYSQL_PORT**
   - Valor: `35026`

3. **MYSQL_USER**
   - Valor: `lahornilla_fsoto`

4. **MYSQL_PASSWORD**
   - Valor: `Paine2024!+`

5. **MYSQL_DB**
   - Valor: `lahornilla_LH_Operaciones`

**Recursos:**
- CPU: Deja el valor por defecto (1 CPU)
- Memoria: Deja el valor por defecto (512 MiB) o aumenta a 1 GiB si es necesario

Haz clic en **"Siguiente"** o **"Next"**

---

### 2.5 Escalamiento

#### En la sección "Escalamiento" o "Scaling":

**Número mínimo de instancias:**
- `0` (para ahorrar costos cuando no hay tráfico)

**Número máximo de instancias:**
- `10` (o el valor que prefieras)

**Tiempo de espera de solicitudes:**
- `300` segundos (5 minutos)

**Concurrencia:**
- `80` (valor por defecto, está bien)

Haz clic en **"Siguiente"** o **"Next"**

---

### 2.6 Seguridad

#### En la sección "Seguridad" o "Security":

- Deja los valores por defecto
- No necesitas cambiar nada aquí

Haz clic en **"Siguiente"** o **"Next"**

---

### 2.7 Redes

#### En la sección "Redes" o "Networking":

- Deja los valores por defecto
- No necesitas cambiar nada aquí

Haz clic en **"Siguiente"** o **"Next"**

---

### 2.8 Revisar y Crear

#### En la sección "Revisar" o "Review":

1. **Revisa toda la configuración:**
   - Nombre: `aplicaciones-doc`
   - Región: `europe-west1`
   - Branch pattern: `^main$` ⚠️ **VERIFICA ESTO**
   - Dockerfile: `Dockerfile`
   - Puerto: `8080`
   - Variables de entorno: Las 5 que agregaste

2. **Si todo está correcto:**
   - Haz clic en **"Crear"** o **"Create"**

⏱️ **Espera 3-5 minutos** mientras Cloud Run:
- Crea el activador de Cloud Build
- Clona el repositorio
- Construye la imagen Docker
- Despliega el servicio

---

## 📋 PASO 3: Verificar el Despliegue

### 3.1 Ver el Progreso
1. Después de hacer clic en "Crear", verás la página de detalles del servicio
2. Observa la sección **"Configurando implementación continua"**
3. Deberías ver:
   - ✔ "Creando activador de Cloud Build" - Completado
   - ⏳ "Compilando e implementando a partir del repositorio" - En progreso

### 3.2 Verificar que Funciona
1. Espera a que el estado cambie a **"Completado"** o **"Completed"**
2. Verás la **URL** del servicio: `https://aplicaciones-doc-XXXXX.europe-west1.run.app`
3. Haz clic en la URL para probar que funciona

### 3.3 Probar la Aplicación
1. Abre la URL en tu navegador
2. Deberías ver la página principal con las opciones:
   - Cuadernos de Campo
   - Papeleta de Aplicación

---

## ✅ Checklist Final

- [ ] Servicio anterior eliminado
- [ ] Nuevo servicio creado con nombre `aplicaciones-doc`
- [ ] Branch pattern configurado como `^main$`
- [ ] Dockerfile path configurado como `Dockerfile`
- [ ] Puerto configurado como `8080`
- [ ] 5 variables de entorno agregadas (MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB)
- [ ] Servicio desplegado correctamente
- [ ] URL funciona y muestra la aplicación

---

## 🆘 Si Algo Sale Mal

### Error: "No se encontró ninguna rama"
- **Solución:** Verifica que el Branch pattern sea exactamente `^main$`
- Verifica que la rama `main` existe en GitHub: https://github.com/FrancSCL/APLICACIONES-DOC/tree/main

### Error: "Dockerfile no encontrado"
- **Solución:** Verifica que el Dockerfile path sea exactamente `Dockerfile` (sin ruta, solo el nombre)
- Verifica que el Dockerfile existe en GitHub: https://github.com/FrancSCL/APLICACIONES-DOC/blob/main/Dockerfile

### Error: "Build falló"
- **Solución:** 
  1. Ve a Cloud Build → Historial
  2. Revisa los logs del build para ver el error específico
  3. Verifica que `requirements.txt` esté correcto
  4. Verifica que `app.py` tenga el código correcto al final

### El servicio no responde
- **Solución:**
  1. Verifica que las variables de entorno estén correctas
  2. Revisa los logs del servicio en Cloud Run → Pestaña "Registros"
  3. Verifica que la base de datos sea accesible desde Cloud Run

---

## 📞 URLs Útiles

- **Cloud Run Console:** https://console.cloud.google.com/run?project=gestion-la-hornilla
- **Cloud Build Triggers:** https://console.cloud.google.com/cloud-build/triggers?project=gestion-la-hornilla
- **Repositorio GitHub:** https://github.com/FrancSCL/APLICACIONES-DOC

---

## 🎉 ¡Listo!

Una vez completado, tu aplicación estará funcionando en Cloud Run y se actualizará automáticamente cada vez que hagas push a la rama `main` de GitHub.
