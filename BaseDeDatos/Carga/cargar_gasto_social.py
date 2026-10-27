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
        r"\datos_transformados\gasto_social"
        r"\gasto_social_2021_transformado.csv"
    ),
    2022: Path(
        r"D:\Gestión de datos e información\05_Transformacion"
        r"\datos_transformados\gasto_social"
        r"\gasto_social_2022_transformado.csv"
    ),
    2023: Path(
        r"D:\Gestión de datos e información\05_Transformacion"
        r"\datos_transformados\gasto_social"
        r"\gasto_social_2023_transformado.csv"
    ),
}

REGISTROS_ESPERADOS = {
    2021: 4659466,
    2022: 4848187,
    2023: 5053653,
}

CHUNKSIZE = 20000

CONFIG_MYSQL = {
    "host": "localhost",
    "user": "root",
    "password": "Icommerce2026!",
    "database": "sistema_finanzas_mef",
}


# ============================================================
# COLUMNAS DEL CSV
# ============================================================

COLUMNAS_CSV = [
    "ANO",
    "MES",
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
    "SEC_FUNC",
    "PROGRAMA_PPTO",
    "PROGRAMA_PPTO_NOMBRE",
    "TIPO_ACT_PROY",
    "TIPO_ACT_PROY_NOMBRE",
    "PRODUCTO_PROYECTO",
    "PRODUCTO_PROYECTO_NOMBRE",
    "ACTIVIDAD_ACCION_OBRA",
    "ACTIVIDAD_ACCION_OBRA_NOMBRE",
    "FUNCION",
    "FUNCION_NOMBRE",
    "DIVISION_FUNCIONAL",
    "DIVISION_FUNCIONAL_NOMBRE",
    "GRUPO_FUNCIONAL",
    "GRUPO_FUNCIONAL_NOMBRE",
    "META",
    "FINALIDAD",
    "META_NOMBRE",
    "DEPARTAMENTO_META",
    "DEPARTAMENTO_META_NOMBRE",
    "FUENTE_FINANCIAMIENTO",
    "FUENTE_FINANCIAMIENTO_NOMBRE",
    "RUBRO",
    "RUBRO_NOMBRE",
    "TIPO_RECURSO",
    "TIPO_RECURSO_NOMBRE",
    "CATEGORIA_GASTO",
    "CATEGORIA_GASTO_NOMBRE",
    "TIPO_TRANSACCION",
    "GENERICA",
    "GENERICA_NOMBRE",
    "SUBGENERICA",
    "SUBGENERICA_NOMBRE",
    "SUBGENERICA_DET",
    "SUBGENERICA_DET_NOMBRE",
    "ESPECIFICA",
    "ESPECIFICA_NOMBRE",
    "ESPECIFICA_DET",
    "ESPECIFICA_DET_NOMBRE",
    "MONTO_PIA",
    "MONTO_PIM",
    "MONTO_CERTIFICADO",
    "MONTO_COMPROMETIDO_ANUAL",
    "MONTO_COMPROMETIDO",
    "MONTO_DEVENGADO",
    "MONTO_GIRADO",
    "GASTO_SOCIAL",
]


# ============================================================
# SENTENCIA SQL
# ============================================================

COLUMNAS_SQL = [columna.lower() for columna in COLUMNAS_CSV]

placeholders = ", ".join(
    ["%s"] * len(COLUMNAS_SQL)
)

columnas_sql_texto = ", ".join(
    COLUMNAS_SQL
)

SQL_INSERT = f"""
INSERT INTO gasto_social (
    {columnas_sql_texto}
)
VALUES (
    {placeholders}
)
"""


# ============================================================
# PREPARACIÓN DE DATOS
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
        tuple(
            preparar_valor(valor)
            for valor in fila
        )
        for fila in df[COLUMNAS_CSV].itertuples(
            index=False,
            name=None
        )
    ]


# ============================================================
# FUNCIÓN PARA CONSULTAR REGISTROS EXISTENTES
# ============================================================

def obtener_registros_existentes(cursor, anio):

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM gasto_social
        WHERE ano = %s
        """,
        (anio,)
    )

    return cursor.fetchone()[0]


# ============================================================
# CARGA REANUDABLE
# ============================================================

conexion = None
cursor = None

try:

    print("=" * 76)
    print("CARGA REANUDABLE DE GASTO SOCIAL 2021-2023")
    print("=" * 76)

    conexion = mysql.connector.connect(
        **CONFIG_MYSQL
    )

    cursor = conexion.cursor()

    inicio_global = time.time()
    total_insertado_sesion = 0

    # ========================================================
    # ESTADO INICIAL DE MYSQL
    # ========================================================

    print("\nESTADO INICIAL DE LA TABLA")
    print("-" * 76)

    for anio in RUTAS:

        existentes = obtener_registros_existentes(
            cursor,
            anio
        )

        esperado = REGISTROS_ESPERADOS[anio]

        print(
            f"{anio}: {existentes:,} / "
            f"{esperado:,} registros"
        )

        if existentes > esperado:
            raise RuntimeError(
                f"El año {anio} contiene más registros "
                f"({existentes:,}) que los esperados "
                f"({esperado:,}). Se cancela la carga "
                f"para evitar inconsistencias."
            )

    # ========================================================
    # PROCESAMIENTO POR AÑO
    # ========================================================

    for anio, ruta in RUTAS.items():

        print("\n" + "=" * 76)
        print(f"PROCESANDO GASTO SOCIAL {anio}")
        print("=" * 76)

        if not ruta.exists():
            raise FileNotFoundError(
                f"No se encontró el archivo:\n{ruta}"
            )

        existentes = obtener_registros_existentes(
            cursor,
            anio
        )

        esperado = REGISTROS_ESPERADOS[anio]

        # ----------------------------------------------------
        # Si el año ya está completo, se omite
        # ----------------------------------------------------

        if existentes == esperado:

            print(
                f"El año {anio} ya está completamente "
                f"cargado ({existentes:,} registros)."
            )

            print("No se realizarán nuevas inserciones.")

            continue

        print(
            f"Registros ya existentes: {existentes:,}"
        )

        print(
            f"Registros pendientes: "
            f"{esperado - existentes:,}"
        )

        print(
            f"La lectura continuará desde el registro "
            f"{existentes + 1:,}."
        )

        inicio_anio = time.time()

        registros_recorridos = 0
        registros_insertados_anio = 0
        bloque_numero = 0

        lector = pd.read_csv(
            ruta,
            chunksize=CHUNKSIZE,
            low_memory=False
        )

        for bloque in lector:

            bloque_numero += 1

            inicio_bloque = registros_recorridos
            fin_bloque = (
                registros_recorridos + len(bloque)
            )

            # ------------------------------------------------
            # El bloque completo ya está almacenado
            # ------------------------------------------------

            if fin_bloque <= existentes:

                registros_recorridos = fin_bloque

                continue

            # ------------------------------------------------
            # El punto de reanudación está dentro del bloque
            # ------------------------------------------------

            if inicio_bloque < existentes < fin_bloque:

                filas_a_saltar = (
                    existentes - inicio_bloque
                )

                bloque = bloque.iloc[
                    filas_a_saltar:
                ].copy()

            registros_recorridos = fin_bloque

            # ------------------------------------------------
            # Validar estructura
            # ------------------------------------------------

            faltantes = [
                columna
                for columna in COLUMNAS_CSV
                if columna not in bloque.columns
            ]

            if faltantes:

                raise ValueError(
                    f"Faltan columnas en "
                    f"{ruta.name}: {faltantes}"
                )

            # ------------------------------------------------
            # Validar año
            # ------------------------------------------------

            anos_bloque = set(
                pd.to_numeric(
                    bloque["ANO"],
                    errors="coerce"
                )
                .dropna()
                .astype(int)
                .unique()
            )

            if anos_bloque != {anio}:

                raise ValueError(
                    f"El archivo {ruta.name} contiene "
                    f"años inesperados: "
                    f"{sorted(anos_bloque)}"
                )

            # ------------------------------------------------
            # Preparar e insertar
            # ------------------------------------------------

            filas = preparar_filas(bloque)

            if not filas:
                continue

            cursor.executemany(
                SQL_INSERT,
                filas
            )

            conexion.commit()

            cantidad = len(filas)

            registros_insertados_anio += cantidad
            total_insertado_sesion += cantidad

            total_actual = (
                existentes
                + registros_insertados_anio
            )

            print(
                f"Año {anio} | "
                f"Bloque {bloque_numero:03d} | "
                f"MySQL: {total_actual:,} / "
                f"{esperado:,}"
            )

        # ----------------------------------------------------
        # VALIDACIÓN DEL AÑO DIRECTAMENTE EN MYSQL
        # ----------------------------------------------------

        total_mysql_anio = (
            obtener_registros_existentes(
                cursor,
                anio
            )
        )

        tiempo_anio = (
            time.time() - inicio_anio
        ) / 60

        print("\n" + "-" * 76)

        print(
            f"Registros que existían previamente: "
            f"{existentes:,}"
        )

        print(
            f"Registros insertados en esta ejecución: "
            f"{registros_insertados_anio:,}"
        )

        print(
            f"Total actual en MySQL para {anio}: "
            f"{total_mysql_anio:,}"
        )

        print(
            f"Total esperado para {anio}: "
            f"{esperado:,}"
        )

        print(
            f"Tiempo aproximado: "
            f"{tiempo_anio:.2f} minutos"
        )

        if total_mysql_anio != esperado:

            raise RuntimeError(
                f"La carga de {anio} terminó con "
                f"{total_mysql_anio:,} registros, "
                f"pero se esperaban {esperado:,}."
            )

        print(
            f"Validación de {anio}: CORRECTA"
        )

    # ========================================================
    # VALIDACIÓN FINAL
    # ========================================================

    print("\n" + "=" * 76)
    print("VALIDACIÓN FINAL EN MYSQL")
    print("=" * 76)

    cursor.execute(
        """
        SELECT ano, COUNT(*)
        FROM gasto_social
        GROUP BY ano
        ORDER BY ano
        """
    )

    resultados = cursor.fetchall()

    validacion_correcta = True

    for anio, cantidad in resultados:

        anio = int(anio)

        esperado = REGISTROS_ESPERADOS.get(
            anio
        )

        if esperado is None:
            validacion_correcta = False
            estado = "AÑO NO ESPERADO"

        elif cantidad == esperado:
            estado = "CORRECTO"

        else:
            validacion_correcta = False
            estado = "REVISAR"

        print(
            f"{anio}: "
            f"{cantidad:,} registros | "
            f"Esperados: "
            f"{esperado if esperado is None else f'{esperado:,}'} | "
            f"{estado}"
        )

    cursor.execute(
        "SELECT COUNT(*) FROM gasto_social"
    )

    total_mysql = cursor.fetchone()[0]

    total_esperado = sum(
        REGISTROS_ESPERADOS.values()
    )

    tiempo_total = (
        time.time() - inicio_global
    ) / 60

    print("\n" + "-" * 76)

    print(
        f"Total esperado: "
        f"{total_esperado:,}"
    )

    print(
        f"Total cargado en MySQL: "
        f"{total_mysql:,}"
    )

    print(
        f"Registros insertados durante "
        f"esta ejecución: "
        f"{total_insertado_sesion:,}"
    )

    print(
        f"Tiempo total aproximado: "
        f"{tiempo_total:.2f} minutos"
    )

    if (
        total_mysql == total_esperado
        and validacion_correcta
    ):

        print(
            "\nRESULTADO: "
            "CARGA COMPLETA Y VALIDADA"
        )

    else:

        print(
            "\nRESULTADO: "
            "LA CARGA REQUIERE REVISIÓN"
        )

    print("=" * 76)


except Exception as error:

    if (
        conexion is not None
        and conexion.is_connected()
    ):
        conexion.rollback()

    print("\n" + "=" * 76)
    print("ERROR DURANTE LA CARGA")
    print("=" * 76)
    print(error)
    print("=" * 76)


finally:

    if cursor is not None:
        cursor.close()

    if (
        conexion is not None
        and conexion.is_connected()
    ):
        conexion.close()