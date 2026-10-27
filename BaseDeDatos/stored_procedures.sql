USE sistema_financiero_mef;

DELIMITER //

-- 1. PROCEDIMIENTO PARA EL BUSCADOR / AUTOCOMPLETADO DE ENTIDADES
-- Permite buscar por texto o directamente por código SEC_EJEC
CREATE PROCEDURE sp_buscar_entidades (
    IN p_criterio VARCHAR(255)
)
BEGIN
    SELECT 
        sec_ejec, 
        ejecutora_nombre 
    FROM entidad_ejecutora 
    WHERE ejecutora_nombre LIKE CONCAT('%', p_criterio, '%')
       OR CAST(sec_ejec AS CHAR) LIKE CONCAT('%', p_criterio, '%')
    LIMIT 20; -- Limita a las 20 coincidencias más cercanas para mayor rapidez
END //


-- 2. PROCEDIMIENTO PRINCIPAL: CONSULTA INTEGRADA POR SEC_EJEC Y RANGO DE AÑOS
CREATE PROCEDURE sp_consultar_integrado_entidad (
    IN p_sec_ejec INT,
    IN p_ano_inicio SMALLINT,
    IN p_ano_fin SMALLINT
)
BEGIN
    -- Información general de la Entidad
    SELECT sec_ejec, ejecutora_nombre 
    FROM entidad_ejecutora 
    WHERE sec_ejec = p_sec_ejec;

    -- Datos de Transferencias
    SELECT 
        t.ano,
        t.mes,
        f.fuente_nombre,
        r.rubro_nombre,
        t.grupo_transferencia,
        t.origen_operacion,
        t.monto_autorizado,
        t.monto_acreditado
    FROM transferencia t
    INNER JOIN fuente_financiamiento f ON t.codigo_fuente = f.codigo_fuente
    INNER JOIN rubro r ON t.codigo_rubro = r.codigo_rubro
    WHERE t.sec_ejec = p_sec_ejec 
      AND t.ano BETWEEN p_ano_inicio AND p_ano_fin;

    -- Datos de Ingresos
    SELECT 
        i.ano,
        i.mes,
        f.fuente_nombre,
        r.rubro_nombre,
        i.pia,
        i.pim,
        i.monto_recaudado
    FROM ingreso i
    INNER JOIN fuente_financiamiento f ON i.codigo_fuente = f.codigo_fuente
    INNER JOIN rubro r ON i.codigo_rubro = r.codigo_rubro
    WHERE i.sec_ejec = p_sec_ejec 
      AND i.ano BETWEEN p_ano_inicio AND p_ano_fin;

    -- Datos de Gasto Social
    SELECT 
        g.ano,
        g.mes,
        f.fuente_nombre,
        r.rubro_nombre,
        g.pia,
        g.pim,
        g.monto_certificado,
        g.monto_comprometido,
        g.monto_devengado,
        g.monto_girado
    FROM gasto_social g
    INNER JOIN fuente_financiamiento f ON g.codigo_fuente = f.codigo_fuente
    INNER JOIN rubro r ON g.codigo_rubro = r.codigo_rubro
    WHERE g.sec_ejec = p_sec_ejec 
      AND g.ano BETWEEN p_ano_inicio AND p_ano_fin;

    -- Datos de Proyectos de Inversión
    SELECT 
        p.ano,
        f.fuente_nombre,
        r.rubro_nombre,
        p.producto_proyecto,
        p.producto_proyecto_nombre,
        p.pia,
        p.pim,
        p.monto_devengado_ano,
        p.monto_ejecucion_total
    FROM proyecto_inversion p
    INNER JOIN fuente_financiamiento f ON p.codigo_fuente = f.codigo_fuente
    INNER JOIN rubro r ON p.codigo_rubro = r.codigo_rubro
    WHERE p.sec_ejec = p_sec_ejec 
      AND p.ano BETWEEN p_ano_inicio AND p_ano_fin;

END //

DELIMITER ;