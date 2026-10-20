import mysql.connector
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

    def _get_connection(self):
        return mysql.connector.connect(**self.config)

    def buscar_entidades_por_nombre(self, criterio):
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

            # 1. Información de Entidad
            if len(stored_results) > 0:
                entidad_res = stored_results[0].fetchone()
                if entidad_res:
                    resultado["entidad"] = EntidadEjecutora(entidad_res['sec_ejec'], entidad_res['ejecutora_nombre']).to_dict()

            # 2. Transferencias
            if len(stored_results) > 1:
                for f in stored_results[1].fetchall():
                    obj = Transferencia(f['ano'], f['mes'], f['fuente_nombre'], f['rubro_nombre'], f['grupo_transferencia'], f['origen_operacion'], f['monto_autorizado'], f['monto_acreditado'])
                    resultado["transferencias"].append(obj.to_dict())

            # 3. Ingresos
            if len(stored_results) > 2:
                for f in stored_results[2].fetchall():
                    obj = Ingreso(f['ano'], f['mes'], f['fuente_nombre'], f['rubro_nombre'], f['pia'], f['pim'], f['monto_recaudado'])
                    resultado["ingresos"].append(obj.to_dict())

            # 4. Gasto Social
            if len(stored_results) > 3:
                for f in stored_results[3].fetchall():
                    obj = GastoSocial(f['ano'], f['mes'], f['fuente_nombre'], f['rubro_nombre'], f['pia'], f['pim'], f['monto_certificado'], f['monto_comprometido'], f['monto_devengado'], f['monto_girado'])
                    resultado["gasto_social"].append(obj.to_dict())

            # 5. Proyectos de Inversión
            if len(stored_results) > 4:
                for f in stored_results[4].fetchall():
                    obj = ProyectoInversion(f['ano'], f['fuente_nombre'], f['rubro_nombre'], f['producto_proyecto'], f['producto_proyecto_nombre'], f['pia'], f['pim'], f['monto_devengado_ano'], f['monto_ejecucion_total'])
                    resultado["proyectos"].append(obj.to_dict())

        finally:
            cursor.close()
            conn.close()

        return resultado