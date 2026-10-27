import mysql.connector
import csv
import io
import re
from Modelo.entidades import (
    EntidadEjecutora, Transferencia, Ingreso, GastoSocial, ProyectoInversion
)

class SistemaFinancieroDAO:
    def __init__(self):
        self.config = {
            'host': 'localhost',
            'user': 'root',
            'password': 'Icommerce2026!',
            'database': 'sistema_financiero_mef',
            'port': 3306
        }

    def _get_connection(self, user=None, password=None):
        config = self.config.copy()
        if user and password:
            config['user'] = user
            config['password'] = password
        return mysql.connector.connect(**config)

    def validar_conexion_rol(self, usuario, password):
        try:
            conn = self._get_connection(user=usuario, password=password)
            conn.close()
            return True
        except mysql.connector.Error:
            return False

    def obtener_anios_disponibles(self):
        """Obtiene la lista de años disponibles en las tablas del sistema con fallback de seguridad."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            query = """
                SELECT DISTINCT ano FROM (
                    SELECT ano FROM transferencia
                    UNION
                    SELECT ano FROM ingreso
                    UNION
                    SELECT ano FROM gasto_social
                    UNION
                    SELECT ano FROM proyecto_inversion
                ) AS anios
                WHERE ano IS NOT NULL
                ORDER BY ano ASC;
            """
            cursor.execute(query)
            filas = cursor.fetchall()
            cursor.close()
            conn.close()

            anios = [f[0] for f in filas if f[0] is not None]
            return anios if len(anios) > 0 else [2021, 2022, 2023, 2024]
        except Exception as e:
            print(f"Error al obtener años: {e}")
            return [2021, 2022, 2023, 2024]

    def procesar_csv_transferencias(self, usuario, password, archivo_csv):
        """Procesa el CSV de transferencias insertando con el usuario autenticado (Rol Operador)."""
        user_db = usuario if (usuario and usuario.strip()) else 'us_operador_lima'
        pass_db = password if (password and password.strip()) else 'OperadorMef2026!'

        conn = None
        cursor = None
        try:
            conn = self._get_connection(user=user_db, password=pass_db)
            cursor = conn.cursor()

            cursor.execute("SET FOREIGN_KEY_CHECKS=0;")

            bytes_content = archivo_csv.stream.read()
            try:
                contenido = bytes_content.decode("utf-8-sig")
            except UnicodeDecodeError:
                contenido = bytes_content.decode("latin-1", errors="replace")

            stream = io.StringIO(contenido)
            primera_linea = contenido.split('\n')[0] if contenido else ''
            delimitador = ';' if ';' in primera_linea else ','

            lector = csv.DictReader(stream, delimiter=delimitador)

            query = """
                INSERT INTO transferencia 
                (sec_ejec, codigo_fuente, codigo_rubro, ano, mes, grupo_transferencia, origen_operacion, monto_autorizado, monto_acreditado)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            batch = []
            total_registros = 0

            for fila in lector:
                f = {str(k).strip().lower(): str(v).strip() for k, v in fila.items() if k}

                v_sec = int(f.get('sec_ejec', '301086'))
                v_fue = int(f.get('codigo_fuente', '5'))
                v_rub = int(f.get('codigo_rubro', '18'))
                v_ano = int(f.get('ano', '2024'))
                v_mes = int(f.get('mes', '1'))

                grupo_trans = f.get('grupo_transferencia', 'GL')
                origen_op = f.get('origen_operacion', 'CANON MINERO 2024')

                v_aut = float(f.get('monto_autorizado', '0.0'))
                v_acr = float(f.get('monto_acreditado', '0.0'))

                batch.append((
                    v_sec, v_fue, v_rub, v_ano, v_mes,
                    grupo_trans[:50],
                    origen_op[:100],
                    v_aut, v_acr
                ))
                total_registros += 1

            if batch:
                cursor.executemany(query, batch)

            conn.commit()
            cursor.execute("SET FOREIGN_KEY_CHECKS=1;")
            
            return {
                "exito": True, 
                "mensaje": f"¡Éxito! Se procesaron e insertaron correctamente {total_registros} registros del archivo '{archivo_csv.filename}' en MySQL con el rol '{user_db}' (Trigger de auditoría ejecutado)."
            }

        except mysql.connector.Error as err:
            if conn: conn.rollback()
            return {"exito": False, "mensaje": f"Error de MySQL / Permisos: {err.msg}"}
        except Exception as e:
            if conn: conn.rollback()
            return {"exito": False, "mensaje": f"Error al procesar el archivo: {str(e)}"}
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def obtener_log_trazabilidad(self):
        """Consulta los eventos de auditoría y trazabilidad registrados por los Triggers (Rol Auditor)."""
        conn = None
        cursor = None
        try:
            conn = self._get_connection(user='us_auditor_mef', password='AuditorMef2026!')
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT id_log, usuario_bd, host_origen, tabla_afectada, accion_realizada, fecha_hora 
                FROM log_trazabilidad_acceso 
                ORDER BY fecha_hora DESC 
                LIMIT 50;
            """)
            logs = cursor.fetchall()
            for row in logs:
                if row.get('fecha_hora'):
                    row['fecha_hora'] = row['fecha_hora'].strftime('%Y-%m-%d %H:%M:%S')
            return logs
        except Exception as e:
            print(f"Error al obtener logs: {e}")
            return []
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

    def obtener_transferencias_enmascaradas(self):
        """Consulta la vista enmascarada para el perfil público/ciudadano."""
        conn = self._get_connection(user='us_web_publico', password='Consulta2026!')
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM vw_transferencias_enmascaradas LIMIT 50;")
        resultado = cursor.fetchall()
        cursor.close()
        conn.close()
        return resultado

    def buscar_entidades_por_nombre(self, criterio):
        """Busca entidades ejecutoras utilizando el procedimiento almacenado sp_buscar_entidades."""
        conn = self._get_connection()
        cursor = conn.cursor(dictionary=True)
        entidades = []
        try:
            cursor.callproc('sp_buscar_entidades', [criterio])
            for result in cursor.stored_results():
                filas = result.fetchall()
                for fila in filas:
                    entidades.append(EntidadEjecutora(fila['sec_ejec'], fila['ejecutora_nombre']).to_dict())
        finally:
            cursor.close()
            conn.close()
        return entidades

    def consultar_integrado_entidad(self, sec_ejec, ano_inicio, ano_fin):
        """Consulta consolidada sobre los 4 datasets invocando el procedimiento almacenado."""
        conn = self._get_connection()
        cursor = conn.cursor(dictionary=True)
        
        resultado = {
            "entidad": None,
            "transferencias": [],
            "ingresos": [],
            "gasto_social": [],
            "proyectos": []
        }

        try:
            cursor.callproc('sp_consultar_integrado_entidad', [sec_ejec, ano_inicio, ano_fin])
            stored_results = list(cursor.stored_results())

            if len(stored_results) > 0:
                entidad_res = stored_results[0].fetchone()
                if entidad_res:
                    resultado["entidad"] = EntidadEjecutora(entidad_res['sec_ejec'], entidad_res['ejecutora_nombre']).to_dict()

            if len(stored_results) > 1:
                for f in stored_results[1].fetchall():
                    obj = Transferencia(
                        f['ano'], f['mes'], f['fuente_nombre'], f['rubro_nombre'],
                        f['grupo_transferencia'], f['origen_operacion'],
                        f['monto_autorizado'], f['monto_acreditado']
                    )
                    resultado["transferencias"].append(obj.to_dict())

            if len(stored_results) > 2:
                for f in stored_results[2].fetchall():
                    obj = Ingreso(
                        f['ano'], f['mes'], f['fuente_nombre'], f['rubro_nombre'],
                        f['pia'], f['pim'], f['monto_recaudado']
                    )
                    resultado["ingresos"].append(obj.to_dict())

            if len(stored_results) > 3:
                for f in stored_results[3].fetchall():
                    obj = GastoSocial(
                        f['ano'], f['mes'], f['fuente_nombre'], f['rubro_nombre'],
                        f['pia'], f['pim'], f['monto_certificado'], f['monto_comprometido'],
                        f['monto_devengado'], f['monto_girado']
                    )
                    resultado["gasto_social"].append(obj.to_dict())

            if len(stored_results) > 4:
                for f in stored_results[4].fetchall():
                    obj = ProyectoInversion(
                        f['ano'], f['fuente_nombre'], f['rubro_nombre'],
                        f['producto_proyecto'], f['producto_proyecto_nombre'],
                        f['pia'], f['pim'], f['monto_devengado_ano'], f['monto_ejecucion_total']
                    )
                    resultado["proyectos"].append(obj.to_dict())

        finally:
            cursor.close()
            conn.close()

        return resultado

    def consultar_integrado_con_udf(self, sec_ejec, ano_inicio, ano_fin):
        """Consulta la ejecución presupuestal invocando la UDF fn_CalcularPorcentajeEjecucionGlobal de la Sesión 7."""
        conn = self._get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            query = """
                SELECT 
                    e.sec_ejec,
                    e.ejecutora_nombre,
                    IFNULL(SUM(i.monto_recaudado), 0) AS total_ingresos,
                    IFNULL(SUM(g.monto_devengado), 0) AS total_gasto,
                    IFNULL(SUM(t.monto_acreditado), 0) AS total_transferencias,
                    fn_CalcularPorcentajeEjecucionGlobal(
                        SUM(i.monto_recaudado), 
                        SUM(t.monto_acreditado), 
                        SUM(g.monto_devengado)
                    ) AS porcentaje_ejecucion_udf
                FROM entidad_ejecutora e
                LEFT JOIN ingreso i ON e.sec_ejec = i.sec_ejec AND i.ano BETWEEN %s AND %s
                LEFT JOIN gasto_social g ON e.sec_ejec = g.sec_ejec AND g.ano BETWEEN %s AND %s
                LEFT JOIN transferencia t ON e.sec_ejec = t.sec_ejec AND t.ano BETWEEN %s AND %s
                WHERE e.sec_ejec = %s
                GROUP BY e.sec_ejec, e.ejecutora_nombre;
            """
            cursor.execute(query, (ano_inicio, ano_fin, ano_inicio, ano_fin, ano_inicio, ano_fin, sec_ejec))
            return cursor.fetchone()
        except Exception as e:
            print(f"Error al ejecutar consulta UDF: {e}")
            return None
        finally:
            cursor.close()
            conn.close()