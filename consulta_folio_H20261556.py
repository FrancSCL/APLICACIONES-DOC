"""
Solo lectura: revisa la papeleta H20261556 (o C20261556 / 1556) en FACT e histórico.
"""
import os
import mysql.connector
from mysql.connector import Error

MYSQL_HOST = os.getenv("MYSQL_HOST", "200.73.20.99")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "35026"))
MYSQL_USER = os.getenv("MYSQL_USER", "lahornilla_fsoto")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "Paine2024!+")
MYSQL_DB = os.getenv("MYSQL_DB", "lahornilla_LH_Operaciones")

BUSCAR = "H20261556"

try:
    conn = mysql.connector.connect(
        host=MYSQL_HOST, port=MYSQL_PORT, user=MYSQL_USER,
        password=MYSQL_PASSWORD, database=MYSQL_DB, connection_timeout=10,
    )
except Error as e:
    print("Error conectando:", e)
    exit(1)

cur = conn.cursor(dictionary=True)

# Buscar por H20261556, C20261556, C20251556, num_documento 1556
cur.execute("""
    SELECT id, id_aplicacion, fecha_planificacion, num_documento, id_sucursal, id_especie,
           CASE WHEN num_documento IS NOT NULL THEN CONCAT('C', YEAR(fecha_planificacion), num_documento) ELSE id_aplicacion END AS folio
    FROM FACT_AREATECNICA_FITO_APLICACION_HISTORICO
    WHERE id = %s OR id_aplicacion = %s
       OR (num_documento IS NOT NULL AND CONCAT('C', YEAR(fecha_planificacion), num_documento) IN (%s, %s))
       OR (num_documento = 1556 AND YEAR(fecha_planificacion) >= 2025)
    ORDER BY fecha_planificacion DESC
    LIMIT 10
""", (BUSCAR, BUSCAR, "C20261556", "C20251556"))
rows = cur.fetchall()

if not rows:
    cur.execute("""
        SELECT id, id_aplicacion, fecha_planificacion, num_documento, id_sucursal, id_especie,
               CASE WHEN num_documento IS NOT NULL THEN CONCAT('C', YEAR(fecha_planificacion), num_documento) ELSE id_aplicacion END AS folio
        FROM FACT_AREATECNICA_FITO_APLICACION_HISTORICO
        WHERE id LIKE %s OR id_aplicacion LIKE %s OR num_documento = 1556
        ORDER BY fecha_planificacion DESC
        LIMIT 10
    """, ("%" + "20261556" + "%", "%" + "1556" + "%"))
    rows = cur.fetchall()

if not rows:
    print("No se encontró papeleta con id/folio", BUSCAR, "ni C20261556/C20251556 ni num_documento 1556.")
    conn.close()
    exit(0)

print("Registro(s) en FACT_AREATECNICA_FITO_APLICACION_HISTORICO:")
for r in rows:
    print("  ", r)
row = rows[0]
id_historico = row["id"]
id_aplicacion_original = row["id_aplicacion"]
print()
print("Usando: id_historico =", repr(id_historico), ", id_aplicacion_original =", repr(id_aplicacion_original))
print()

# --- FACT (lo que usa la app ahora) ---
print("--- FACT (tablas en línea, como está la app hoy) ---")
cur.execute("SELECT COUNT(*) AS n FROM FACT_AREATECNICA_FITO_PRODUCTOSAAPLICAR WHERE id_aplicacion = %s", (id_aplicacion_original,))
np = cur.fetchone()["n"]
cur.execute("SELECT COUNT(*) AS n FROM FACT_AREATECNICA_FITO_CUARTELESAAPLICAR WHERE id_aplicacion = %s", (id_aplicacion_original,))
nc = cur.fetchone()["n"]
print("  Productos (FACT_AREATECNICA_FITO_PRODUCTOSAAPLICAR id_aplicacion=%s):" % repr(id_aplicacion_original), np)
print("  Cuarteles (FACT_AREATECNICA_FITO_CUARTELESAAPLICAR id_aplicacion=%s):" % repr(id_aplicacion_original), nc)

# --- Histórico (por si ahí sí hay datos) ---
print()
print("--- Histórico (para comparar) ---")
cur.execute("SELECT COUNT(*) AS n FROM FACT_AREATECNICA_FITO_PRODUCTOSAAPLICAR_HISTORICO WHERE id_aplicacion = %s", (id_aplicacion_original,))
np_h_orig = cur.fetchone()["n"]
cur.execute("SELECT COUNT(*) AS n FROM FACT_AREATECNICA_FITO_PRODUCTOSAAPLICAR_HISTORICO WHERE id_aplicacion = %s", (id_historico,))
np_h_id = cur.fetchone()["n"]
cur.execute("SELECT COUNT(*) AS n FROM FACT_AREATECNICA_FITO_CUARTELESAAPLICAR WHERE id_aplicacion = %s", (id_historico,))
nc_h = cur.fetchone()["n"]
print("  Productos _HISTORICO id_aplicacion=id_original:", np_h_orig)
print("  Productos _HISTORICO id_aplicacion=id_historico:", np_h_id)
print("  Cuarteles FACT id_aplicacion=id_historico:", nc_h)

print()
print("--- RESUMEN ---")
if np > 0 and nc > 0:
    print("  Con tablas FACT y id_aplicacion_original esta papeleta SÍ tendría productos y cuarteles.")
else:
    print("  Con tablas FACT y id_aplicacion_original esta papeleta NO tiene productos/cuarteles -> PDF en blanco.")
    if np_h_id > 0 or nc_h > 0:
        print("  Los datos existen en histórico / por id_historico; para llenar el PDF habría que usar id_historico en esas consultas o usar tablas _HISTORICO con id_historico.")

conn.close()
print()
print("Fin.")
