import os
import sys
from flask import Flask, render_template, request, jsonify

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Modelo.dao import SistemaFinancieroDAO

app = Flask(
    __name__,
    template_folder='../Vista/templates',
    static_folder='../Vista/static'
)

dao = SistemaFinancieroDAO()

@app.route('/')
def index():
    """ Renderiza la pantalla principal del Dashboard """
    return render_template('dashboard.html')


@app.route('/api/buscar_entidades', methods=['GET'])
def buscar_entidades():
    """
    Endpoint para el buscador con autocompletado.
    Uso: /api/buscar_entidades?q=JUNIN
    """
    criterio = request.args.get('q', '', type=str)
    if not criterio or len(criterio) < 2:
        return jsonify([])
    
    entidades = dao.buscar_entidades_por_nombre(criterio)
    return jsonify(entidades)


@app.route('/api/consultar_integrado', methods=['GET'])
def consultar_integrado():
    """
    Endpoint principal para obtener la radiografía financiera integrada.
    Uso: /api/consultar_integrado?sec_ejec=301086&ano_inicio=2021&ano_fin=2023
    """
    sec_ejec = request.args.get('sec_ejec', type=int)
    ano_inicio = request.args.get('ano_inicio', default=2021, type=int)
    ano_fin = request.args.get('ano_fin', default=2023, type=int)

    if not sec_ejec:
        return jsonify({"error": "Debe proporcionar un código de entidad válido (sec_ejec)"}), 400

    # Llama al DAO para obtener los datos de la Base de Datos
    data = dao.consultar_integrado_entidad(sec_ejec, ano_inicio, ano_fin)

    if not data.get("entidad"):
        return jsonify({"error": "No se encontró la entidad seleccionada."}), 404


    # LÓGICA DE NEGOCIO: Cálculo de Indicadores Financieros Globales

    total_transferencias = sum(t["monto_acreditado"] for t in data["transferencias"])
    total_ingresos = sum(i["monto_recaudado"] for i in data["ingresos"])
    
    total_gasto_pim = sum(g["pim"] for g in data["gasto_social"])
    total_gasto_devengado = sum(g["monto_devengado"] for g in data["gasto_social"])
    
    # % Ejecución del Gasto Social = (Devengado / PIM) * 100
    pct_ejecucion_gasto = (total_gasto_devengado / total_gasto_pim * 100) if total_gasto_pim > 0 else 0.0

    proyectos_activos = len(data["proyectos"])

    # Estructura del JSON que recibirá la Capa Vista
    respuesta = {
        "entidad": data["entidad"],
        "periodo": {"inicio": ano_inicio, "fin": ano_fin},
        "indicadores": {
            "total_transferencias_acreditadas": total_transferencias,
            "total_ingresos_recaudados": total_ingresos,
            "total_gasto_social_devengado": total_gasto_devengado,
            "porcentaje_ejecucion_gasto": round(pct_ejecucion_gasto, 2),
            "cantidad_proyectos": proyectos_activos
        },
        "detalle": {
            "transferencias": data["transferencias"],
            "ingresos": data["ingresos"],
            "gasto_social": data["gasto_social"],
            "proyectos": data["proyectos"]
        }
    }

    return jsonify(respuesta)



# EJECUCIÓN DEL SERVIDOR LOCAL

if __name__ == '__main__':
    app.run(debug=True, port=5000)