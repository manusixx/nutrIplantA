-- ============================================================
-- nutrI-plantA — Inicialización de la base de datos
-- ============================================================
-- Crea esquemas separados para cada servicio según ADR-01.
-- Este script se ejecuta automáticamente la primera vez que
-- se levanta el contenedor de PostgreSQL.
-- ============================================================

-- Esquema para auth-service
CREATE SCHEMA IF NOT EXISTS auth;
COMMENT ON SCHEMA auth IS 'Esquema para auth-service: usuarios, roles, refresh tokens';

-- Esquema para diagnostico-service
CREATE SCHEMA IF NOT EXISTS diagnostico;
COMMENT ON SCHEMA diagnostico IS 'Esquema para diagnostico-service: cultivos, diagnósticos, planes, recordatorios';

-- Mensaje de confirmación
DO $$
BEGIN
    RAISE NOTICE 'Esquemas auth y diagnostico creados correctamente';
END $$;
