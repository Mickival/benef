-- SQLite
-- =========================================
-- ACTIVAR CLAVES FORÁNEAS (MUY IMPORTANTE)
-- =========================================
PRAGMA foreign_keys = ON;


-- =========================================
-- TABLA: BENEFICIARIOS
-- =========================================
CREATE TABLE IF NOT EXISTS beneficiarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    ci TEXT NOT NULL UNIQUE, -- Puede contener letras y números
    nombre TEXT NOT NULL,
    cite TEXT NOT NULL,

    nudecud TEXT, -- Guarda NUREJ o CUD
    tipo_codigo TEXT CHECK(tipo_codigo IN ('NUREJ','CUD')),

    fecha_inicio DATE NOT NULL,

    carga_horaria INTEGER NOT NULL
        CHECK(carga_horaria IN (4,6,8,16)),

    periodo_meses INTEGER NOT NULL
        CHECK(periodo_meses > 0),

    telefono TEXT
);


-- Índice para búsquedas rápidas por CI
CREATE INDEX IF NOT EXISTS idx_beneficiarios_ci
ON beneficiarios(ci);



-- =========================================
-- TABLA: ASISTENCIAS (PLANILLA REAL)
-- =========================================
CREATE TABLE asistencias(

id INTEGER PRIMARY KEY AUTOINCREMENT,
ci TEXT,
fecha TEXT,
dia TEXT,
hora_ingreso TEXT,
hora_salida TEXT,
horas REAL

)



-- Índices para acelerar consultas
CREATE INDEX IF NOT EXISTS idx_asistencias_beneficiario
ON asistencias(beneficiario_id);

CREATE INDEX IF NOT EXISTS idx_asistencias_fecha
ON asistencias(fecha);



-- TABLA: ACTIVIDADES MENSUALES
DROP TABLE actividades_mensuales;
CREATE TABLE actividades_mensuales (

id INTEGER PRIMARY KEY AUTOINCREMENT,
fecha DATE NOT NULL,
descripcion TEXT NOT NULL

);



-- =========================================
-- TABLA: INFORMES GENERADOS
-- =========================================
CREATE TABLE IF NOT EXISTS informes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    beneficiario_id INTEGER NOT NULL,

    tipo TEXT NOT NULL
        CHECK(tipo IN ('Mensual','Evaluacion','Conclusion','Incumplimiento')),

    fecha_generacion DATE NOT NULL,

    observaciones TEXT,

    FOREIGN KEY (beneficiario_id)
        REFERENCES beneficiarios(id)
        ON DELETE CASCADE
);


CREATE INDEX IF NOT EXISTS idx_informes_beneficiario
ON informes(beneficiario_id);



-- =========================================
-- VISTA PARA CALCULAR FECHA FIN
-- =========================================
CREATE VIEW IF NOT EXISTS vista_beneficiarios_resumen AS
SELECT 
    b.id,
    b.ci,
    b.nombre,
    b.carga_horaria,
    b.fecha_inicio,
    b.periodo_meses,
    date(b.fecha_inicio, '+' || b.periodo_meses || ' months') AS fecha_fin,
    ROUND(
        julianday(date(b.fecha_inicio, '+' || b.periodo_meses || ' months')) 
        - julianday('now')
    ) AS dias_restantes
FROM beneficiarios b;


SELECT * FROM vista_beneficiarios_resumen;


INSERT INTO beneficiarios 
(ci, nombre, cite, nudecud, tipo_codigo, fecha_inicio, carga_horaria, periodo_meses, telefono)
VALUES 
('7894561LP',
 'Juan Carlos Mamani Quispe',
 'GAMEA-12345-2026',
 '4587-A',
 'CUD',
 '2026-02-01',
 6,
 12,
 '76543210');


INSERT INTO actividades_mensuales (anio, mes, dia_semana, descripcion)
VALUES (2026, 2, 'Lunes', 'Limpieza de áreas verdes');

INSERT INTO actividades_mensuales (anio, mes, dia_semana, descripcion)
VALUES (2026, 2, 'Sabado', 'Apoyo en centro de salud');

INSERT INTO asistencias(beneficiario_id, fecha, hora_ingreso, hora_salida, actividad_realizada, estado)
VALUES (1, '2026-02-07', '08:00', '14:00', 'Apoyo en centro de salud', 'Asistio');

INSERT INTO asistencias(beneficiario_id, fecha, estado) 
VALUES (1, '2026-02-14', 'Falto');

INSERT INTO asistencias(beneficiario_id, fecha, hora_ingreso, hora_salida, actividad_realizada, estado)
VALUES (1, '2026-02-21', '08:10', '14:00', 'Apoyo en centro de salud', 'Asistio');

INSERT INTO asistencias(beneficiario_id, fecha, hora_ingreso, hora_salida, actividad_realizada, estado)
VALUES (1, '2026-02-28', '08:05', '14:00', 'Apoyo en centro de salud', 'Asistio');

INSERT INTO informes(beneficiario_id, tipo, fecha_generacion, observaciones)
VALUES (1, 'Mensual', '2026-02-28', 'Informe correspondiente al mes de febrero 2026');


DROP VIEW IF EXISTS vista_beneficiarios_resumen;

CREATE VIEW vista_beneficiarios_resumen AS
SELECT
    b.id,
    b.ci,
    b.nombre,
    b.carga_horaria,
    b.fecha_inicio,
    b.periodo_meses,

    date(b.fecha_inicio, '+' || b.periodo_meses || ' months') AS fecha_fin_legal,

    (
        SELECT MAX(fecha)
        FROM asistencias a
        WHERE a.beneficiario_id = b.id
    ) AS ultimo_sabado_registrado,

    CAST(
        (
        julianday(date(b.fecha_inicio, '+' || b.periodo_meses || ' months'))
        - julianday('now')
        ) / 7 AS INTEGER
    ) AS semanas_restantes

FROM beneficiarios b;

SELECT * FROM vista_beneficiarios_resumen;

SELECT * FROM actividades_mensuales;

SELECT * FROM asistencias;


SELECT * FROM beneficiarios;

SELECT name FROM sqlite_master WHERE type='table';


-- ============================================================
-- LIMPIEZA COMPLETA DE LA BASE DE DATOS
-- Elimina todos los datos y reinicia los contadores de ID
-- ============================================================

PRAGMA foreign_keys = OFF;

-- 1. Vaciar todas las tablas en orden correcto
--    (primero las que tienen FK, después las referenciadas)
DELETE FROM informes;
DELETE FROM asistencias;
DELETE FROM actividades_mensuales;
DELETE FROM beneficiarios;

-- 2. Reiniciar contadores AUTOINCREMENT
--    SQLite guarda el último ID en la tabla interna sqlite_sequence
DELETE FROM sqlite_sequence WHERE name = 'informes';
DELETE FROM sqlite_sequence WHERE name = 'asistencias';
DELETE FROM sqlite_sequence WHERE name = 'actividades_mensuales';
DELETE FROM sqlite_sequence WHERE name = 'beneficiarios';

PRAGMA foreign_keys = ON;

-- 3. Opcional: compactar el archivo .db para liberar espacio en disco
VACUUM;

-- Verificación — todas deben devolver 0
SELECT 'beneficiarios'       AS tabla, COUNT(*) AS registros FROM beneficiarios
UNION ALL
SELECT 'asistencias',                  COUNT(*)               FROM asistencias
UNION ALL
SELECT 'actividades_mensuales',        COUNT(*)               FROM actividades_mensuales
UNION ALL
SELECT 'informes',                     COUNT(*)               FROM informes;