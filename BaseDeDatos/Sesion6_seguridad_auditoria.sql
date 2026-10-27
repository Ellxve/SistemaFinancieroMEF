-- =============================================================================
-- FACULTAD DE INGENIERÍA - ESCUELA DE INGENIERÍA DE SISTEMAS
-- CURSO: GESTIÓN DE DATOS E INFORMACIÓN (2026-II)
-- SESIÓN 6: SEGURIDAD DE LA INFORMACIÓN EN BD, ROLES (DCL), ENMASCARAMIENTO Y TRAZABILIDAD
-- PROYECTO: Sistema de información financiera del MEF (2021–2023)
-- BASE DE DATOS: sistema_financiero_mef
-- =============================================================================

USE sistema_financiero_mef;

-- -----------------------------------------------------------------------------
-- 1. CREACIÓN DE ROLES DE BASE DE DATOS (RBAC / DCL)
-- -----------------------------------------------------------------------------
CREATE ROLE IF NOT EXISTS 'rol_ciudadano_consulta';
CREATE ROLE IF NOT EXISTS 'rol_operador_mef';
CREATE ROLE IF NOT EXISTS 'rol_auditor_mef';

-- -----------------------------------------------------------------------------
-- 2. ASIGNACIÓN DE PRIVILEGIOS A ROLES (GRANT)
-- -----------------------------------------------------------------------------

-- Rol Ciudadano Consulta: Acceso estrictamente de solo lectura (SELECT)
GRANT SELECT ON sistema_financiero_mef.ingreso TO 'rol_ciudadano_consulta';
GRANT SELECT ON sistema_financiero_mef.gasto_social TO 'rol_ciudadano_consulta';
GRANT SELECT ON sistema_financiero_mef.proyecto_inversion TO 'rol_ciudadano_consulta';
GRANT SELECT ON sistema_financiero_mef.transferencia TO 'rol_ciudadano_consulta';
GRANT SELECT ON sistema_financiero_mef.entidad_ejecutora TO 'rol_ciudadano_consulta';

-- Rol Operador MEF: Permisos de consulta e inserción para la carga de nuevos datasets (ej. CSV 2024)
GRANT SELECT, INSERT ON sistema_financiero_mef.transferencia TO 'rol_operador_mef';
GRANT SELECT, INSERT ON sistema_financiero_mef.ingreso TO 'rol_operador_mef';
GRANT SELECT ON sistema_financiero_mef.entidad_ejecutora TO 'rol_operador_mef';

-- Rol Auditor MEF: Acceso exclusivo a logs de auditoría y trazabilidad
GRANT SELECT ON sistema_financiero_mef.log_trazabilidad_acceso TO 'rol_auditor_mef';
GRANT SELECT ON sistema_financiero_mef.transferencia TO 'rol_auditor_mef';

-- -----------------------------------------------------------------------------
-- 3. CREACIÓN DE USUARIOS DE BD Y ASOCIACIÓN DE ROLES
-- -----------------------------------------------------------------------------

-- Usuario 1: Ciudadano / Web Público
CREATE USER IF NOT EXISTS 'us_web_publico'@'localhost' IDENTIFIED BY 'Consulta2026!';
GRANT 'rol_ciudadano_consulta' TO 'us_web_publico'@'localhost';
SET DEFAULT ROLE 'rol_ciudadano_consulta' TO 'us_web_publico'@'localhost';

-- Usuario 2: Operador MEF (Carga de datasets)
CREATE USER IF NOT EXISTS 'us_operador_lima'@'localhost' IDENTIFIED BY 'OperadorMef2026!';
GRANT 'rol_operador_mef' TO 'us_operador_lima'@'localhost';
SET DEFAULT ROLE 'rol_operador_mef' TO 'us_operador_lima'@'localhost';

-- Usuario 3: Auditor de Seguridad
CREATE USER IF NOT EXISTS 'us_auditor_mef'@'localhost' IDENTIFIED BY 'Auditoria2026!';
GRANT 'rol_auditor_mef' TO 'us_auditor_mef'@'localhost';
SET DEFAULT ROLE 'rol_auditor_mef' TO 'us_auditor_mef'@'localhost';

FLUSH PRIVILEGES;

-- -----------------------------------------------------------------------------
-- 4. ENMASCARAMIENTO Y PROTECCIÓN DE DATOS SENSIBLES
-- Vista protegida que enmascara parcialmente el origen de la operación
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW vw_transferencias_enmascaradas AS
SELECT 
    id_transferencia,
    sec_ejec,
    ano,
    mes,
    grupo_transferencia,
    -- Oculta los caracteres centrales del origen de operación
    CONCAT(LEFT(origen_operacion, 3), '****', RIGHT(origen_operacion, 2)) AS origen_operacion_protegido,
    monto_autorizado,
    monto_acreditado
FROM transferencia;

GRANT SELECT ON sistema_financiero_mef.vw_transferencias_enmascaradas TO 'rol_ciudadano_consulta';

-- -----------------------------------------------------------------------------
-- 5. TABLA DE TRAZABILIDAD Y TRIGGER DE AUDITORÍA
-- -----------------------------------------------------------------------------

-- Tabla para guardar el registro automático de eventos de auditoría
CREATE TABLE IF NOT EXISTS log_trazabilidad_acceso (
    id_log INT AUTO_INCREMENT PRIMARY KEY,
    usuario_bd VARCHAR(100) NOT NULL,
    host_origen VARCHAR(100) NOT NULL,
    tabla_afectada VARCHAR(100) NOT NULL,
    accion_realizada VARCHAR(100) NOT NULL,
    fecha_evento DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Trigger: Disparador automático que registra cuando el operador sube o inserta transferencias
DELIMITER //
CREATE TRIGGER trg_trazabilidad_transferencias
AFTER INSERT ON transferencia
FOR EACH ROW
BEGIN
    INSERT INTO log_trazabilidad_acceso (
        usuario_bd, 
        host_origen, 
        tabla_afectada, 
        accion_realizada, 
        fecha_evento
    )
    VALUES (
        USER(),
        CURRENT_USER(),
        'transferencia',
        CONCAT('CARGA_DATASET_NUEVO_REGISTRO_ANO_', NEW.ano),
        NOW()
    );
END //
DELIMITER ;