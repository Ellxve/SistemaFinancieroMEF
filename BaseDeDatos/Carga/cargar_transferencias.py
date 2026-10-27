import pandas as pd
import mysql.connector
from pathlib import Path

# ============================================================
# CONFIGURACIÓN
# ============================================================

RUTAS = {
    2021: Path(
        r"D:\Gestión de datos e información\05_Transformacion"
        r"\datos_transformados\transferencias"
        r"\transferencias_2021_transformado.csv"
    ),
    2022: Path(
        r"D:\Gestión de datos e información\05_Transformacion"
        r"\datos_transformados\transferencias"
        r"\transferencias_2022_transformado.csv"
    ),
    2023: Path(
        r"D:\Gestión de datos e información\05_Transformacion"
        r"\datos_transformados\transferencias"
        r"\transferencias_2023_transformado.csv"
    ),
}

REGISTROS_ESPERADOS = {
    2021: 327563,
    2022: 347701,
    2023: 341997,
}

CHUNKSIZE = 10000

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
    "MES",
    "MES_NOMBRE",
    "GRUPO_TRANSFERENCIA",
    "GRUPO_TRANSFERENCIA_NOMBRE",
    "TIPO_ENTIDAD",
    "TIPO_ENTIDAD_NOMBRE",
    "PLIEGO",
    "PLIEGO_NOMBRE",
    "SEC_EJEC",
    "EJECUTORA_NOMBRE",
    "DEPARTAMENTO_EJECUTORA",
    "DEPARTAMENTO_EJECUTORA_NOMBRE",
    "PROVINCIA_EJECUTORA",
    "PROVINCIA_EJECUTORA_NOMBRE",
    "DISTRITO_EJECUTORA",
    "DISTRITO_EJECUTORA_NOMBRE",
    "RUBRO",
    "RUBRO_NOMBRE",
    "FUENTE",
    "FUENTE_NOMBRE",
    "RECURSO",
    "RECURSO_NOMBRE",
    "ORIGEN_OPERACION_NOMBRE",
    "MONTO_AUTORIZADO",
    "MONTO_ACREDITADO",
]

COLUMNAS_SQL = [
    "ano",
    "mes",
    "mes_nombre",
    "grupo_transferencia",
    "grupo_transferencia_nombre",
    "tipo_entidad",
    "tipo_entidad_nombre",
    "pliego",
    "pliego_nombre",
    "sec_ejec",
    "ejecutora_nombre",
    "departamento_ejecutora",
    "departamento_ejecutora_nombre",
    "provincia_ejecutora",
    "provincia_ejecutora_nombre",
    "distrito_ejecutora",
    "distrito_ejecutora_nombre",
    "rubro",
    "rubro_nombre",
    "fuente",
    "fuente_nombre",
    "recurso",
    "recurso_nombre",
    "origen_operacion_nombre",
    "monto_autorizado",
    "monto_acreditado",
]

PLACEHOLDERS = ", ".join(["%s"] * len(COLUMNAS_SQL))
NOMBRES_COLUMNAS_SQL = ", ".join(COLUMNAS_SQL)

SQL_INSERT = f"""
INSERT INTO transferencias (
    {NOMBRES_COLUMNAS_SQL}
)
VALUES (
    {PLACEHOLDERS}
)
"""

# ============================================================
# FUNCIONES
# ============================================================

def preparar_valor(valor):
    """
    Convierte valores ausentes de Pandas/NumPy en None para que
    MySQL los almacene como NULL.
    """
    if pd.isna(valor):
        return None

    # Convierte escalares NumPy a tipos nativos de Python
    if hasattr(valor, "item"):
        try:
            return valor.item()
        except ValueError:
            pass

    return valor


def preparar_filas(df):
    """
    Convierte cada fila del DataFrame en una tupla compatible
    con mysql.connector.
    """
    filas = []

    for fila in df[COLUMNAS_CSV].itertuples(index=False, name=None):
        filas.append(tuple(preparar_valor(valor) for valor in fila))

    return filas


# ============================================================
# CONEXIÓN
# ============================================================

conexion = None
cursor = None

try:
    conexion = mysql.connector.connect(**CONFIG_MYSQL)
    cursor = conexion.cursor()

    print("=" * 72)
    print("CARGA DE TRANSFERENCIAS 2021-2023 A MYSQL")
    print("=" * 72)

    # --------------------------------------------------------
    # Seguridad: la tabla debe estar vacía antes de comenzar
    # --------------------------------------------------------

    cursor.execute("SELECT COUNT(*) FROM transferencias")
    registros_previos = cursor.fetchone()[0]

    print(f"\nRegistros existentes antes de la carga: {registros_previos:,}")

    if registros_previos != 0:
        raise RuntimeError(
            "La tabla transferencias no está vacía. "
            "Se cancela la carga para evitar duplicar registros."
        )

    total_insertado = 0

    # ========================================================
    # CARGA POR AÑO
    # ========================================================

    for anio, ruta in RUTAS.items():

        print("\n" + "=" * 72)
        print(f"CARGANDO TRANSFERENCIAS {anio}")
        print("=" * 72)

        if not ruta.exists():
            raise FileNotFoundError(
                f"No se encontró el archivo:\n{ruta}"
            )

        registros_anio = 0
        numero_bloque = 0

        for bloque in pd.read_csv(
            ruta,
            chunksize=CHUNKSIZE,
            low_memory=False
        ):
            numero_bloque += 1

            # Verificación de estructura
            faltantes = [
                columna
                for columna in COLUMNAS_CSV
                if columna not in bloque.columns
            ]

            if faltantes:
                raise ValueError(
                    f"Faltan columnas en {ruta.name}: {faltantes}"
                )

            # Validación del año contenido en el bloque
            anos_bloque = set(
                pd.to_numeric(
                    bloque["ANO"],
                    errors="coerce"
                ).dropna().astype(int).unique()
            )

            if anos_bloque != {anio}:
                raise ValueError(
                    f"El archivo {ruta.name} contiene años "
                    f"inesperados: {sorted(anos_bloque)}"
                )

            filas = preparar_filas(bloque)

            cursor.executemany(SQL_INSERT, filas)
            conexion.commit()

            registros_bloque = len(filas)
            registros_anio += registros_bloque
            total_insertado += registros_bloque

            print(
                f"Año {anio} | "
                f"Bloque {numero_bloque:02d} | "
                f"Insertados acumulados: {registros_anio:,}"
            )

        esperado = REGISTROS_ESPERADOS[anio]

        print(f"\nRegistros esperados {anio}: {esperado:,}")
        print(f"Registros enviados a MySQL {anio}: {registros_anio:,}")

        if registros_anio != esperado:
            raise RuntimeError(
                f"La cantidad procesada para {anio} "
                f"no coincide con la esperada."
            )

    # ========================================================
    # VALIDACIÓN EN MYSQL
    # ========================================================

    print("\n" + "=" * 72)
    print("VALIDACIÓN DE LA CARGA")
    print("=" * 72)

    cursor.execute("""
        SELECT ano, COUNT(*)
        FROM transferencias
        GROUP BY ano
        ORDER BY ano
    """)

    resultados = cursor.fetchall()

    validacion_correcta = True

    for anio, cantidad in resultados:
        esperado = REGISTROS_ESPERADOS.get(int(anio))

        estado = (
            "CORRECTO"
            if cantidad == esperado
            else "REVISAR"
        )

        if cantidad != esperado:
            validacion_correcta = False

        print(
            f"{anio}: "
            f"{cantidad:,} registros | "
            f"Esperados: {esperado:,} | "
            f"{estado}"
        )

    cursor.execute("SELECT COUNT(*) FROM transferencias")
    total_mysql = cursor.fetchone()[0]

    total_esperado = sum(REGISTROS_ESPERADOS.values())

    print("\n" + "-" * 72)
    print(f"Total esperado: {total_esperado:,}")
    print(f"Total cargado en MySQL: {total_mysql:,}")
    print(f"Total enviado durante el proceso: {total_insertado:,}")

    if total_mysql == total_esperado and validacion_correcta:
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