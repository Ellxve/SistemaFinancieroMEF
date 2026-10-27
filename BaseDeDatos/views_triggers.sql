USE sistema_financiero_mef;

-- =========================================================================
-- 1. VISTA CONSOLIDADA: Resumen financiero integral de las 4 capas/fuentes
-- Consolida Ingresos, Gasto Social, Transferencias y Proyectos por Entidad y Año
-- =========================================================================
CREATE OR REPLACE VIEW vw_resumen_financiero_integrado AS
SELECT 
    e.sec_ejec,
    e.ejecutora_nombre,
    periodo.ano,
    
    -- Totales de Transferencias
    COALESCE(SUM(t.monto_autorizado), 0) AS total_transferencia_autorizada,
    COALESCE(SUM(t.monto_acreditado), 0) AS total_transferencia_acreditada,
    
    -- Totales de Ingresos
    COALESCE(SUM(i.pia), 0) AS total_ingreso_pia,
    COALESCE(SUM(i.pim), 0) AS total_ingreso_pim,
    COALESCE(SUM(i.monto_recaudado), 0) AS total_ingreso_recaudado,
    
    -- Totales de Gasto Social
    COALESCE(SUM(g.pia), 0) AS total_gasto_social_pia,
    COALESCE(SUM(g.pim), 0) AS total_gasto_social_pim,
    COALESCE(SUM(g.monto_devengado), 0) AS total_gasto_social_devengado,
    
    -- Totales de Proyectos de Inversión
    COALESCE(SUM(p.pia), 0) AS total_proyectos_pia,
    COALESCE(SUM(p.pim), 0) AS total_proyectos_pim,
    COALESCE(SUM(p.monto_devengado_ano), 0) AS total_proyectos_devengado

FROM entidad_ejecutora e
CROSS JOIN (
    SELECT 2021 AS ano UNION ALL SELECT 2022 UNION ALL SELECT 2023
) periodo
LEFT JOIN transferencia t ON e.sec_ejec = t.sec_ejec AND periodo.ano = t.ano
LEFT JOIN ingreso i ON e.sec_ejec = i.sec_ejec AND periodo.ano = i.ano
LEFT JOIN gasto_social g ON e.sec_ejec = g.sec_ejec AND periodo.ano = g.ano
LEFT JOIN proyecto_inversion p ON e.sec_ejec = p.sec_ejec AND periodo.ano = p.ano
GROUP BY e.sec_ejec, e.ejecutora_nombre, periodo.ano;


-- =========================================================================
-- 2. TRIGGER: Validar integridad de montos en Transferencias
-- =========================================================================
DELIMITER //

CREATE TRIGGER trg_validar_monto_transferencia
BEFORE INSERT ON transferencia
FOR EACH ROW
BEGIN
    IF NEW.monto_autorizado < 0 OR NEW.monto_acreditado < 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Error de integridad: Los montos autorizado y acreditado no pueden ser negativos.';
    END IF;
END //

DELIMITER ;