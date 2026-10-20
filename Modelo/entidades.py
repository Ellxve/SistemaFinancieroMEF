# ENTIDADES DEL SISTEMA DE INFORMACIÓN FINANCIERA MEF

class EntidadEjecutora:
    def __init__(self, sec_ejec, ejecutora_nombre):
        self.sec_ejec = sec_ejec
        self.ejecutora_nombre = ejecutora_nombre

    def to_dict(self):
        return {
            "sec_ejec": self.sec_ejec,
            "ejecutora_nombre": self.ejecutora_nombre
        }


class FuenteFinanciamiento:
    def __init__(self, codigo_fuente, fuente_nombre):
        self.codigo_fuente = codigo_fuente
        self.fuente_nombre = fuente_nombre


class Rubro:
    def __init__(self, codigo_rubro, rubro_nombre):
        self.codigo_rubro = codigo_rubro
        self.rubro_nombre = rubro_nombre


class Transferencia:
    def __init__(self, ano, mes, fuente_nombre, rubro_nombre, grupo_transferencia, origen_operacion, monto_autorizado, monto_acreditado):
        self.ano = ano
        self.mes = mes
        self.fuente_nombre = fuente_nombre
        self.rubro_nombre = rubro_nombre
        self.grupo_transferencia = grupo_transferencia
        self.origen_operacion = origen_operacion
        self.monto_autorizado = float(monto_autorizado or 0)
        self.monto_acreditado = float(monto_acreditado or 0)

    def to_dict(self):
        return {
            "ano": self.ano,
            "mes": self.mes,
            "fuente_nombre": self.fuente_nombre,
            "rubro_nombre": self.rubro_nombre,
            "grupo_transferencia": self.grupo_transferencia,
            "origen_operacion": self.origen_operacion,
            "monto_autorizado": self.monto_autorizado,
            "monto_acreditado": self.monto_acreditado
        }


class Ingreso:
    def __init__(self, ano, mes, fuente_nombre, rubro_nombre, pia, pim, monto_recaudado):
        self.ano = ano
        self.mes = mes
        self.fuente_nombre = fuente_nombre
        self.rubro_nombre = rubro_nombre
        self.pia = float(pia or 0)
        self.pim = float(pim or 0)
        self.monto_recaudado = float(monto_recaudado or 0)

    def to_dict(self):
        return {
            "ano": self.ano,
            "mes": self.mes,
            "fuente_nombre": self.fuente_nombre,
            "rubro_nombre": self.rubro_nombre,
            "pia": self.pia,
            "pim": self.pim,
            "monto_recaudado": self.monto_recaudado
        }


class GastoSocial:
    def __init__(self, ano, mes, fuente_nombre, rubro_nombre, pia, pim, monto_certificado, monto_comprometido, monto_devengado, monto_girado):
        self.ano = ano
        self.mes = mes
        self.fuente_nombre = fuente_nombre
        self.rubro_nombre = rubro_nombre
        self.pia = float(pia or 0)
        self.pim = float(pim or 0)
        self.monto_certificado = float(monto_certificado or 0)
        self.monto_comprometido = float(monto_comprometido or 0)
        self.monto_devengado = float(monto_devengado or 0)
        self.monto_girado = float(monto_girado or 0)

    def to_dict(self):
        return {
            "ano": self.ano,
            "mes": self.mes,
            "fuente_nombre": self.fuente_nombre,
            "rubro_nombre": self.rubro_nombre,
            "pia": self.pia,
            "pim": self.pim,
            "monto_certificado": self.monto_certificado,
            "monto_comprometido": self.monto_comprometido,
            "monto_devengado": self.monto_devengado,
            "monto_girado": self.monto_girado
        }


class ProyectoInversion:
    def __init__(self, ano, fuente_nombre, rubro_nombre, producto_proyecto, producto_proyecto_nombre, pia, pim, monto_devengado_ano, monto_ejecucion_total):
        self.ano = ano
        self.fuente_nombre = fuente_nombre
        self.rubro_nombre = rubro_nombre
        self.producto_proyecto = producto_proyecto
        self.producto_proyecto_nombre = producto_proyecto_nombre
        self.pia = float(pia or 0)
        self.pim = float(pim or 0)
        self.monto_devengado_ano = float(monto_devengado_ano or 0)
        self.monto_ejecucion_total = float(monto_ejecucion_total or 0)

    def to_dict(self):
        return {
            "ano": self.ano,
            "fuente_nombre": self.fuente_nombre,
            "rubro_nombre": self.rubro_nombre,
            "producto_proyecto": self.producto_proyecto,
            "producto_proyecto_nombre": self.producto_proyecto_nombre,
            "pia": self.pia,
            "pim": self.pim,
            "monto_devengado_ano": self.monto_devengado_ano,
            "monto_ejecucion_total": self.monto_ejecucion_total
        }