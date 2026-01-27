# 🔍 VERIFICAR VARIABLES DE ENTORNO EN CLOUD RUN

## ❌ Error Actual
"No se pudo conectar a la base de datos. Verifica las credenciales y la conectividad."

## ✅ SOLUCIÓN: Verificar Variables de Entorno

### Paso 1: Ir a Cloud Run

1. Ve a: https://console.cloud.google.com/run?project=gestion-la-hornilla
2. Haz clic en el servicio **"aplicaciones-doc"**

### Paso 2: Editar la Revisión

1. Haz clic en el botón **"Editar e implementar una nueva revisión"** (arriba a la derecha)
2. O ve a la pestaña **"Revisiones"** → Selecciona la revisión más reciente → **"Editar"**

### Paso 3: Agregar Variables de Entorno

1. En la sección **"Contenedores"** o **"Container"**
2. Busca **"Variables de entorno"** o **"Environment variables"**
3. Haz clic en **"Agregar variable"** o **"Add variable"**
4. Agrega estas 5 variables **UNA POR UNA**:

   **Variable 1:**
   - Nombre: `MYSQL_HOST`
   - Valor: `200.73.20.99`

   **Variable 2:**
   - Nombre: `MYSQL_PORT`
   - Valor: `35026`

   **Variable 3:**
   - Nombre: `MYSQL_USER`
   - Valor: `lahornilla_fsoto`

   **Variable 4:**
   - Nombre: `MYSQL_PASSWORD`
   - Valor: `Paine2024!+`

   **Variable 5:**
   - Nombre: `MYSQL_DB`
   - Valor: `lahornilla_LH_Operaciones`

### Paso 4: Guardar y Desplegar

1. Haz clic en **"Crear"** o **"Create"** (abajo)
2. Espera 1-2 minutos para que se despliegue
3. Prueba nuevamente la aplicación

---

## 🔍 ALTERNATIVA: Verificar Variables Existentes

Si las variables ya están configuradas, verifica que tengan los valores correctos:

1. Ve a Cloud Run → Tu servicio
2. Pestaña **"Revisiones"** → Revisión más reciente
3. Pestaña **"Contenedores"**
4. Busca la sección **"Variables de entorno"**
5. Verifica que todas las 5 variables estén presentes con los valores correctos

---

## 🆘 Si el Problema Persiste

### Problema: Firewall de Base de Datos

Si las variables están correctas pero sigue sin conectar, el problema es que **la base de datos no permite conexiones desde Cloud Run**.

**Solución:**
1. Contacta al administrador de la base de datos
2. Pide que abran el puerto `35026` para conexiones desde:
   - Google Cloud IPs (rango amplio)
   - O la IP específica de tu servicio Cloud Run
3. Verifica que el firewall permita conexiones desde Internet o desde Google Cloud

### Ver Logs para Más Detalles

1. Ve a Cloud Run → Tu servicio
2. Pestaña **"Registros"** (Logs)
3. Busca mensajes que digan:
   - "Error conectando a MySQL"
   - "Connection timeout"
   - "Access denied"
4. El mensaje específico te dirá exactamente qué está fallando

---

## 📝 NOTA IMPORTANTE

Las variables de entorno son **OBLIGATORIAS** para que la aplicación funcione en Cloud Run. Sin ellas, la aplicación no puede conectarse a la base de datos.
