-- =============================================================================
-- NAVAM — PostgreSQL Initialisation Script
-- Runs once on first container boot via docker-entrypoint-initdb.d
-- =============================================================================

-- ---------------------------------------------------------------------------
-- Extensions (on the default "navam" database)
-- ---------------------------------------------------------------------------
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS btree_gin;
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- ---------------------------------------------------------------------------
-- Application schemas
-- ---------------------------------------------------------------------------
CREATE SCHEMA IF NOT EXISTS navam;
CREATE SCHEMA IF NOT EXISTS audit;
CREATE SCHEMA IF NOT EXISTS ml;

-- Set default search path so application queries resolve without schema prefix
ALTER DATABASE navam SET search_path TO navam, public;

-- ---------------------------------------------------------------------------
-- Audit helper function — records row-level changes
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION audit.record_change()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        INSERT INTO audit.log(table_name, operation, old_data, changed_at)
        VALUES (TG_TABLE_NAME, TG_OP, row_to_json(OLD), NOW());
        RETURN OLD;
    ELSE
        INSERT INTO audit.log(table_name, operation, old_data, new_data, changed_at)
        VALUES (TG_TABLE_NAME, TG_OP, row_to_json(OLD), row_to_json(NEW), NOW());
        RETURN NEW;
    END IF;
END;
$$;

-- Audit log table
CREATE TABLE IF NOT EXISTS audit.log (
    id          BIGSERIAL PRIMARY KEY,
    table_name  TEXT        NOT NULL,
    operation   TEXT        NOT NULL,  -- INSERT | UPDATE | DELETE
    old_data    JSONB,
    new_data    JSONB,
    changed_by  TEXT        DEFAULT current_user,
    changed_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_log_table   ON audit.log(table_name);
CREATE INDEX IF NOT EXISTS idx_audit_log_changed ON audit.log(changed_at DESC);

-- ---------------------------------------------------------------------------
-- Create auxiliary databases (MLflow + Airflow)
-- Must be outside a transaction block — run as separate statements
-- ---------------------------------------------------------------------------
SELECT 'CREATE DATABASE navam_mlflow OWNER navam'
WHERE NOT EXISTS (
    SELECT FROM pg_database WHERE datname = 'navam_mlflow'
)\gexec

SELECT 'CREATE DATABASE navam_airflow OWNER navam'
WHERE NOT EXISTS (
    SELECT FROM pg_database WHERE datname = 'navam_airflow'
)\gexec

-- ---------------------------------------------------------------------------
-- Grant privileges
-- ---------------------------------------------------------------------------
GRANT ALL PRIVILEGES ON DATABASE navam        TO navam;
GRANT ALL PRIVILEGES ON SCHEMA navam          TO navam;
GRANT ALL PRIVILEGES ON SCHEMA audit          TO navam;
GRANT ALL PRIVILEGES ON SCHEMA ml             TO navam;
GRANT ALL PRIVILEGES ON ALL TABLES    IN SCHEMA navam TO navam;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA navam TO navam;

-- ---------------------------------------------------------------------------
-- Placeholder tables (populated by Alembic migrations)
-- These exist so Martin can auto-publish them even before migrations run.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS navam.habitations (
    id              UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    lgd_code        TEXT        UNIQUE NOT NULL,
    name            TEXT        NOT NULL,
    district        TEXT        NOT NULL,
    state           TEXT        NOT NULL DEFAULT 'Uttarakhand',
    population      INTEGER,
    households      INTEGER,
    geom            GEOMETRY(Point, 4326),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS navam.safe_sites (
    id              UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    name            TEXT        NOT NULL,
    site_type       TEXT        NOT NULL,  -- RELIEF_CAMP | STAGING_AREA | HELIPAD
    capacity        INTEGER,
    district        TEXT        NOT NULL,
    state           TEXT        NOT NULL DEFAULT 'Uttarakhand',
    geom            GEOMETRY(Point, 4326),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Spatial indexes
CREATE INDEX IF NOT EXISTS idx_habitations_geom  ON navam.habitations  USING GIST(geom);
CREATE INDEX IF NOT EXISTS idx_safe_sites_geom   ON navam.safe_sites   USING GIST(geom);
CREATE INDEX IF NOT EXISTS idx_habitations_lgd   ON navam.habitations  (lgd_code);
CREATE INDEX IF NOT EXISTS idx_habitations_dist  ON navam.habitations  (district);

COMMENT ON TABLE navam.habitations IS 'LGD-coded habitations with risk scores and population data';
COMMENT ON TABLE navam.safe_sites  IS 'Pre-identified safe evacuation and relief sites';
