USE sistema_financiero_mef;
-- SESION 7
-- 1. VERIFICAR LOS INDICES EXISTENTES
SHOW INDEX FROM ingreso;
SHOW INDEX FROM gasto_social;
SHOW INDEX FROM transferencia;
SHOW INDEX FROM proyecto_inversion;

-- 2. CONSULTA CON INNER JOIN, AGREGACION Y SUBCONSULTA
SELECT
    e.sec_ejec AS codigo_ejecutora,
    e.ejecutora_nombre AS nombre_entidad,
    SUM(i.pia) AS total_pia
FROM entidad_ejecutora e
INNER JOIN ingreso i
    ON e.sec_ejec = i.sec_ejec
WHERE i.ano = 2023
GROUP BY e.sec_ejec, e.ejecutora_nombre
HAVING SUM(i.pia) > (
    SELECT AVG(pia)
    FROM ingreso
    WHERE ano = 2023
)
LIMIT 50;


-- 3. CONSULTA CON LEFT JOIN
SELECT
    e.sec_ejec AS codigo_ejecutora,
    e.ejecutora_nombre AS nombre_entidad,
    COALESCE(SUM(i.pia), 0) AS total_pia
FROM entidad_ejecutora e
LEFT JOIN ingreso i
    ON e.sec_ejec = i.sec_ejec
    AND i.ano = 2023
GROUP BY e.sec_ejec, e.ejecutora_nombre
LIMIT 50;


-- 4. FUNCION DEFINIDA POR EL USUARIO (UDF)
DROP FUNCTION IF EXISTS fn_CalcularPorcentajeEjecucionGlobal;

DELIMITER //

CREATE FUNCTION fn_CalcularPorcentajeEjecucionGlobal(
    p_ingresos DECIMAL(20,2),
    p_transferencias DECIMAL(20,2),
    p_gasto DECIMAL(20,2)
)
RETURNS DECIMAL(7,2)
DETERMINISTIC
BEGIN
    DECLARE v_total DECIMAL(20,2);

    SET v_total = IFNULL(p_ingresos, 0)
                + IFNULL(p_transferencias, 0);

    IF v_total = 0 THEN
        RETURN 0.00;
    END IF;

    RETURN (IFNULL(p_gasto, 0) / v_total) * 100;
END //

DELIMITER ;

-- 5. PROBAR LA FUNCION CON VALORES DE EJEMPLO
SELECT fn_CalcularPorcentajeEjecucionGlobal(
    1000.00, 300.00, 800.00
) AS porcentaje_ejecucion;


-- 6. ANALISIS DEL PLAN DE EJECUCION
EXPLAIN
SELECT
    sec_ejec,
    SUM(pia) AS total_pia
FROM ingreso
WHERE ano = 2023
GROUP BY sec_ejec;
