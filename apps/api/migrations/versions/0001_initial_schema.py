"""migrations/versions/0001_initial_schema.py
NAVAM — Initial database schema migration
PostgreSQL 16 + PostGIS 3.4

Creates:
  Schemas  : navam, audit
  Extensions: uuid-ossp, postgis, btree_gist
  Tables   : habitations, data_sources, policy_configs, hazard_scores,
             priority_scores, safe_sites, site_capacity_assessments,
             relocation_plans, relocation_decisions, jobs, field_reports,
             audit.log
  Triggers : WORM immutability (relocation_decisions, audit.log),
             updated_at auto-update (habitations, safe_sites, relocation_plans)
  Indexes  : GIST spatial, B-tree operational
"""

from __future__ import annotations

from alembic import op

# ---------------------------------------------------------------------------
# Alembic revision metadata
# ---------------------------------------------------------------------------
revision: str = "0001"
down_revision: str | None = None
branch_labels: str | tuple[str, ...] | None = None
depends_on: str | tuple[str, ...] | None = None


# ===========================================================================
# UPGRADE
# ===========================================================================
def upgrade() -> None:

    # -----------------------------------------------------------------------
    # 1. Extensions & Schemas
    # -----------------------------------------------------------------------
    op.execute("""
        -- Enable UUID generation (uuid_generate_v4)
        CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

        -- Enable PostGIS (geometry, geography types + spatial functions)
        CREATE EXTENSION IF NOT EXISTS postgis;

        -- Enable GiST index support for range/exclusion constraints
        CREATE EXTENSION IF NOT EXISTS btree_gist;

        -- Application schema
        CREATE SCHEMA IF NOT EXISTS navam;

        -- Immutable audit schema (separate from application data)
        CREATE SCHEMA IF NOT EXISTS audit;
    """)

    # -----------------------------------------------------------------------
    # 2. Table: navam.habitations
    #    Core reference table — one row per revenue village / habitation.
    #    Geometry stored in EPSG:4326 (WGS-84).
    # -----------------------------------------------------------------------
    op.execute("""
        CREATE TABLE IF NOT EXISTS navam.habitations (
            id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            lgd_village_code    VARCHAR(11)  UNIQUE NOT NULL,
            lgd_block_code      VARCHAR(7)   NOT NULL,
            lgd_district_code   VARCHAR(5)   NOT NULL,   -- '05016' = Chamoli
            lgd_state_code      VARCHAR(3)   NOT NULL,   -- '05'    = Uttarakhand
            village_name        VARCHAR(255) NOT NULL,
            village_name_hi     VARCHAR(255),             -- Devanagari name
            block_name          VARCHAR(255),
            district_name       VARCHAR(255),
            state_name          VARCHAR(255),
            centroid            GEOMETRY(POINT, 4326) NOT NULL,
            boundary            GEOMETRY(MULTIPOLYGON, 4326),
            elevation_m         NUMERIC(8,2),
            area_sqkm           NUMERIC(10,4),
            population_total    INTEGER,
            population_sc       INTEGER,
            population_st       INTEGER,
            households          INTEGER,
            literacy_rate       NUMERIC(5,2),
            elderly_pct         NUMERIC(5,2),             -- % aged 60+
            female_pct          NUMERIC(5,2),
            housing_pucca_pct   NUMERIC(5,2),
            data_source         VARCHAR(50)  NOT NULL DEFAULT 'SYNTHETIC',
            source_year         INTEGER      DEFAULT 2011,
            created_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
            updated_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
            is_active           BOOLEAN      NOT NULL DEFAULT TRUE
        );
    """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_habitations_centroid  ON navam.habitations USING GIST(centroid);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_habitations_boundary  ON navam.habitations USING GIST(boundary);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_habitations_district  ON navam.habitations(lgd_district_code);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_habitations_block     ON navam.habitations(lgd_block_code);")

    # -----------------------------------------------------------------------
    # 3. Table: navam.data_sources
    #    Provenance catalogue for every ingested dataset.
    # -----------------------------------------------------------------------
    op.execute("""
        CREATE TABLE IF NOT EXISTS navam.data_sources (
            id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            source_system       VARCHAR(100)  NOT NULL,  -- 'IMD', 'CWC', 'GSI', 'SYNTHETIC'
            source_dataset      VARCHAR(255)  NOT NULL,
            source_uri          TEXT,
            source_version      VARCHAR(100),
            source_timestamp    TIMESTAMPTZ,
            ingested_at         TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
            transform_version   VARCHAR(64),             -- git commit SHA of ETL code
            quality_flags       JSONB,
            -- example: {"null_rate": 0.02, "out_of_range_count": 5, "spatial_validity": true}
            record_count        INTEGER,
            notes               TEXT
        );
    """)

    # -----------------------------------------------------------------------
    # 4. Table: navam.policy_configs
    #    Versioned, audited weight configurations for the scoring engine.
    # -----------------------------------------------------------------------
    op.execute("""
        CREATE TABLE IF NOT EXISTS navam.policy_configs (
            id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            policy_name             VARCHAR(255) NOT NULL,
            version                 INTEGER      NOT NULL DEFAULT 1,
            effective_from          TIMESTAMPTZ  NOT NULL,
            effective_to            TIMESTAMPTZ,
            weights                 JSONB        NOT NULL,
            -- example: {"flood": 0.35, "landslide": 0.30, "erosion": 0.15, "drought": 0.10, "cyclone": 0.10}
            season_weights          JSONB        NOT NULL,
            -- example: {"MONSOON": {"flood": 0.40, ...}, "DRY": {"flood": 0.20, ...}}
            thresholds              JSONB        NOT NULL,
            -- example: {"IMMEDIATE": 80, "SHORT_TERM": 60, "MEDIUM_TERM": 40}
            vulnerability_weights   JSONB        NOT NULL,
            -- example: {"elderly_pct": 0.3, "sc_st_pct": 0.25, "literacy_inverse": 0.25, "housing_kutcha": 0.2}
            overrides               JSONB,
            author_id               VARCHAR(255) NOT NULL,
            approver_id             VARCHAR(255),
            change_reason           TEXT,
            git_commit_sha          VARCHAR(64),
            is_active               BOOLEAN      NOT NULL DEFAULT FALSE,
            created_at              TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
            UNIQUE(policy_name, version)
        );
    """)

    # -----------------------------------------------------------------------
    # 5. Table: navam.hazard_scores
    #    Time-stamped hazard scores per habitation per hazard type.
    # -----------------------------------------------------------------------
    op.execute("""
        CREATE TABLE IF NOT EXISTS navam.hazard_scores (
            id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            habitation_id       UUID        NOT NULL REFERENCES navam.habitations(id) ON DELETE RESTRICT,
            hazard_type         VARCHAR(50) NOT NULL,  -- 'FLOOD','LANDSLIDE','EROSION','DROUGHT','CYCLONE'
            score               NUMERIC(5,2) NOT NULL CHECK (score >= 0 AND score <= 100),
            ci_lower_90         NUMERIC(5,2),
            ci_upper_90         NUMERIC(5,2),
            raw_value           NUMERIC(12,4),          -- e.g., flood depth in metres
            raw_unit            VARCHAR(50),
            source_dataset_id   UUID        REFERENCES navam.data_sources(id),
            model_version       VARCHAR(100),
            valid_from          TIMESTAMPTZ NOT NULL,
            valid_to            TIMESTAMPTZ,
            season              VARCHAR(20),            -- 'MONSOON','DRY','ALL'
            data_source         VARCHAR(50) NOT NULL DEFAULT 'SYNTHETIC',
            computed_at         TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
    """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_hazard_scores_habitation ON navam.hazard_scores(habitation_id);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_hazard_scores_type       ON navam.hazard_scores(hazard_type);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_hazard_scores_valid      ON navam.hazard_scores(valid_from, valid_to);")

    # -----------------------------------------------------------------------
    # 6. Table: navam.priority_scores
    #    Composite risk + vulnerability scores, one row per habitation per run.
    # -----------------------------------------------------------------------
    op.execute("""
        CREATE TABLE IF NOT EXISTS navam.priority_scores (
            id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            habitation_id           UUID         NOT NULL REFERENCES navam.habitations(id) ON DELETE RESTRICT,
            policy_config_id        UUID         NOT NULL REFERENCES navam.policy_configs(id),
            score                   NUMERIC(5,2) NOT NULL CHECK (score >= 0 AND score <= 100),
            ci_lower_90             NUMERIC(5,2),
            ci_upper_90             NUMERIC(5,2),
            priority_tier           VARCHAR(20)  NOT NULL,  -- 'IMMEDIATE','SHORT_TERM','MEDIUM_TERM','MONITOR'
            national_rank           INTEGER,
            district_rank           INTEGER,
            score_breakdown         JSONB        NOT NULL,
            -- example: {"flood_contribution": 32.4, "landslide_contribution": 28.1, "vulnerability": 15.2}
            shap_values             JSONB,
            -- example: [{"feature": "landslide_score", "shap_value": 12.3, "feature_value": 0.87}]
            joint_hazard_probability NUMERIC(8,6),          -- Copula: P(flood AND landslide)
            season                  VARCHAR(20),
            computed_at             TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
            job_id                  UUID
        );
    """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_priority_scores_habitation ON navam.priority_scores(habitation_id);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_priority_scores_score      ON navam.priority_scores(score DESC);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_priority_scores_tier       ON navam.priority_scores(priority_tier);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_priority_scores_computed   ON navam.priority_scores(computed_at DESC);")

    # -----------------------------------------------------------------------
    # 7. Table: navam.safe_sites
    #    Potential relocation target sites — geological & infrastructure data.
    # -----------------------------------------------------------------------
    op.execute("""
        CREATE TABLE IF NOT EXISTS navam.safe_sites (
            id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            site_code               VARCHAR(50)  UNIQUE NOT NULL,
            site_name               VARCHAR(255) NOT NULL,
            site_name_hi            VARCHAR(255),
            centroid                GEOMETRY(POINT, 4326)        NOT NULL,
            boundary                GEOMETRY(MULTIPOLYGON, 4326),
            area_sqkm               NUMERIC(10,4),
            lgd_district_code       VARCHAR(5)   NOT NULL,
            lgd_block_code          VARCHAR(7),
            max_theoretical_capacity INTEGER,                    -- derived from area
            elevation_m             NUMERIC(8,2),
            hazard_free_verified    BOOLEAN      DEFAULT FALSE,
            road_access             BOOLEAN,
            nearest_road_dist_km    NUMERIC(8,3),
            water_source_type       VARCHAR(100),                -- 'RIVER','BOREWELL','NONE'
            water_yield_lpd         INTEGER,                     -- litres per day
            site_type               VARCHAR(50),                 -- 'GOVERNMENT_LAND','FOREST','PRIVATE','CAMP'
            current_status          VARCHAR(50)  DEFAULT 'AVAILABLE',  -- 'AVAILABLE','PARTIALLY_USED','FULL'
            data_source             VARCHAR(50)  NOT NULL DEFAULT 'SYNTHETIC',
            source_dataset_id       UUID         REFERENCES navam.data_sources(id),
            notes                   TEXT,
            created_at              TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
            updated_at              TIMESTAMPTZ  NOT NULL DEFAULT NOW()
        );
    """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_safe_sites_centroid  ON navam.safe_sites USING GIST(centroid);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_safe_sites_district  ON navam.safe_sites(lgd_district_code);")

    # -----------------------------------------------------------------------
    # 8. Table: navam.site_capacity_assessments
    #    Quantitative capacity analysis (land, water, infrastructure).
    # -----------------------------------------------------------------------
    op.execute("""
        CREATE TABLE IF NOT EXISTS navam.site_capacity_assessments (
            id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            safe_site_id            UUID    NOT NULL REFERENCES navam.safe_sites(id) ON DELETE RESTRICT,
            assessment_date         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            land_capacity           INTEGER NOT NULL,     -- persons from area × density factor
            water_capacity          INTEGER NOT NULL,     -- persons from water_yield_lpd / 45 lpd/person
            infrastructure_capacity INTEGER NOT NULL,     -- persons: road_access + power availability
            practical_capacity      INTEGER NOT NULL,     -- MIN(land, water, infrastructure)
            capacity_breakdown      JSONB   NOT NULL,
            -- example: {"land_sqm": 12000, "persons_per_sqm": 0.5, "water_lpd": 45000, "lpd_per_person": 45}
            sensitivity_low         INTEGER,              -- practical at -20% water+infra
            sensitivity_high        INTEGER,              -- practical at +20%
            assessed_by             VARCHAR(255),
            assessment_method       VARCHAR(50) DEFAULT 'ALGORITHMIC',  -- 'ALGORITHMIC','FIELD','COMBINED'
            notes                   TEXT
        );
    """)

    # -----------------------------------------------------------------------
    # 9. Table: navam.relocation_plans
    #    Top-level container grouping relocation decisions for a district run.
    # -----------------------------------------------------------------------
    op.execute("""
        CREATE TABLE IF NOT EXISTS navam.relocation_plans (
            id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            plan_name           VARCHAR(255) NOT NULL,
            district_code       VARCHAR(5)   NOT NULL,
            policy_config_id    UUID         REFERENCES navam.policy_configs(id),
            status              VARCHAR(50)  NOT NULL DEFAULT 'DRAFT',
            -- 'DRAFT','APPROVED','IN_PROGRESS','COMPLETED','CANCELLED'
            total_habitations   INTEGER,
            total_population    INTEGER,
            created_by          VARCHAR(255) NOT NULL,
            approved_by         VARCHAR(255),
            approved_at         TIMESTAMPTZ,
            created_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
            updated_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW()
        );
    """)

    # -----------------------------------------------------------------------
    # 10. Table: navam.relocation_decisions  (IMMUTABLE — insert-only / WORM)
    #     Authoritative record of each human relocation decision.
    #     Triggers (below) block UPDATE and DELETE.
    # -----------------------------------------------------------------------
    op.execute("""
        CREATE TABLE IF NOT EXISTS navam.relocation_decisions (
            id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            plan_id             UUID         REFERENCES navam.relocation_plans(id),
            habitation_id       UUID         NOT NULL REFERENCES navam.habitations(id) ON DELETE RESTRICT,
            target_site_id      UUID         NOT NULL REFERENCES navam.safe_sites(id)  ON DELETE RESTRICT,
            priority_score_id   UUID         REFERENCES navam.priority_scores(id),
            decision_type       VARCHAR(50)  NOT NULL,  -- 'APPROVE_RELOCATION','DEFER','OVERRIDE_REJECT'
            decision_by_user_id VARCHAR(255) NOT NULL,
            decision_by_role    VARCHAR(50)  NOT NULL,
            decision_at         TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
            population_affected INTEGER,
            notes               TEXT,
            override_reason     TEXT,          -- mandatory when decision_type = 'OVERRIDE_REJECT'
            ip_address          INET,
            user_agent          TEXT
        );
    """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_decisions_habitation ON navam.relocation_decisions(habitation_id);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_decisions_plan       ON navam.relocation_decisions(plan_id);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_decisions_at         ON navam.relocation_decisions(decision_at DESC);")

    # -----------------------------------------------------------------------
    # 11. Table: audit.log  (IMMUTABLE — insert-only)
    #     BIGSERIAL primary key for efficient append-only writes.
    #     Triggers (below) block UPDATE and DELETE.
    # -----------------------------------------------------------------------
    op.execute("""
        CREATE TABLE IF NOT EXISTS audit.log (
            id              BIGSERIAL    PRIMARY KEY,
            event_at        TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
            user_id         VARCHAR(255),
            user_role       VARCHAR(50),
            action          VARCHAR(100) NOT NULL,  -- 'READ_PRIORITY_SCORES','WRITE_DECISION',...
            resource_type   VARCHAR(100),
            resource_id     UUID,
            district_code   VARCHAR(5),
            ip_address      INET,
            user_agent      TEXT,
            query_params    JSONB,
            response_hash   VARCHAR(64),            -- SHA-256 of response body
            correlation_id  UUID,
            duration_ms     INTEGER
        );
    """)
    op.execute("CREATE INDEX IF NOT EXISTS idx_audit_log_at       ON audit.log(event_at DESC);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_audit_log_user     ON audit.log(user_id);")
    op.execute("CREATE INDEX IF NOT EXISTS idx_audit_log_resource ON audit.log(resource_type, resource_id);")

    # -----------------------------------------------------------------------
    # 12. Table: navam.jobs
    #     Background scoring/compute job tracker (Celery task metadata).
    # -----------------------------------------------------------------------
    op.execute("""
        CREATE TABLE IF NOT EXISTS navam.jobs (
            id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            job_type        VARCHAR(100) NOT NULL,  -- 'DISTRICT_RECOMPUTE','NATIONAL_RECOMPUTE'
            status          VARCHAR(50)  NOT NULL DEFAULT 'PENDING',
            -- 'PENDING','RUNNING','COMPLETED','FAILED'
            scope           VARCHAR(50),             -- 'DISTRICT','STATE','NATIONAL'
            district_code   VARCHAR(5),
            progress_pct    INTEGER      DEFAULT 0,
            requested_by    VARCHAR(255),
            weights_override JSONB,
            started_at      TIMESTAMPTZ,
            completed_at    TIMESTAMPTZ,
            result_summary  JSONB,
            error_message   TEXT,
            created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
        );
    """)

    # -----------------------------------------------------------------------
    # 13. Table: navam.field_reports
    #     Ground-truth observations submitted by field officers.
    # -----------------------------------------------------------------------
    op.execute("""
        CREATE TABLE IF NOT EXISTS navam.field_reports (
            id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            habitation_id       UUID        NOT NULL REFERENCES navam.habitations(id) ON DELETE RESTRICT,
            reported_by_user_id VARCHAR(255) NOT NULL,
            reported_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            visit_date          DATE        NOT NULL,
            observation_text    TEXT        NOT NULL,
            hazard_observations JSONB,
            photo_urls          JSONB,       -- array of presigned S3 URLs
            gps_lat             NUMERIC(10,7),
            gps_lon             NUMERIC(10,7),
            verified            BOOLEAN     DEFAULT FALSE,
            verified_by         VARCHAR(255),
            verified_at         TIMESTAMPTZ
        );
    """)

    # -----------------------------------------------------------------------
    # 14. WORM Trigger: navam.relocation_decisions — block UPDATE and DELETE
    # -----------------------------------------------------------------------
    op.execute("""
        CREATE OR REPLACE FUNCTION navam.prevent_decision_mutation()
        RETURNS TRIGGER
        LANGUAGE plpgsql
        SECURITY DEFINER
        AS $$
        BEGIN
            RAISE EXCEPTION
                'Relocation decisions are immutable. '
                'Decision ID % cannot be % after creation. '
                'Original decision recorded at: %. '
                'Contact the system administrator if correction is required.',
                OLD.id,
                TG_OP,
                OLD.decision_at
                USING ERRCODE = 'restrict_violation';
            RETURN NULL;
        END;
        $$;
    """)

    op.execute("""
        CREATE TRIGGER trg_decisions_immutable_update
            BEFORE UPDATE ON navam.relocation_decisions
            FOR EACH ROW
            EXECUTE FUNCTION navam.prevent_decision_mutation();
    """)

    op.execute("""
        CREATE TRIGGER trg_decisions_immutable_delete
            BEFORE DELETE ON navam.relocation_decisions
            FOR EACH ROW
            EXECUTE FUNCTION navam.prevent_decision_mutation();
    """)

    # -----------------------------------------------------------------------
    # 15. WORM Trigger: audit.log — block UPDATE and DELETE
    # -----------------------------------------------------------------------
    op.execute("""
        CREATE OR REPLACE FUNCTION audit.prevent_log_mutation()
        RETURNS TRIGGER
        LANGUAGE plpgsql
        SECURITY DEFINER
        AS $$
        BEGIN
            RAISE EXCEPTION
                'Audit log is immutable. '
                'Record % cannot be % after creation. '
                'The audit trail is a compliance requirement.',
                OLD.id,
                TG_OP
                USING ERRCODE = 'restrict_violation';
            RETURN NULL;
        END;
        $$;
    """)

    op.execute("""
        CREATE TRIGGER trg_audit_immutable_update
            BEFORE UPDATE ON audit.log
            FOR EACH ROW
            EXECUTE FUNCTION audit.prevent_log_mutation();
    """)

    op.execute("""
        CREATE TRIGGER trg_audit_immutable_delete
            BEFORE DELETE ON audit.log
            FOR EACH ROW
            EXECUTE FUNCTION audit.prevent_log_mutation();
    """)

    # -----------------------------------------------------------------------
    # 16. updated_at auto-update trigger (shared function)
    # -----------------------------------------------------------------------
    op.execute("""
        CREATE OR REPLACE FUNCTION navam.update_updated_at()
        RETURNS TRIGGER
        LANGUAGE plpgsql
        AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$;
    """)

    # Apply to tables that carry updated_at
    for tbl in ("habitations", "safe_sites", "relocation_plans"):
        op.execute(f"""
            CREATE TRIGGER trg_{tbl}_updated_at
                BEFORE UPDATE ON navam.{tbl}
                FOR EACH ROW
                EXECUTE FUNCTION navam.update_updated_at();
        """)

    # -----------------------------------------------------------------------
    # 17. Row-level comments (COMMENT ON TABLE) for schema documentation
    # -----------------------------------------------------------------------
    op.execute("COMMENT ON TABLE navam.habitations            IS 'Revenue villages / habitations — master spatial reference layer.';")
    op.execute("COMMENT ON TABLE navam.data_sources           IS 'Data provenance catalogue for all ingested datasets.';")
    op.execute("COMMENT ON TABLE navam.policy_configs         IS 'Versioned hazard-weight configurations, human-approved.';")
    op.execute("COMMENT ON TABLE navam.hazard_scores          IS 'Per-habitation per-hazard scores with confidence intervals.';")
    op.execute("COMMENT ON TABLE navam.priority_scores        IS 'Composite vulnerability+hazard priority scores with SHAP breakdown.';")
    op.execute("COMMENT ON TABLE navam.safe_sites             IS 'Verified relocation target sites with capacity data.';")
    op.execute("COMMENT ON TABLE navam.site_capacity_assessments IS 'Quantitative land/water/infra capacity analysis per site.';")
    op.execute("COMMENT ON TABLE navam.relocation_plans       IS 'District-level relocation planning containers.';")
    op.execute("COMMENT ON TABLE navam.relocation_decisions   IS 'IMMUTABLE: authoritative human relocation decision log (WORM).';")
    op.execute("COMMENT ON TABLE audit.log                    IS 'IMMUTABLE: system-wide action audit trail (WORM).';")
    op.execute("COMMENT ON TABLE navam.jobs                   IS 'Background scoring job tracker.';")
    op.execute("COMMENT ON TABLE navam.field_reports          IS 'Ground-truth field officer observations.';")


# ===========================================================================
# DOWNGRADE — drops all objects in reverse dependency order
# ===========================================================================
def downgrade() -> None:

    # -------
    # Triggers first, then functions, then tables (reverse FK order)
    # -------
    for tbl in ("habitations", "safe_sites", "relocation_plans"):
        op.execute(f"DROP TRIGGER IF EXISTS trg_{tbl}_updated_at ON navam.{tbl};")

    op.execute("DROP TRIGGER IF EXISTS trg_decisions_immutable_update ON navam.relocation_decisions;")
    op.execute("DROP TRIGGER IF EXISTS trg_decisions_immutable_delete ON navam.relocation_decisions;")
    op.execute("DROP TRIGGER IF EXISTS trg_audit_immutable_update     ON audit.log;")
    op.execute("DROP TRIGGER IF EXISTS trg_audit_immutable_delete     ON audit.log;")

    op.execute("DROP FUNCTION IF EXISTS navam.prevent_decision_mutation();")
    op.execute("DROP FUNCTION IF EXISTS audit.prevent_log_mutation();")
    op.execute("DROP FUNCTION IF EXISTS navam.update_updated_at();")

    # Tables — leaf tables first, then parents
    op.execute("DROP TABLE IF EXISTS navam.field_reports                CASCADE;")
    op.execute("DROP TABLE IF EXISTS navam.jobs                         CASCADE;")
    op.execute("DROP TABLE IF EXISTS audit.log                          CASCADE;")
    op.execute("DROP TABLE IF EXISTS navam.relocation_decisions         CASCADE;")
    op.execute("DROP TABLE IF EXISTS navam.relocation_plans             CASCADE;")
    op.execute("DROP TABLE IF EXISTS navam.site_capacity_assessments    CASCADE;")
    op.execute("DROP TABLE IF EXISTS navam.safe_sites                   CASCADE;")
    op.execute("DROP TABLE IF EXISTS navam.priority_scores              CASCADE;")
    op.execute("DROP TABLE IF EXISTS navam.hazard_scores                CASCADE;")
    op.execute("DROP TABLE IF EXISTS navam.policy_configs               CASCADE;")
    op.execute("DROP TABLE IF EXISTS navam.data_sources                 CASCADE;")
    op.execute("DROP TABLE IF EXISTS navam.habitations                  CASCADE;")

    op.execute("DROP SCHEMA IF EXISTS audit  CASCADE;")
    op.execute("DROP SCHEMA IF EXISTS navam  CASCADE;")

    op.execute("DROP EXTENSION IF EXISTS btree_gist;")
    op.execute("DROP EXTENSION IF EXISTS postgis;")
    op.execute("DROP EXTENSION IF EXISTS \"uuid-ossp\";")
