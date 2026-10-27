USE sistema_financiero_mef;
-- SESION 8

-- 1. CREACIÓN DE TABLAS (STAGING E HISTÓRICO)

-- Tabla Origen (Staging / Carga Temporal del CSV)
CREATE TABLE IF NOT EXISTS PJ_STAGING_TRANSFERENCIA (
    PJ_id_transferencia INT PRIMARY KEY,
    PJ_sec_ejec INT NOT NULL,
    PJ_codigo_fuente INT NOT NULL,
    PJ_codigo_rubro INT NOT NULL,
    PJ_ano INT NOT NULL,
    PJ_mes INT NOT NULL,
    PJ_origen_operacion VARCHAR(100),
    PJ_monto_autorizado DECIMAL(15,2),
    PJ_monto_acreditado DECIMAL(15,2)
);

-- Tabla Destino (Histórico Oficial de Producción MEF)
CREATE TABLE IF NOT EXISTS PJ_HISTORICO_TRANSFERENCIA (
    PJ_id_transferencia INT PRIMARY KEY,
    PJ_sec_ejec INT NOT NULL,
    PJ_codigo_fuente INT NOT NULL,
    PJ_codigo_rubro INT NOT NULL,
    PJ_ano INT NOT NULL,
    PJ_mes INT NOT NULL,
    PJ_origen_operacion VARCHAR(100),
    PJ_monto_autorizado DECIMAL(15,2),
    PJ_monto_acreditado DECIMAL(15,2),
    PJ_fecha_migracion DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. CARGA DE DATOS DE PRUEBA
INSERT INTO PJ_STAGING_TRANSFERENCIA 
    (PJ_id_transferencia, PJ_sec_ejec, PJ_codigo_fuente, PJ_codigo_rubro, PJ_ano, PJ_mes, PJ_origen_operacion, PJ_monto_autorizado, PJ_monto_acreditado)
VALUES
    (101, 301086, 5, 18, 2024, 1, 'CANON MINERO 2024', 500000.00, 480000.00),
    (102, 301086, 5, 18, 2024, 2, 'FONCOR 2024', 1200000.00, 1200000.00),
    (103, 301086, 5, 18, 2024, 3, 'SOBRETASA REGALIA', 85000.00, 0.00)
ON DUPLICATE KEY UPDATE PJ_monto_acreditado = VALUES(PJ_monto_acreditado);

-- Insertar registro previo en el Histórico para probar la actualización
INSERT INTO PJ_HISTORICO_TRANSFERENCIA 
    (PJ_id_transferencia, PJ_sec_ejec, PJ_codigo_fuente, PJ_codigo_rubro, PJ_ano, PJ_mes, PJ_origen_operacion, PJ_monto_autorizado, PJ_monto_acreditado, PJ_fecha_migracion)
VALUES
    (101, 301086, 5, 18, 2024, 1, 'CANON MINERO 2024', 500000.00, 400000.00, '2026-01-01 00:00:00')
ON DUPLICATE KEY UPDATE PJ_monto_acreditado = VALUES(PJ_monto_acreditado);

-- MERGE

INSERT INTO PJ_HISTORICO_TRANSFERENCIA (
    PJ_id_transferencia, PJ_sec_ejec, PJ_codigo_fuente, PJ_codigo_rubro,
    PJ_ano, PJ_mes, PJ_origen_operacion, PJ_monto_autorizado, PJ_monto_acreditado
)
SELECT 
    PJ_id_transferencia, PJ_sec_ejec, PJ_codigo_fuente, PJ_codigo_rubro,
    PJ_ano, PJ_mes, PJ_origen_operacion, PJ_monto_autorizado, PJ_monto_acreditado
FROM PJ_STAGING_TRANSFERENCIA
ON DUPLICATE KEY UPDATE
    PJ_monto_autorizado = VALUES(PJ_monto_autorizado),
    PJ_monto_acreditado = VALUES(PJ_monto_acreditado),
    PJ_fecha_migracion  = CURRENT_TIMESTAMP;


-- CURSOR DE MIGRACIÓN 
DROP PROCEDURE IF EXISTS sp_migrar_transferencias_cursor;

DELIMITER //

CREATE PROCEDURE sp_migrar_transferencias_cursor()
BEGIN
    -- Declaración de variables locales
    DECLARE v_id INT;
    DECLARE v_sec INT;
    DECLARE v_fue INT;
    DECLARE v_rub INT;
    DECLARE v_ano INT;
    DECLARE v_mes INT;
    DECLARE v_ori VARCHAR(100);
    DECLARE v_aut DECIMAL(15,2);
    DECLARE v_acr DECIMAL(15,2);
    DECLARE v_fin INT DEFAULT 0;
    DECLARE v_contador INT DEFAULT 0;

    -- 1. Declarar cursor
    DECLARE cur_transferencias CURSOR FOR 
        SELECT PJ_id_transferencia, PJ_sec_ejec, PJ_codigo_fuente, PJ_codigo_rubro, PJ_ano, PJ_mes, PJ_origen_operacion, PJ_monto_autorizado, PJ_monto_acreditado
        FROM PJ_STAGING_TRANSFERENCIA
        WHERE PJ_ano = 2024 AND PJ_monto_acreditado > 0;

    -- 2. Declarar manejador de fin de filas
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_fin = 1;

    -- 3. Abrir cursor
    OPEN cur_transferencias;

    -- 4. Bucle de migración
    read_loop: LOOP
        FETCH cur_transferencias INTO v_id, v_sec, v_fue, v_rub, v_ano, v_mes, v_ori, v_aut, v_acr;
        
        IF v_fin = 1 THEN
            LEAVE read_loop;
        END IF;

        -- Insertar solo si no existe previamente en el histórico
        IF NOT EXISTS (SELECT 1 FROM PJ_HISTORICO_TRANSFERENCIA WHERE PJ_id_transferencia = v_id) THEN
            INSERT INTO PJ_HISTORICO_TRANSFERENCIA (
                PJ_id_transferencia, PJ_sec_ejec, PJ_codigo_fuente, PJ_codigo_rubro,
                PJ_ano, PJ_mes, PJ_origen_operacion, PJ_monto_autorizado, PJ_monto_acreditado
            )
            VALUES (v_id, v_sec, v_fue, v_rub, v_ano, v_mes, v_ori, v_aut, v_acr);
            
            SET v_contador = v_contador + 1;
        END IF;
    END LOOP;

    -- 5. Cerrar cursor
    CLOSE cur_transferencias;

    SELECT CONCAT('Migración realizada con éxito. Filas insertadas: ', v_contador) AS Resultado;
END //

DELIMITER ;

-- Ejecutar el procedimiento del cursor
CALL sp_migrar_transferencias_cursor();

-- 3. CONSULTA DE VERIFICACIÓN
SELECT * FROM PJ_HISTORICO_TRANSFERENCIA;