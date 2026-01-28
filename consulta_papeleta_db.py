"""
Script de SOLO LECTURA para diagnosticar qué datos devuelve la BD
para una papeleta. No modifica nada.
Uso: python consulta_papeleta_db.py [id_historico]
 Si no pasas id_historico, usa uno reciente de FACT_AREATECNICA_FITO_APLICACION_HISTORICO.
"""
import os
import sys
import mysql.connector
from mysql.connector import Error

# Misma config que app.py
MYSQL_HOST = os.getenv("MYSQL_HOST", "200.73.20.99")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "35026"))
MYSQL_USER = os.getenv("MYSQL_USER", "lahornilla_fsoto")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "Paine2024!+")
MYSQL_DB = os.getenv("MYSQL_DB", "lahornilla_LH_Operaciones")


def run():
    id_historico = None
    if len(sys.argv) > 1:
        id_historico = sys.argv[1].strip()

    try:
        conn = mysql.connector.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB,
            connection_timeout=10,
        )
    except Error as e:
        print("Error conectando a MySQL:", e)
        return

    with conn.cursor(dictionary=True) as cur:
        # Si no dieron id, tomar uno reciente
        if not id_historico:
            cur.execute("""
                SELECT id, id_aplicacion, fecha_planificacion, id_sucursal, id_especie
                FROM FACT_AREATECNICA_FITO_APLICACION_HISTORICO
                WHERE fecha_planificacion IS NOT NULL
                ORDER BY fecha_planificacion DESC
                LIMIT 1
            """)
            row = cur.fetchone()
            if not row:
                print("No hay registros en FACT_AREATECNICA_FITO_APLICACION_HISTORICO.")
                conn.close()
                return
            id_historico = row["id"]
            id_aplicacion_original = row["id_aplicacion"]
            print("Usando registro reciente:")
            print("  id (historico) =", id_historico)
            print("  id_aplicacion  =", id_aplicacion_original)
            print("  fecha_planif.  =", row["fecha_planificacion"])
            print("  id_sucursal    =", row["id_sucursal"])
            print("  id_especie     =", row["id_especie"])
        else:
            cur.execute("""
                SELECT id, id_aplicacion, fecha_planificacion, id_sucursal, id_especie
                FROM FACT_AREATECNICA_FITO_APLICACION_HISTORICO
                WHERE id = %s
            """, (id_historico,))
            row = cur.fetchone()
            if not row:
                print("No existe FACT_AREATECNICA_FITO_APLICACION_HISTORICO con id =", id_historico)
                conn.close()
                return
            id_aplicacion_original = row["id_aplicacion"]
            print("Registro elegido:")
            print("  id (historico) =", id_historico)
            print("  id_aplicacion  =", id_aplicacion_original)
            print("  fecha_planif.  =", row["fecha_planificacion"])
            print("  id_sucursal    =", row["id_sucursal"])
            print("  id_especie     =", row["id_especie"])

        print()
        print("--- 1) PRODUCTOS (FACT_AREATECNICA_FITO_PRODUCTOSAAPLICAR_HISTORICO) ---")
        print("    Filtro usado en app: id_aplicacion = id_aplicacion_original =", repr(id_aplicacion_original))

        # Igual que en app: por id_aplicacion (valor "original")
        cur.execute("""
            SELECT pp.id, pp.id_producto, pp.id_aplicacion, pp.dosis_100, pp.unidad, pp.observaciones
            FROM FACT_AREATECNICA_FITO_PRODUCTOSAAPLICAR_HISTORICO pp
            WHERE pp.id_aplicacion = %s
            ORDER BY pp.id
            LIMIT 20
        """, (id_aplicacion_original,))
        rows_prod = cur.fetchall()
        print("    Filas con id_aplicacion = id_aplicacion_original:", len(rows_prod))
        for i, r in enumerate(rows_prod[:5]):
            print("      [%d]" % i, r)
        if len(rows_prod) > 5:
            print("      ... y", len(rows_prod) - 5, "más")

        # Por si en histórico guardan el id del registro histórico de aplicacion
        cur.execute("""
            SELECT COUNT(*) AS n
            FROM FACT_AREATECNICA_FITO_PRODUCTOSAAPLICAR_HISTORICO
            WHERE id_aplicacion = %s
        """, (id_historico,))
        n_por_historico = cur.fetchone()["n"]
        print("    Filas con id_aplicacion = id_historico:", n_por_historico)

        print()
        print("--- 2) CUARTELES (FACT_AREATECNICA_FITO_CUARTELESAAPLICAR) ---")
        print("    Filtro usado en app: id_aplicacion = id_aplicacion_original =", repr(id_aplicacion_original))

        cur.execute("""
            SELECT c.id, c.id_aplicacion, c.id_cuartel, c.superficie, c.hora_inicio, c.hora_termino
            FROM FACT_AREATECNICA_FITO_CUARTELESAAPLICAR c
            WHERE c.id_aplicacion = %s
            ORDER BY c.id
            LIMIT 20
        """, (id_aplicacion_original,))
        rows_cuart = cur.fetchall()
        print("    Filas con id_aplicacion = id_aplicacion_original:", len(rows_cuart))
        for i, r in enumerate(rows_cuart[:5]):
            print("      [%d]" % i, r)
        if len(rows_cuart) > 5:
            print("      ... y", len(rows_cuart) - 5, "más")

        cur.execute("""
            SELECT COUNT(*) AS n
            FROM FACT_AREATECNICA_FITO_CUARTELESAAPLICAR
            WHERE id_aplicacion = %s
        """, (id_historico,))
        n_cuart_hist = cur.fetchone()["n"]
        print("    Filas con id_aplicacion = id_historico:", n_cuart_hist)

        print()
        print("--- 3) Consulta completa de PRODUCTOS (como en app, con JOINs) ---")
        cur.execute("""
            SELECT 
                MIN(p.codigo_softland) AS codigo_softland,
                MIN(p.nombre_comercial) AS nombre_comercial,
                MIN(pp.dosis_100) AS dosis_100_num,
                COALESCE(MIN(u.abreviatura), '') AS unidad_abrev
            FROM FACT_AREATECNICA_FITO_PRODUCTOSAAPLICAR_HISTORICO pp
            INNER JOIN DIM_AREATECNICA_FITO_PRODUCTO p ON pp.id_producto = p.id
            LEFT JOIN DIM_GENERAL_UNIDAD u ON pp.unidad = u.id
            WHERE pp.id_aplicacion = %s
            GROUP BY pp.id_producto
            ORDER BY MIN(pp.id)
            LIMIT 10
        """, (id_aplicacion_original,))
        rows_full = cur.fetchall()
        print("    Productos (agregados) con id_aplicacion = id_aplicacion_original:", len(rows_full))
        for i, r in enumerate(rows_full):
            print("      [%d]" % i, r)

    conn.close()
    print()
    print("Fin diagnóstico.")


if __name__ == "__main__":
    run()
