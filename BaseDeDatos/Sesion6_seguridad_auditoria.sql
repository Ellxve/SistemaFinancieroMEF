
-- SESIÓN 6
USE sistema_financiero_mef;
-- 1. TABLA Y TRIGGER DE TRAZABILIDAD 

CREATE TABLE IF NOT EXISTS log_trazabilidad_acceso (
    id_log INT AUTO_INCREMENT PRIMARY KEY,
    usuario_bd VARCHAR(100) NOT NULL,
    host_origen VARCHAR(100) NOT NULL,
    tabla_afectada VARCHAR(100) NOT NULL,
    accion_realizada VARCHAR(100) NOT NULL,
    fecha_evento DATETIME DEFAULT CURRENT_TIMESTAMP
);

DROP TRIGGER IF EXISTS trg_trazabilidad_transferencias;

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

-- 2. VISTA CON ENMASCARAMIENTO DE DATOS SENSIBLES
CREATE OR REPLACE VIEW vw_transferencias_enmascaradas AS
SELECT 
    id_transferencia,
    sec_ejec,
    ano,
    mes,
    grupo_transferencia,
    CONCAT(LEFT(origen_operacion, 3), '****', RIGHT(origen_operacion, 2)) AS origen_operacion_protegido,
    monto_autorizado,
    monto_acreditado
FROM transferencia;

-- 3. CREACIÓN DE ROLES DE BASE DE DATOS (RBAC / DCL)
CREATE ROLE IF NOT EXISTS 'rol_ciudadano_consulta';
CREATE ROLE IF NOT EXISTS 'rol_operador_mef';
CREATE ROLE IF NOT EXISTS 'rol_auditor_mef';

-- 4. ASIGNACIÓN DE PRIVILEGIOS A ROLES (GRANT)
-- Rol Ciudadano Consulta
GRANT SELECT ON sistema_financiero_mef.ingreso TO 'rol_ciudadano_consulta';
GRANT SELECT ON sistema_financiero_mef.gasto_social TO 'rol_ciudadano_consulta';
GRANT SELECT ON sistema_financiero_mef.proyecto_inversion TO 'rol_ciudadano_consulta';
GRANT SELECT ON sistema_financiero_mef.transferencia TO 'rol_ciudadano_consulta';
GRANT SELECT ON sistema_financiero_mef.entidad_ejecutora TO 'rol_ciudadano_consulta';
GRANT SELECT ON sistema_financiero_mef.vw_transferencias_enmascaradas TO 'rol_ciudadano_consulta';

-- Rol Operador MEF
GRANT SELECT, INSERT ON sistema_financiero_mef.transferencia TO 'rol_operador_mef';
GRANT SELECT, INSERT ON sistema_financiero_mef.ingreso TO 'rol_operador_mef';
GRANT SELECT ON sistema_financiero_mef.entidad_ejecutora TO 'rol_operador_mef';

-- Rol Auditor MEF 
GRANT SELECT ON sistema_financiero_mef.log_trazabilidad_acceso TO 'rol_auditor_mef';
GRANT SELECT ON sistema_financiero_mef.transferencia TO 'rol_auditor_mef';

-- 5. CREACIÓN DE USUARIOS DE BD Y ASOCIACIÓN DE ROLES
CREATE USER IF NOT EXISTS 'us_web_publico'@'localhost' IDENTIFIED BY 'Consulta2026!';
GRANT 'rol_ciudadano_consulta' TO 'us_web_publico'@'localhost';
SET DEFAULT ROLE 'rol_ciudadano_consulta' TO 'us_web_publico'@'localhost';

CREATE USER IF NOT EXISTS 'us_operador_lima'@'localhost' IDENTIFIED BY 'OperadorMef2026!';
GRANT 'rol_operador_mef' TO 'us_operador_lima'@'localhost';
SET DEFAULT ROLE 'rol_operador_mef' TO 'us_operador_lima'@'localhost';

CREATE USER IF NOT EXISTS 'us_auditor_mef'@'localhost' IDENTIFIED BY 'Auditoria2026!';
GRANT 'rol_auditor_mef' TO 'us_auditor_mef'@'localhost';
SET DEFAULT ROLE 'rol_auditor_mef' TO 'us_auditor_mef'@'localhost';

FLUSH PRIVILEGES;