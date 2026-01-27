# 🔍 CÓMO REVISAR LOS LOGS DEL BUILD

## PASO 1: Ir a Historial de Compilaciones

1. En la página de detalles del servicio "aplicaciones-doc"
2. Haz clic en **"Historial de compilaciones"** (Build history) - tiene un ícono de gráfico de barras
3. O ve directamente a: https://console.cloud.google.com/cloud-build/builds?project=gestion-la-hornilla

## PASO 2: Encontrar el Build Fallido

1. Busca el build más reciente (debería estar arriba)
2. Debería tener un ícono rojo ❌ o decir "Failed"
3. Haz clic en el build para ver los detalles

## PASO 3: Ver los Logs

1. En la página de detalles del build, verás una sección de "Logs" o "Registros"
2. Busca el error específico (generalmente está al final de los logs)
3. Copia el mensaje de error completo

## PASO 4: Compartir el Error

Una vez que veas el error, compártelo conmigo y te ayudo a solucionarlo.

---

## Alternativa: Ver desde Cloud Run

1. En la página de detalles del servicio
2. Busca la sección "Compilando e implementando a partir del repositorio"
3. Haz clic en "ver registros" o "view logs"
4. Esto te llevará directamente a los logs del build
