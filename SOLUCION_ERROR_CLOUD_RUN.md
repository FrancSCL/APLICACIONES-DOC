# 🔧 SOLUCIÓN: Error de Rama en Cloud Run

## ❌ Problema
Cloud Run muestra el error:
> "No se encontró ninguna rama que coincida con el patrón configurado"

## ✅ Solución Paso a Paso

### Opción 1: Actualizar Configuración del Activador en Cloud Run (RECOMENDADO)

1. **Ve a Cloud Run Console:**
   - https://console.cloud.google.com/run

2. **Selecciona tu servicio:**
   - Haz clic en "aplicaciones-doc"

3. **Edita la configuración del repositorio:**
   - Haz clic en el botón **"Editar la configuración del repositorio"** (arriba a la derecha)

4. **Verifica/Actualiza el patrón de rama:**
   - Busca el campo **"Branch pattern"** o **"Patrón de rama"**
   - Debe estar configurado como: `^main$` o `main`
   - Si dice `^master$` o `master`, cámbialo a `^main$`

5. **Guarda los cambios:**
   - Haz clic en **"Guardar"** o **"Save"**

6. **Espera:**
   - Cloud Run detectará automáticamente la rama `main` y comenzará el build

---

### Opción 2: Eliminar rama master y dejar solo main

Si prefieres eliminar la rama `master` del repositorio:

```bash
# Eliminar rama master del remoto
git push origin --delete master
```

Luego verifica que solo existe `main`:
```bash
git ls-remote --heads origin
```

---

### Opción 3: Verificar Configuración del Activador en Cloud Build

1. **Ve a Cloud Build:**
   - https://console.cloud.google.com/cloud-build/triggers

2. **Busca el activador de "aplicaciones-doc"**

3. **Edita el activador:**
   - Haz clic en el activador
   - Verifica la configuración de **"Branch"** o **"Rama"**
   - Debe ser: `^main$` o `main`

4. **Guarda los cambios**

---

## 🔍 Verificación

Después de actualizar la configuración:

1. **Espera 30-60 segundos** para que Cloud Run detecte el cambio

2. **Verifica el estado:**
   - Vuelve a la página de detalles del servicio
   - El error debería desaparecer
   - Deberías ver "Compilando e implementando..." en progreso

3. **Revisa los logs:**
   - Ve a la pestaña **"Revisiones"** (Revisions)
   - Deberías ver una nueva revisión en construcción

---

## 📝 Notas Importantes

- El patrón `^main$` significa "exactamente la rama main"
- El patrón `main` también funciona pero es menos específico
- Si cambias el patrón, Cloud Run automáticamente buscará la nueva rama
- Puede tomar 1-2 minutos para que el build comience después del cambio

---

## 🆘 Si el Error Persiste

1. **Verifica que la rama `main` existe en GitHub:**
   - https://github.com/FrancSCL/APLICACIONES-DOC/tree/main

2. **Verifica que el Dockerfile está en la raíz:**
   - https://github.com/FrancSCL/APLICACIONES-DOC/blob/main/Dockerfile

3. **Verifica que app.py tiene el código correcto al final:**
   - https://github.com/FrancSCL/APLICACIONES-DOC/blob/main/app.py

4. **Intenta hacer un nuevo commit para forzar el trigger:**
   ```bash
   git commit --allow-empty -m "Trigger Cloud Run build"
   git push
   ```
