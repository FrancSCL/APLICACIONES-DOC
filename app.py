import os
from flask import Flask, render_template, request, redirect, url_for, send_file, abort, make_response
import mysql.connector
from mysql.connector import Error
import pdfkit


def create_app():
    """
    Factory de la aplicación Flask.
    Permite desplegar en distintos entornos (local, Cloud Run, cPanel).
    """
    app = Flask(__name__)

    # Config básica. Credenciales fijas para la base de datos.
    app.config["MYSQL_HOST"] = os.getenv("MYSQL_HOST", "200.73.20.99")
    app.config["MYSQL_PORT"] = int(os.getenv("MYSQL_PORT", "35026"))
    app.config["MYSQL_USER"] = os.getenv("MYSQL_USER", "lahornilla_fsoto")
    app.config["MYSQL_PASSWORD"] = os.getenv("MYSQL_PASSWORD", "Paine2024!+")
    app.config["MYSQL_DB"] = os.getenv("MYSQL_DB", "lahornilla_LH_Operaciones")

    # Registrar rutas
    register_routes(app)

    return app


def get_db_connection(app):
    """
    Crea y devuelve una nueva conexión a MySQL usando mysql-connector-python.
    Las consultas deben hacerse SIEMPRE a través de vistas.
    """
    try:
        conn = mysql.connector.connect(
            host=app.config["MYSQL_HOST"],
            port=app.config["MYSQL_PORT"],
            user=app.config["MYSQL_USER"],
            password=app.config["MYSQL_PASSWORD"],
            database=app.config["MYSQL_DB"],
            connection_timeout=10,  # Timeout de conexión en segundos
            autocommit=False,
        )
        return conn
    except Error as e:
        # En producción conviene registrar esto en logs en lugar de imprimir.
        print(f"Error conectando a MySQL: {e}")
        return None
    except Exception as e:
        print(f"Error inesperado conectando a MySQL: {e}")
        return None


def register_routes(app: Flask):

    @app.route("/")
    def index():
        """
        Página principal con dos opciones:
        - Cuadernos de Campo
        - Papeleta de Aplicación
        """
        return render_template("index.html")

    # ──────────────────────────────────────────────
    # 1) CUADERNOS DE CAMPO
    # ──────────────────────────────────────────────
    @app.route("/cuadernos", methods=["GET", "POST"])
    def cuadernos():
        """
        Muestra un selector de campos (fundos) desde la vista VISTA_AREATECNICA_CUADERNOCAMPO.
        Al seleccionar un campo simplemente confirma la selección.
        """
        conn = get_db_connection(app)
        if conn is None:
            abort(500, description="No se pudo conectar a la base de datos.")

        campos = []
        try:
            with conn.cursor(dictionary=True) as cur:
                # Obtener fundos únicos desde la vista de cuadernos de campo
                cur.execute(
                    """
                    SELECT DISTINCT 
                        id_sucursal AS id_campo,
                        COALESCE(suc, CONCAT('Fundo ', id_sucursal)) AS nombre_campo
                    FROM VISTA_AREATECNICA_CUADERNOCAMPO
                    WHERE id_sucursal IS NOT NULL
                    ORDER BY nombre_campo
                    """
                )
                campos = cur.fetchall()
        finally:
            conn.close()

        campo_seleccionado = None
        nombre_campo_seleccionado = None

        if request.method == "POST":
            campo_id = request.form.get("id_campo")
            if campo_id:
                # Buscar el nombre del campo seleccionado solo para mostrarlo.
                for c in campos:
                    if str(c["id_campo"]) == str(campo_id):
                        campo_seleccionado = c["id_campo"]
                        nombre_campo_seleccionado = c["nombre_campo"]
                        break

        return render_template(
            "cuadernos.html",
            campos=campos,
            campo_seleccionado=campo_seleccionado,
            nombre_campo_seleccionado=nombre_campo_seleccionado,
        )

    # ──────────────────────────────────────────────
    # 2) PAPELETA DE APLICACIÓN
    # ──────────────────────────────────────────────
    @app.route("/papeleta", methods=["GET", "POST"])
    def papeleta():
        """
        Flujo en dos pasos:
        1. Seleccionar sucursal.
        2. Según la sucursal, listar aplicaciones fitosanitarias y permitir elegir una para generar PDF.
        """
        sucursales = []
        aplicaciones = []
        sucursal_seleccionada = None
        aplicacion_seleccionada = None
        error_message = None

        try:
            conn = get_db_connection(app)
            if conn is None:
                error_message = "No se pudo conectar a la base de datos. Verifica las credenciales y la conectividad."
                return render_template(
                    "papeleta.html",
                    sucursales=[],
                    sucursal_seleccionada=None,
                    aplicaciones=[],
                    aplicacion_seleccionada=None,
                    error_message=error_message,
                )

            try:
                with conn.cursor(dictionary=True) as cur:
                    # Listar sucursales productivas disponibles (solo IDs: 2, 3, 4, 5, 6, 7, 8, 9, 27)
                    cur.execute(
                        """
                        SELECT id, sucursal
                        FROM DIM_GENERAL_SUCURSAL
                        WHERE id IN (2, 3, 4, 5, 6, 7, 8, 9, 27)
                        ORDER BY sucursal
                        """
                    )
                    sucursales = cur.fetchall()

                    if request.method == "POST":
                        sucursal_seleccionada = request.form.get("id_sucursal")

                        if sucursal_seleccionada:
                            # Listar aplicaciones filtradas por sucursal
                            cur.execute(
                                """
                                SELECT 
                                    id AS id_aplicacion,
                                    CASE 
                                        WHEN num_documento IS NOT NULL 
                                        THEN CONCAT('C', YEAR(fecha_planificacion), num_documento)
                                        ELSE id
                                    END AS folio,
                                    fecha_planificacion,
                                    num_documento
                                FROM `FACT_AREATECNICA_FITO_ APLICACION`
                                WHERE fecha_planificacion IS NOT NULL
                                  AND id_sucursal = %s
                                ORDER BY fecha_planificacion DESC
                                LIMIT 100
                                """,
                                (sucursal_seleccionada,),
                            )
                            aplicaciones = cur.fetchall()

                            aplicacion_id = request.form.get("id_aplicacion")
                            if aplicacion_id:
                                for a in aplicaciones:
                                    if str(a["id_aplicacion"]) == str(aplicacion_id):
                                        aplicacion_seleccionada = a
                                        break
            except Exception as e:
                print(f"Error en consulta SQL: {e}")
                error_message = f"Error al consultar la base de datos: {str(e)}"
            finally:
                if conn:
                    try:
                        conn.close()
                    except:
                        pass
        except Exception as e:
            print(f"Error general en /papeleta: {e}")
            error_message = f"Error inesperado: {str(e)}"

        return render_template(
            "papeleta.html",
            sucursales=sucursales,
            sucursal_seleccionada=sucursal_seleccionada,
            aplicaciones=aplicaciones,
            aplicacion_seleccionada=aplicacion_seleccionada,
            error_message=error_message,
        )

    # ──────────────────────────────────────────────
    # GENERACIÓN DE PDF
    # ──────────────────────────────────────────────
    @app.route("/papeleta/pdf/<id_aplicacion>")
    def papeleta_pdf(id_aplicacion):
        """
        Genera un PDF a partir del HTML de la papeleta usando WeasyPrint.
        Los datos se obtienen directamente desde FACT_AREATECNICA_FITO_APLICACION
        y sus tablas relacionadas (DIM y FACT).
        """
        conn = get_db_connection(app)
        if conn is None:
            abort(500, description="No se pudo conectar a la base de datos.")

        datos_papeleta = None
        productos = []
        cuarteles = []
        maquinaria = []

        try:
            with conn.cursor(dictionary=True) as cur:
                # 1) Obtener datos principales de la aplicación
                # Primero obtenemos los datos básicos sin JOINs complejos
                cur.execute(
                    """
                    SELECT 
                        id AS id_aplicacion,
                        CASE 
                            WHEN num_documento IS NOT NULL 
                            THEN CONCAT('C', YEAR(fecha_planificacion), num_documento)
                            ELSE id
                        END AS folio,
                        fecha_planificacion,
                        CONCAT(YEAR(fecha_planificacion) - 1, '-', YEAR(fecha_planificacion) % 100) AS temporada,
                        mojamiento,
                        CASE 
                            WHEN modo_aplicacion = 4 THEN 'NO APLICA'
                            ELSE CONCAT(mojamiento, ' Litros')
                        END AS mojamiento_texto,
                        id_sucursal,
                        id_especie,
                        id_estadofenologico,
                        id_tipoaplicacion,
                        modo_aplicacion,
                        id_autorizador,
                        id_dosificador,
                        seleccion_tractores,
                        seleccion_maquinarias,
                        aplicadores
                    FROM `FACT_AREATECNICA_FITO_ APLICACION`
                    WHERE id = %s
                    """,
                    (id_aplicacion,),
                )
                datos_base = cur.fetchone()

                if not datos_base:
                    abort(404, description="Aplicación no encontrada.")

                # Ahora obtenemos los datos relacionados desde las tablas DIM
                # (con manejo de errores si las tablas no existen)
                datos_papeleta = dict(datos_base)
                
                # Formatear fecha: de YYYY-MM-DD a M/D/YYYY
                if datos_papeleta.get('fecha_planificacion'):
                    fecha_obj = datos_papeleta['fecha_planificacion']
                    if isinstance(fecha_obj, str):
                        from datetime import datetime
                        fecha_obj = datetime.strptime(fecha_obj, '%Y-%m-%d')
                    # Formatear como M/D/YYYY (sin ceros iniciales)
                    mes = str(fecha_obj.month)
                    dia = str(fecha_obj.day)
                    año = str(fecha_obj.year)
                    datos_papeleta['fecha_planificacion_formatted'] = f"{mes}/{dia}/{año}"
                else:
                    datos_papeleta['fecha_planificacion_formatted'] = ''
                
                # Formatear temporada: de 2025-26 a 25-26
                if datos_papeleta.get('temporada'):
                    temp_parts = datos_papeleta['temporada'].split('-')
                    if len(temp_parts) == 2:
                        datos_papeleta['temporada_formatted'] = f"{temp_parts[0][-2:]}-{temp_parts[1]}"
                    else:
                        datos_papeleta['temporada_formatted'] = datos_papeleta['temporada']
                else:
                    datos_papeleta['temporada_formatted'] = ''
                
                # Obtener fundo/sucursal
                try:
                    cur.execute(
                        "SELECT sucursal FROM DIM_GENERAL_SUCURSAL WHERE id = %s",
                        (datos_base['id_sucursal'],)
                    )
                    result = cur.fetchone()
                    datos_papeleta['fundo'] = result['sucursal'] if result else f"Sucursal {datos_base['id_sucursal']}"
                except:
                    datos_papeleta['fundo'] = f"Sucursal {datos_base['id_sucursal']}"

                # Obtener especie
                try:
                    cur.execute(
                        "SELECT especie FROM DIM_GENERAL_ESPECIE WHERE id = %s",
                        (datos_base['id_especie'],)
                    )
                    result = cur.fetchone()
                    datos_papeleta['especie'] = result['especie'] if result else f"Especie {datos_base['id_especie']}"
                except:
                    datos_papeleta['especie'] = f"Especie {datos_base['id_especie']}"

                # Obtener estado fenológico
                try:
                    cur.execute(
                        "SELECT grupoestado FROM DIM_AREATECNICA_FENOLOGIA_GRUPOESTADO WHERE id = %s",
                        (datos_base['id_estadofenologico'],)
                    )
                    result = cur.fetchone()
                    datos_papeleta['estado_fenologico'] = result['grupoestado'].upper() if result and result['grupoestado'] else ''
                except:
                    datos_papeleta['estado_fenologico'] = ''

                # Obtener modo aplicación
                try:
                    cur.execute(
                        "SELECT tipo FROM DIM_AREATECNICA_FITO_TIPOAPLICACION WHERE id = %s",
                        (datos_base['id_tipoaplicacion'],)
                    )
                    result = cur.fetchone()
                    datos_papeleta['modo_aplicacion_nombre'] = result['tipo'].upper() if result and result['tipo'] else ''
                except:
                    datos_papeleta['modo_aplicacion_nombre'] = ''

                # Obtener recomendado por (administrador de la sucursal)
                # Casos especiales: Sucursal 4 y 8 -> Felipe Larrain, Sucursal 3 y 5 -> Juan Pablo Allendes
                id_sucursal = datos_base['id_sucursal']
                try:
                    # Casos especiales primero
                    if id_sucursal in [4, 8]:
                        datos_papeleta['recomendado_por'] = 'FELIPE LARRAIN'
                    elif id_sucursal in [3, 5]:
                        datos_papeleta['recomendado_por'] = 'JUAN PABLO ALLENDES'
                    else:
                        # Buscar administrador de la sucursal (cargo id=2)
                        cur.execute(
                            """
                            SELECT c.nombre, c.apellido 
                            FROM DIM_GENERAL_COLABORADOR c
                            WHERE c.id_sucursal = %s 
                              AND c.id_cargo = 2
                            LIMIT 1
                            """,
                            (id_sucursal,)
                        )
                        result = cur.fetchone()
                        if result:
                            nombre = result.get('nombre', '').strip()
                            apellido = result.get('apellido', '').strip()
                            datos_papeleta['recomendado_por'] = f"{nombre} {apellido}".upper() if nombre or apellido else ''
                        else:
                            # Fallback: usar el id_autorizador
                            if datos_base.get('id_autorizador'):
                                cur.execute(
                                    "SELECT nombre, apellido FROM DIM_GENERAL_COLABORADOR WHERE id = %s",
                                    (datos_base['id_autorizador'],)
                                )
                                result = cur.fetchone()
                                if result:
                                    nombre = result.get('nombre', '').strip()
                                    apellido = result.get('apellido', '').strip()
                                    datos_papeleta['recomendado_por'] = f"{nombre} {apellido}".upper() if nombre or apellido else ''
                                else:
                                    datos_papeleta['recomendado_por'] = ''
                            else:
                                datos_papeleta['recomendado_por'] = ''
                except Exception as e:
                    print(f"Error obteniendo recomendado por: {e}")
                    datos_papeleta['recomendado_por'] = ''

                # Obtener dosificador
                try:
                    cur.execute(
                        "SELECT nombre, apellido FROM DIM_GENERAL_COLABORADOR WHERE id = %s",
                        (datos_base['id_dosificador'],)
                    )
                    result = cur.fetchone()
                    if result:
                        # Formatear con espacios correctos
                        nombre = result.get('nombre', '').strip()
                        apellido = result.get('apellido', '').strip()
                        datos_papeleta['dosificador'] = f"{nombre} {apellido}".upper() if nombre or apellido else ''
                    else:
                        datos_papeleta['dosificador'] = ''
                except:
                    datos_papeleta['dosificador'] = ''

                # Obtener encargado aplicación
                # Excepción: Sucursales 4 y 8 tienen el mismo encargado (Juan Carlos Romero)
                # Para las demás sucursales, buscar colaborador con id_cargo=12 de esa sucursal
                try:
                    # Caso especial: Sucursales 4 y 8 tienen el mismo encargado
                    if id_sucursal in [4, 8]:
                        datos_papeleta['encargado_aplicacion'] = 'JUAN CARLOS ROMERO'
                    else:
                        # Buscar encargado de aplicación por cargo id=12 en la sucursal específica
                        cur.execute(
                            """
                            SELECT c.nombre, c.apellido 
                            FROM DIM_GENERAL_COLABORADOR c
                            WHERE c.id_sucursal = %s 
                              AND c.id_cargo = 12
                            LIMIT 1
                            """,
                            (id_sucursal,)
                        )
                        result = cur.fetchone()
                        if result:
                            nombre = result.get('nombre', '').strip()
                            apellido = result.get('apellido', '').strip()
                            datos_papeleta['encargado_aplicacion'] = f"{nombre} {apellido}".upper() if nombre or apellido else ''
                        else:
                            # Fallback: intentar obtener desde FACT_AREATECNICA_FITO_CUARTELESAAPLICAR
                            cur.execute(
                                """
                                SELECT DISTINCT c.id, c.nombre, c.apellido
                                FROM FACT_AREATECNICA_FITO_CUARTELESAAPLICAR ca
                                INNER JOIN DIM_GENERAL_COLABORADOR c ON ca.id_aplicador = c.id
                                WHERE ca.id_aplicacion = %s
                                LIMIT 1
                                """,
                                (id_aplicacion,)
                            )
                            result = cur.fetchone()
                            if result:
                                nombre = result.get('nombre', '').strip()
                                apellido = result.get('apellido', '').strip()
                                datos_papeleta['encargado_aplicacion'] = f"{nombre} {apellido}".upper() if nombre or apellido else ''
                            else:
                                # Fallback final: usar el autorizador
                                if datos_base.get('id_autorizador'):
                                    cur.execute(
                                        "SELECT nombre, apellido FROM DIM_GENERAL_COLABORADOR WHERE id = %s",
                                        (datos_base['id_autorizador'],)
                                    )
                                    result = cur.fetchone()
                                    if result:
                                        nombre = result.get('nombre', '').strip()
                                        apellido = result.get('apellido', '').strip()
                                        datos_papeleta['encargado_aplicacion'] = f"{nombre} {apellido}".upper() if nombre or apellido else ''
                                    else:
                                        datos_papeleta['encargado_aplicacion'] = ''
                                else:
                                    datos_papeleta['encargado_aplicacion'] = ''
                except Exception as e:
                    print(f"Error obteniendo encargado aplicación: {e}")
                    datos_papeleta['encargado_aplicacion'] = ''

                # 2) Obtener productos a aplicar
                # Intentar obtener desde FACT_AREATECNICA_FITO_PRODUCTOSAAPLICAR y sus DIM asociadas.
                try:
                    cur.execute(
                        """
                        SELECT 
                            MIN(p.codigo_softland) AS codigo_softland,
                            MIN(p.nombre_comercial) AS nombre_comercial,
                            COALESCE(GROUP_CONCAT(DISTINCT ia.ia ORDER BY ia.ia SEPARATOR ', '), '') AS ingrediente_activo,
                            COALESCE(MIN(obj.objetivo_producto), '') AS objetivo_producto,
                            COALESCE(MIN(act.actividad_producto), '') AS actividad_producto,
                            CONCAT(MIN(p.reingreso), ' hr(s)') AS tiempo_reingreso,
                            CASE 
                                WHEN MAX(car.carencia) IS NULL THEN ''
                                ELSE CONCAT(MAX(car.carencia), ' día(s)')
                            END AS carencia,
                            CONCAT(MIN(pp.dosis_100), ' ', COALESCE(MIN(u.abreviatura), '')) AS dosis_100,
                            MIN(pp.dosis_100) AS dosis_100_num,
                            MIN(pp.observaciones) AS observaciones,
                            COALESCE(MIN(u.abreviatura), '') AS unidad_abrev,
                            COALESCE(MIN(u.unidad_estandar), '') AS unidad_estandar
                        FROM FACT_AREATECNICA_FITO_PRODUCTOSAAPLICAR pp
                        INNER JOIN DIM_AREATECNICA_FITO_PRODUCTO p ON pp.id_producto = p.id
                        LEFT JOIN DIM_AREATECNICA_FITO_PROD_IA pia ON p.id = pia.id_prod
                        LEFT JOIN DIM_AREATECNICA_FITO_PRODUCTOIA ia ON pia.id_ia = ia.id
                        LEFT JOIN DIM_AREATECNICA_FITO_PRODUCTOOBJETIVO obj ON pp.id_objetivo = obj.id
                        LEFT JOIN DIM_AREATECNICA_FITO_PRODUCTOACTIVIDAD act ON pp.id_actividad = act.id
                        LEFT JOIN DIM_AREATECNICA_FITO_PROD_CARENCIA car ON car.id_producto = pp.id_producto 
                            AND car.id_especie = %s
                        LEFT JOIN DIM_GENERAL_UNIDAD u ON pp.unidad = u.id
                        WHERE pp.id_aplicacion = %s
                        GROUP BY pp.id_producto
                        ORDER BY MIN(pp.id)
                        """,
                        (datos_base['id_especie'], id_aplicacion),
                    )
                    productos_raw = cur.fetchall()
                    
                    # Calcular dosis_ha y dosis_maq para cada producto
                    mojamiento = datos_papeleta.get('mojamiento', 0)
                    for prod in productos_raw:
                        dosis_100_num = prod.get('dosis_100_num', 0) or 0
                        unidad_abrev = prod.get('unidad_abrev', '')
                        unidad_estandar = prod.get('unidad_estandar', '')
                        
                        # Dosis por hectárea
                        dosis_ha_val = dosis_100_num * mojamiento / 100
                        if dosis_ha_val >= 1000:
                            prod['dosis_ha'] = f"{dosis_ha_val / 1000} {unidad_estandar}"
                        else:
                            prod['dosis_ha'] = f"{dosis_ha_val} {unidad_abrev}"
                        
                        # Dosis por maquinaria (necesitaríamos capacidad_maq, por ahora igual que ha)
                        prod['dosis_maq'] = prod['dosis_ha']
                    
                    productos = productos_raw
                    
                    # Obtener nombres de productos para la cabecera (máximo 6)
                    nombres_productos = [p['nombre_comercial'] for p in productos[:6]]
                    for i in range(6):
                        datos_papeleta[f'prod{i+1}_nombre'] = nombres_productos[i] if i < len(nombres_productos) else ''
                        
                except Exception as e:
                    print(f"Error obteniendo productos: {e}")
                    productos = []
                    for i in range(6):
                        datos_papeleta[f'prod{i+1}_nombre'] = ''

                # 3) Obtener capacidad de maquinaria primero (necesaria para cálculos)
                #    Prioridad:
                #    1) Desde FACT_AREATECNICA_FITO_CUARTELESAAPLICAR.id_maquinaria
                #    2) Desde FACT_AREATECNICA_FITO_ APLICACION.seleccion_maquinarias
                #    3) Valor por defecto 1000 L (solo si no hay datos)
                capacidad_maq = None
                try:
                    # 1) Intentar obtener desde FACT_AREATECNICA_FITO_CUARTELESAAPLICAR
                    cur.execute(
                        """
                        SELECT DISTINCT c.id_maquinaria
                        FROM FACT_AREATECNICA_FITO_CUARTELESAAPLICAR c
                        WHERE c.id_aplicacion = %s AND c.id_maquinaria IS NOT NULL
                        LIMIT 1
                        """,
                        (id_aplicacion,),
                    )
                    maq_result = cur.fetchone()
                    if maq_result and maq_result.get('id_maquinaria'):
                        cur.execute(
                            "SELECT capacidad_maquinaria FROM VISTA_APPSOP_MAQUINARIAACTIVA WHERE id = %s",
                            (maq_result['id_maquinaria'],)
                        )
                        cap_result = cur.fetchone()
                        if cap_result and cap_result.get('capacidad_maquinaria'):
                            capacidad_maq = cap_result['capacidad_maquinaria']

                    # 2) Si aún no tenemos capacidad, intentar desde seleccion_maquinarias de la tabla principal
                    if not capacidad_maq:
                        seleccion_maqs = datos_base.get('seleccion_maquinarias') or ''
                        maq_ids = [m.strip() for m in seleccion_maqs.split(',') if m.strip()]
                        if maq_ids:
                            cur.execute(
                                "SELECT capacidad_maquinaria FROM VISTA_APPSOP_MAQUINARIAACTIVA WHERE id = %s",
                                (maq_ids[0],)
                            )
                            cap_result = cur.fetchone()
                            if cap_result and cap_result.get('capacidad_maquinaria'):
                                capacidad_maq = cap_result['capacidad_maquinaria']

                except Exception as e:
                    print(f"Error obteniendo capacidad maquinaria: {e}")

                # 3) Si no se encontró nada, usar 1000 L como emergencia
                if not capacidad_maq:
                    capacidad_maq = 1000
                
                # 3) Obtener cuarteles/maquinadas
                # Intentar obtener desde FACT_AREATECNICA_FITO_CUARTELESAAPLICAR
                try:
                    mojamiento = datos_papeleta.get('mojamiento', 0)
                    
                    cur.execute(
                        """
                        SELECT 
                            COALESCE(c.superficie, cu.sup_productiva, cu.sup_oficial, 0) AS superficie,
                            c.hora_inicio,
                            c.hora_termino,
                            NULL AS fecha_viable_cosecha,
                            cu.CODIGO AS centro_costo,
                            cu.CUARTEL AS cuartel,
                            cu.variedad
                        FROM FACT_AREATECNICA_FITO_CUARTELESAAPLICAR c
                        LEFT JOIN GENERAL_CATASTRO_CUARTELES cu ON c.id_cuartel = cu.CODIGO
                        WHERE c.id_aplicacion = %s
                        ORDER BY cu.CUARTEL
                        """,
                        (id_aplicacion,),
                    )
                    cuarteles_raw = cur.fetchall()

                    # Calcular valores para cada cuartel
                    for cuartel in cuarteles_raw:
                        superficie = cuartel.get('superficie', 0) or 0
                        mezcla_total = mojamiento * superficie
                        num_maquinadas = mezcla_total / capacidad_maq if capacidad_maq > 0 else 0
                        concho_litros = (num_maquinadas - int(num_maquinadas)) * capacidad_maq
                        
                        # Formatear número de maquinadas: siempre mostrar 2 decimales
                        num_maq_display = f"{round(num_maquinadas, 2):.2f}"
                        
                        # Concho: mostrar "0 L" si es 0 o muy cercano a 0, sino mostrar el valor
                        if abs(concho_litros) < 0.01:
                            concho_display = "0 L"
                        else:
                            concho_display = f"{round(concho_litros)} L"
                        
                        # Formatear superficie con máximo 1 decimal
                        superficie_rounded = round(superficie, 1)
                        if superficie_rounded == int(superficie_rounded):
                            hectareas_aplicar_str = f"{int(superficie_rounded)} ha(s)"
                        else:
                            hectareas_aplicar_str = f"{superficie_rounded} ha(s)"
                        
                        cuartel_dict = {
                            'centro_costo': cuartel.get('centro_costo', ''),
                            'cuartel': cuartel.get('cuartel', ''),
                            'variedad': cuartel.get('variedad', ''),
                            'hectareas_aplicar': hectareas_aplicar_str,
                            'hectareas_aplicadas': '',
                            'fecha_viable_cosecha': cuartel.get('fecha_viable_cosecha', ''),
                            'hora_inicio': cuartel.get('hora_inicio', ''),
                            'hora_termino': cuartel.get('hora_termino', ''),
                            'mezcla_cuartel': f"{round(mezcla_total)} L",
                            'num_maquinadas': num_maq_display,
                            'concho': concho_display,
                            'superficie': superficie
                        }
                        
                        # Calcular productos teóricos por cuartel (simplificado)
                        for i, prod in enumerate(productos[:6], 1):
                            dosis_100_num = prod.get('dosis_100_num', 0) or 0
                            
                            dosis_teorico = superficie * dosis_100_num * mojamiento / 100
                            unidad = prod.get('unidad_abrev', '')
                            if dosis_teorico >= 1000:
                                unidad = prod.get('unidad_estandar', '')
                                dosis_teorico = dosis_teorico / 1000
                            
                            # Formatear sin decimales innecesarios
                            if dosis_teorico > 0:
                                if dosis_teorico == int(dosis_teorico):
                                    cuartel_dict[f'prod{i}_teorico'] = f"{int(dosis_teorico)} {unidad}"
                                else:
                                    cuartel_dict[f'prod{i}_teorico'] = f"{round(dosis_teorico, 2)} {unidad}"
                            else:
                                cuartel_dict[f'prod{i}_teorico'] = ''
                            cuartel_dict[f'prod{i}_real'] = ''
                        
                        cuarteles.append(cuartel_dict)
                    
                    # Calcular totales
                    total_superficie = sum(c.get('superficie', 0) for c in cuarteles)
                    total_mezcla = mojamiento * total_superficie
                    total_maquinadas = total_mezcla / capacidad_maq if capacidad_maq > 0 else 0
                    total_concho = (total_maquinadas - int(total_maquinadas)) * capacidad_maq
                    
                    # Formatear número de maquinadas totales: siempre mostrar 2 decimales
                    total_maq_display = f"{round(total_maquinadas, 2):.2f}"
                    
                    # Concho total: mostrar "0 L" si es 0 o muy cercano a 0, sino mostrar el valor
                    if abs(total_concho) < 0.01:
                        total_concho_display = "0 L"
                    else:
                        total_concho_display = f"{round(total_concho)} L"
                    
                    # Formatear total superficie con máximo 1 decimal
                    total_superficie_rounded = round(total_superficie, 1)
                    if total_superficie_rounded == int(total_superficie_rounded):
                        datos_papeleta['total_superficie'] = f"{int(total_superficie_rounded)} ha(s)"
                    else:
                        datos_papeleta['total_superficie'] = f"{total_superficie_rounded} ha(s)"
                    datos_papeleta['total_mezcla_cuartel'] = f"{round(total_mezcla)} L"
                    datos_papeleta['total_maquinadas'] = total_maq_display
                    datos_papeleta['total_concho'] = total_concho_display
                    
                    # Totales por producto
                    for i, prod in enumerate(productos[:6], 1):
                        dosis_100_num = prod.get('dosis_100_num', 0) or 0
                        
                        total_teorico = total_superficie * dosis_100_num * mojamiento / 100
                        unidad = prod.get('unidad_abrev', '')
                        if total_teorico >= 1000:
                            unidad = prod.get('unidad_estandar', '')
                            total_teorico = total_teorico / 1000
                        
                        # Formatear sin decimales innecesarios
                        if total_teorico > 0:
                            if total_teorico == int(total_teorico):
                                datos_papeleta[f'total_prod{i}_teorico'] = f"{int(total_teorico)} {unidad}"
                            else:
                                datos_papeleta[f'total_prod{i}_teorico'] = f"{round(total_teorico, 2)} {unidad}"
                        else:
                            datos_papeleta[f'total_prod{i}_teorico'] = ''
                        datos_papeleta[f'total_prod{i}_real'] = ''
                    
                except Exception as e:
                    print(f"Error obteniendo cuarteles: {e}")
                    cuarteles = []
                    datos_papeleta['total_superficie'] = '0 ha(s)'
                    datos_papeleta['total_mezcla_cuartel'] = '0 L'
                    datos_papeleta['total_maquinadas'] = 0
                    datos_papeleta['total_concho'] = ''
                    for i in range(6):
                        datos_papeleta[f'total_prod{i+1}_teorico'] = ''
                        datos_papeleta[f'total_prod{i+1}_real'] = ''

                # 4) Obtener maquinaria desde FACT_AREATECNICA_FITO_CUARTELESAAPLICAR
                # Los datos vienen directamente de los cuarteles aplicados
                try:
                    operador_nombre = ''
                    tractor_nombre = ''
                    maq_nombre = ''
                    capacidad_litros = ''
                    
                    # Primero intentar desde los cuarteles
                    cur.execute(
                        """
                        SELECT DISTINCT
                            c.id_aplicador,
                            c.id_tractor,
                            c.id_maquinaria
                        FROM FACT_AREATECNICA_FITO_CUARTELESAAPLICAR c
                        WHERE c.id_aplicacion = %s
                          AND (c.id_aplicador IS NOT NULL OR c.id_tractor IS NOT NULL OR c.id_maquinaria IS NOT NULL)
                        LIMIT 1
                        """,
                        (id_aplicacion,),
                    )
                    maq_data = cur.fetchone()
                    
                    if maq_data:
                        # Obtener operador desde cuarteles
                        if maq_data.get('id_aplicador'):
                            try:
                                cur.execute(
                                    "SELECT nombre, apellido FROM DIM_GENERAL_COLABORADOR WHERE id = %s",
                                    (maq_data['id_aplicador'],)
                                )
                                result = cur.fetchone()
                                if result:
                                    nombre = result.get('nombre', '').strip()
                                    apellido = result.get('apellido', '').strip()
                                    operador_nombre = f"{nombre} {apellido}".strip()
                            except Exception as e:
                                print(f"Error obteniendo operador desde cuarteles: {e}")
                        
                        # Obtener tractor (intentar desde vista común o tabla)
                        if maq_data.get('id_tractor'):
                            try:
                                # Intentar desde VISTA_APPSOP_MAQUINARIAACTIVA (puede tener tractores también)
                                cur.execute(
                                    "SELECT descripcion_ceco FROM VISTA_APPSOP_MAQUINARIAACTIVA WHERE id = %s",
                                    (maq_data['id_tractor'],)
                                )
                                result = cur.fetchone()
                                if result:
                                    tractor_nombre = result.get('descripcion_ceco', '')
                            except:
                                pass
                        
                        # Obtener maquinaria
                        if maq_data.get('id_maquinaria'):
                            try:
                                cur.execute(
                                    "SELECT descripcion_ceco, capacidad_maquinaria FROM VISTA_APPSOP_MAQUINARIAACTIVA WHERE id = %s",
                                    (maq_data['id_maquinaria'],)
                                )
                                result = cur.fetchone()
                                if result:
                                    maq_nombre = result.get('descripcion_ceco', '')
                                    capacidad_litros = result.get('capacidad_maquinaria', '')
                            except Exception as e:
                                print(f"Error obteniendo maquinaria: {e}")
                    
                    # Si no se encontró operador desde cuarteles, intentar desde la tabla principal (fallback)
                    if not operador_nombre:
                        aplicadores_str = datos_base.get('aplicadores', '')
                        if aplicadores_str:
                            operador_id = aplicadores_str.split(',')[0].strip() if aplicadores_str else None
                            if operador_id:
                                try:
                                    cur.execute(
                                        "SELECT nombre, apellido FROM DIM_GENERAL_COLABORADOR WHERE id = %s",
                                        (operador_id,)
                                    )
                                    result = cur.fetchone()
                                    if result:
                                        operador_nombre = f"{result['nombre']} {result['apellido']}"
                                except Exception as e:
                                    print(f"Error obteniendo operador desde tabla principal: {e}")
                    
                    # Si no se encontró tractor desde cuarteles, intentar desde la tabla principal (fallback)
                    if not tractor_nombre:
                        tractores_str = datos_base.get('seleccion_tractores', '')
                        if tractores_str:
                            tractor_id = tractores_str.split(',')[0].strip() if tractores_str else None
                            if tractor_id:
                                try:
                                    cur.execute(
                                        "SELECT descripcion_ceco FROM VISTA_APPSOP_MAQUINARIAACTIVA WHERE id = %s",
                                        (tractor_id,)
                                    )
                                    result = cur.fetchone()
                                    if result:
                                        tractor_nombre = result.get('descripcion_ceco', '')
                                except:
                                    pass
                    
                    # Si no se encontró maquinaria desde cuarteles, intentar desde la tabla principal (fallback)
                    if not maq_nombre:
                        maquinarias_str = datos_base.get('seleccion_maquinarias', '')
                        if maquinarias_str:
                            maq_id = maquinarias_str.split(',')[0].strip() if maquinarias_str else None
                            if maq_id:
                                try:
                                    cur.execute(
                                        "SELECT descripcion_ceco, capacidad_maquinaria FROM VISTA_APPSOP_MAQUINARIAACTIVA WHERE id = %s",
                                        (maq_id,)
                                    )
                                    result = cur.fetchone()
                                    if result:
                                        maq_nombre = result.get('descripcion_ceco', '')
                                        capacidad_litros = result.get('capacidad_maquinaria', '')
                                except Exception as e:
                                    print(f"Error obteniendo maquinaria desde tabla principal: {e}")
                    
                    maquinaria.append({
                        'operador': operador_nombre,
                        'tractor': tractor_nombre,
                        'maquinaria': maq_nombre,
                        'capacidad_litros': capacidad_litros if capacidad_litros else '',
                        'velocidad': '',
                        'marcha': '',
                        'rpm': '',
                        'presion_bar': '',
                        'boquillas': ''
                    })
                except Exception as e:
                    print(f"Error obteniendo maquinaria: {e}")
                    maquinaria.append({
                        'operador': '',
                        'tractor': '',
                        'maquinaria': '',
                        'capacidad_litros': '',
                        'velocidad': '',
                        'marcha': '',
                        'rpm': '',
                        'presion_bar': '',
                        'boquillas': ''
                    })
                
                # Generar texto de concho si aplica
                total_concho_val = datos_papeleta.get('total_concho', '')
                if total_concho_val and total_concho_val != '' and total_concho_val != '0 L':
                    try:
                        concho_litros = float(str(total_concho_val).replace(' L', '').strip())
                        capacidad_maq = 1000  # Valor por defecto
                        
                        concho_texto = "CONCHO: "
                        for i, prod in enumerate(productos[:6], 1):
                            if prod.get('nombre_comercial'):
                                # Calcular dosis para concho
                                dosis_100_num = prod.get('dosis_100_num', 0) or 0
                                dosis_concho = concho_litros * dosis_100_num / 100
                                unidad = prod.get('unidad_abrev', '')
                                
                                concho_texto += f"{prod['nombre_comercial']} "
                                if dosis_concho > 0:
                                    concho_texto += f"{round(dosis_concho, 2)} {unidad} / "
                                else:
                                    concho_texto += "/ "
                        datos_papeleta['concho_texto'] = concho_texto.rstrip(' / ')
                    except:
                        datos_papeleta['concho_texto'] = ''
                else:
                    datos_papeleta['concho_texto'] = ''

        except Exception as e:
            print(f"Error consultando datos: {e}")
            abort(500, description=f"Error al obtener datos: {str(e)}")
        finally:
            conn.close()

        if not datos_papeleta:
            abort(404, description="Aplicación no encontrada.")

        # Convertir imágenes a base64 para embebidas en el HTML (más confiable que rutas de archivo)
        import os
        import base64
        base_dir = os.path.dirname(os.path.abspath(__file__))
        static_images_dir = os.path.join(base_dir, 'static', 'images')
        
        def image_to_base64(image_filename):
            """Convierte una imagen a base64 para embebida en HTML"""
            image_path = os.path.join(static_images_dir, image_filename)
            if os.path.exists(image_path):
                try:
                    with open(image_path, 'rb') as img_file:
                        img_data = img_file.read()
                        img_base64 = base64.b64encode(img_data).decode('utf-8')
                        # Determinar el tipo MIME basado en la extensión
                        ext = os.path.splitext(image_filename)[1].lower()
                        mime_type = 'image/png' if ext == '.png' else 'image/jpeg'
                        return f"data:{mime_type};base64,{img_base64}"
                except Exception as e:
                    print(f"Error leyendo imagen {image_filename}: {e}")
                    return ''
            else:
                print(f"Imagen no encontrada: {image_path}")
                return ''
        
        weather_images = {
            'soleado': image_to_base64('soleado.png'),
            'parcialmente_nublado': image_to_base64('parcialmente_nublado.png'),
            'nublado': image_to_base64('nublado.png'),
            'lluvia': image_to_base64('lluvia.png'),
        }
        
        logo_path = image_to_base64('logo_la_hornilla.png')
        
        # Renderizar HTML con Jinja2.
        html_str = render_template(
            "papeleta_pdf.html",
            datos=datos_papeleta,
            productos=productos,
            cuarteles=cuarteles,
            maquinaria=maquinaria,
            weather_images=weather_images,
            logo_path=logo_path,
        )

        # Convertir HTML a PDF usando pdfkit + wkhtmltopdf.
        # pdfkit espera un binario wkhtmltopdf instalado en el sistema.
        try:
            # Opciones para wkhtmltopdf: ignorar errores de carga de recursos externos
            # (por ejemplo, imágenes remotas) y desactivar imágenes si dan problemas
            # de red en el entorno local.
            pdf_options = {
                "encoding": "UTF-8",
                "page-size": "A4",
                "orientation": "Landscape",  # Forzar orientación horizontal
                "load-error-handling": "ignore",  # ignora errores pero intenta cargar imágenes
                "enable-local-file-access": "",  # permite acceso a archivos locales
                "quiet": "",
            }

            # Puedes configurar la ruta explícita al ejecutable wkhtmltopdf mediante
            # la variable de entorno WKHTMLTOPDF_PATH si no está en el PATH.
            wkhtmltopdf_path = os.getenv("WKHTMLTOPDF_PATH")
            if wkhtmltopdf_path:
                config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)
                pdf_bytes = pdfkit.from_string(
                    html_str, False, configuration=config, options=pdf_options
                )
            else:
                pdf_bytes = pdfkit.from_string(html_str, False, options=pdf_options)
        except Exception as e:
            print(f"Error generando PDF con pdfkit/wkhtmltopdf: {e}")
            abort(500, description="Error al generar el PDF.")

        filename = f"papeleta_{datos_papeleta['folio']}.pdf"

        response = make_response(pdf_bytes)
        response.headers["Content-Type"] = "application/pdf"
        response.headers["Content-Disposition"] = f"attachment; filename={filename}"
        return response


app = create_app()


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

