CREATE DATABASE IF NOT EXISTS sistema_financiero_mef;

USE sistema_financiero_mef;

CREATE TABLE entidad_ejecutora (
    sec_ejec INT NOT NULL,
    ejecutora_nombre VARCHAR(500) NOT NULL,

    PRIMARY KEY (sec_ejec)
);

CREATE TABLE fuente_financiamiento (
    codigo_fuente INT NOT NULL,
    fuente_nombre VARCHAR(255) NOT NULL,

    PRIMARY KEY (codigo_fuente)
);

CREATE TABLE rubro (
    codigo_rubro INT NOT NULL,
    rubro_nombre VARCHAR(255) NOT NULL,

    PRIMARY KEY (codigo_rubro)
);

USE sistema_financiero_mef;

-- TABLA: TRANSFERENCIA

CREATE TABLE transferencia (
    id_transferencia BIGINT NOT NULL AUTO_INCREMENT,
    sec_ejec INT NOT NULL,
    codigo_fuente INT NOT NULL,
    codigo_rubro INT NOT NULL,
    ano SMALLINT NOT NULL,
    mes TINYINT NOT NULL,
    grupo_transferencia VARCHAR(255),
    origen_operacion VARCHAR(255),
    monto_autorizado DECIMAL(20,2),
    monto_acreditado DECIMAL(20,2),

    PRIMARY KEY (id_transferencia),

    CONSTRAINT fk_transferencia_entidad
        FOREIGN KEY (sec_ejec)
        REFERENCES entidad_ejecutora(sec_ejec),

    CONSTRAINT fk_transferencia_fuente
        FOREIGN KEY (codigo_fuente)
        REFERENCES fuente_financiamiento(codigo_fuente),

    CONSTRAINT fk_transferencia_rubro
        FOREIGN KEY (codigo_rubro)
        REFERENCES rubro(codigo_rubro)
);


-- TABLA: INGRESO

CREATE TABLE ingreso (
    id_ingreso BIGINT NOT NULL AUTO_INCREMENT,
    sec_ejec INT NOT NULL,
    codigo_fuente INT NOT NULL,
    codigo_rubro INT NOT NULL,
    ano SMALLINT NOT NULL,
    mes TINYINT NOT NULL,
    pia DECIMAL(20,2),
    pim DECIMAL(20,2),
    monto_recaudado DECIMAL(20,2),

    PRIMARY KEY (id_ingreso),

    CONSTRAINT fk_ingreso_entidad
        FOREIGN KEY (sec_ejec)
        REFERENCES entidad_ejecutora(sec_ejec),

    CONSTRAINT fk_ingreso_fuente
        FOREIGN KEY (codigo_fuente)
        REFERENCES fuente_financiamiento(codigo_fuente),

    CONSTRAINT fk_ingreso_rubro
        FOREIGN KEY (codigo_rubro)
        REFERENCES rubro(codigo_rubro)
);

-- TABLA: GASTO SOCIAL

CREATE TABLE gasto_social (
    id_gasto BIGINT NOT NULL AUTO_INCREMENT,
    sec_ejec INT NOT NULL,
    codigo_fuente INT NOT NULL,
    codigo_rubro INT NOT NULL,
    ano SMALLINT NOT NULL,
    mes TINYINT NOT NULL,
    pia DECIMAL(20,2),
    pim DECIMAL(20,2),
    monto_certificado DECIMAL(20,2),
    monto_comprometido DECIMAL(20,2),
    monto_devengado DECIMAL(20,2),
    monto_girado DECIMAL(20,2),

    PRIMARY KEY (id_gasto),

    CONSTRAINT fk_gasto_entidad
        FOREIGN KEY (sec_ejec)
        REFERENCES entidad_ejecutora(sec_ejec),

    CONSTRAINT fk_gasto_fuente
        FOREIGN KEY (codigo_fuente)
        REFERENCES fuente_financiamiento(codigo_fuente),

    CONSTRAINT fk_gasto_rubro
        FOREIGN KEY (codigo_rubro)
        REFERENCES rubro(codigo_rubro)
);

-- TABLA: PROYECTO DE INVERSIÓN

CREATE TABLE proyecto_inversion (
    id_proyecto BIGINT NOT NULL AUTO_INCREMENT,
    sec_ejec INT NOT NULL,
    codigo_fuente INT NOT NULL,
    codigo_rubro INT NOT NULL,
    ano SMALLINT NOT NULL,
    producto_proyecto BIGINT,
    producto_proyecto_nombre VARCHAR(500),
    pia DECIMAL(20,2),
    pim DECIMAL(20,2),
    monto_devengado_ano DECIMAL(20,2),
    monto_ejecucion_total DECIMAL(20,2),

    PRIMARY KEY (id_proyecto),

    CONSTRAINT fk_proyecto_entidad
        FOREIGN KEY (sec_ejec)
        REFERENCES entidad_ejecutora(sec_ejec),

    CONSTRAINT fk_proyecto_fuente
        FOREIGN KEY (codigo_fuente)
        REFERENCES fuente_financiamiento(codigo_fuente),

    CONSTRAINT fk_proyecto_rubro
        FOREIGN KEY (codigo_rubro)
        REFERENCES rubro(codigo_rubro)
);

