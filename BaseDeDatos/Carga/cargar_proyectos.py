import pandas as pd
import mysql.connector
from pathlib import Path
import time

# ============================================================
# CONFIGURACIÓN
# ============================================================

RUTAS = {
    2021: Path(
        r"D:\Gestión de datos e información\05_Transformacion"
        r"\datos_transformados\proyectos"
        r"\proyectos_2021_transformado.csv"
    ),
    2022: Path(
        r"D:\Gestión de datos e información\05_Transformacion"
        r"\datos_transformados\proyectos"
        r"\proyectos_2022_transformado.csv"
    ),
    2023: Path(
        r"D:\Gestión de datos e información\05_Transformacion"
        r"\datos_transformados\proyectos"
        r"\proyectos_2023_transformado.csv"
    ),
}

REGISTROS_ESPERADOS = {
    2021: 86650,
    2022: 93756,
    2023: 88285,
}

CHUNKSIZE = 20000

CONFIG_MYSQL = {
    "host": "localhost",
    "user": "root",
    "password": "Icommerce2026!",
    "database": "sistema_finanzas_mef",
}

# ============================================================
# COLUMNAS
# ============================================================

COLUMNAS_CSV = [
    "ANO",
    "NIVEL_GOBIERNO",
    "NIVEL_GOBIERNO_NOMBRE",
    "SECTOR",
    "SECTOR_NOMBRE",
    "PLIEGO",
    "PLIEGO_NOMBRE",
    "SEC_EJEC",
    "EJECUTORA",
    "EJECUTORA_NOMBRE",
    "DEPARTAMENTO_EJECUTORA",
    "DEPARTAMENTO_EJECUTORA_NOMBRE",
    "PROVINCIA_EJECUTORA",
    "PROVINCIA_EJECUTORA_NOMBRE",
    "DISTRITO_EJECUTORA",
    "DISTRITO_EJECUTORA_NOMBRE",
    "TIPO_ACT_PROY",
    "TIPO_ACT_PROY_NOMBRE",
    "PRODUCTO_PROYECTO",
    "PRODUCTO_PROYECTO_NOMBRE",
    "FUNCION",
    "FUNCION_NOMBRE",
    "DEPARTAMENTO_META",
    "DEPARTAMENTO_META_NOMBRE",
    "FUENTE_FINANCIAMIENTO",
    "FUENTE_FINANCIAMIENTO_NOMBRE",
    "RUBRO",
    "RUBRO_NOMBRE",
    "MONTO_EJECUCION_HASTA_HACE_2_ANOS",
    "MONTO_EJECUCION_ANO_ANTERIOR",
    "MONTO_PIA",
    "MONTO_PIM",
    "MONTO_DEVENGADO_ANO_EJE",
    "MONTO_EJECUCION_TOTAL",
]

COLUMNAS_SQL = [col.lower() for col in COLUMNAS_CSV]

SQL_INSERT = f"""
INSERT INTO proyectos (
    {", ".join(COLUMNAS_SQL)}
)
VALUES (
    {", ".join(["%s"] * len(COLUMNAS_SQL))}
)
"""

# ============================================================
# PREPARACIÓN
# ============================================================

def preparar_valor(valor):
    if pd.isna(valor):
        return None

    if hasattr(valor, "item"):
        try:
            return valor.item()
        except (ValueError, AttributeError):
            pass

    return valor


def preparar_filas(df):
    return [
        tuple(preparar_valor(valor) for valor in fila)
        for fila in df[COLUMNAS_CSV].itertuples(
            index=False,
            name=None
        )
    ]


# ============================================================
# CONEXIÓN Y CARGA
# ============================================================

conexion = None
cursor = None

try:
    print("=" * 72)
    print("CARGA DE PROYECTOS DE INVERSIÓN 2021-2023")
    print("=" * 72)

    conexion = mysql.connector.connect(**CONFIG_MYSQL)
    cursor = conexion.cursor()

    # Verificar que la tabla esté vacía
    cursor.execute("SELECT COUNT(*) FROM proyectos")
    registros_iniciales = cursor.fetchone()[0]

    print(f"\nRegistros existentes antes de la carga: {registros_iniciales:,}")

    if registros_iniciales != 0:
        raise RuntimeError(
            "La tabla proyectos no está vacía. "
            "Se cancela la carga para evitar duplicados."
        )

    inicio = time.time()
    total_insertado = 0

    for anio, ruta in RUTAS.items():

        print("\n" + "=" * 72)
        print(f"PROCESANDO PROYECTOS {anio}")
        print("=" * 72)

        if not ruta.exists():
            raise FileNotFoundError(
                f"No se encontró el archivo: {ruta}"
            )

        insertados_anio = 0
        bloque_numero = 0

        for bloque in pd.read_csv(
            ruta,
            chunksize=CHUNKSIZE,
            low_memory=False
        ):
            bloque_numero += 1

            # Validar columnas
            faltantes = [
                columna
                for columna in COLUMNAS_CSV
                if columna not in bloque.columns
            ]

            if faltantes:
                raise ValueError(
                    f"Faltan columnas en {ruta.name}: {faltantes}"
                )

            # Validar el año
            anos = set(
                pd.to_numeric(
                    bloque["ANO"],
                    errors="coerce"
                )
                .dropna()
                .astype(int)
                .unique()
            )

            if anos != {anio}:
                raise ValueError(
                    f"{ruta.name} contiene años inesperados: "
                    f"{sorted(anos)}"
                )

            filas = preparar_filas(bloque)

            cursor.executemany(SQL_INSERT, filas)
            conexion.commit()

            cantidad = len(filas)

            insertados_anio += cantidad
            total_insertado += cantidad

            print(
                f"Año {anio} | "
                f"Bloque {bloque_numero:02d} | "
                f"Registros cargados: {insertados_anio:,}"
            )

        esperado = REGISTROS_ESPERADOS[anio]

        cursor.execute(
            "SELECT COUNT(*) FROM proyectos WHERE ano = %s",
            (anio,)
        )

        total_mysql_anio = cursor.fetchone()[0]

        print("-" * 72)
        print(f"Total esperado para {anio}: {esperado:,}")
        print(f"Total cargado en MySQL: {total_mysql_anio:,}")

        if total_mysql_anio != esperado:
            raise RuntimeError(
                f"La cantidad cargada para {anio} no coincide "
                f"con la cantidad esperada."
            )

        print(f"Validación {anio}: CORRECTA")

    # ========================================================
    # VALIDACIÓN FINAL
    # ========================================================

    cursor.execute("""
        SELECT ano, COUNT(*)
        FROM proyectos
        GROUP BY ano
        ORDER BY ano
    """)

    resultados = cursor.fetchall()

    print("\n" + "=" * 72)
    print("VALIDACIÓN FINAL")
    print("=" * 72)

    for anio, cantidad in resultados:
        print(
            f"{anio}: {cantidad:,} registros"
        )

    cursor.execute("SELECT COUNT(*) FROM proyectos")
    total_mysql = cursor.fetchone()[0]

    total_esperado = sum(REGISTROS_ESPERADOS.values())

    tiempo = (time.time() - inicio) / 60

    print("\n" + "-" * 72)
    print(f"Total esperado: {total_esperado:,}")
    print(f"Total cargado en MySQL: {total_mysql:,}")
    print(f"Total enviado durante el proceso: {total_insertado:,}")
    print(f"Tiempo total aproximado: {tiempo:.2f} minutos")

    if total_mysql == total_esperado:
        print("\nRESULTADO: CARGA COMPLETA Y VALIDADA")
    else:
        print("\nRESULTADO: LA CARGA REQUIERE REVISIÓN")

    print("=" * 72)

except Exception as error:

    if conexion is not None and conexion.is_connected():
        conexion.rollback()

    print("\n" + "=" * 72)
    print("ERROR DURANTE LA CARGA")
    print("=" * 72)
    print(error)
    print("=" * 72)

finally:

    if cursor is not None:
        cursor.close()

    if conexion is not None and conexion.is_connected():
        conexion.close()