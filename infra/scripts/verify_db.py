#!/usr/bin/env python3
"""infra/scripts/verify_db.py
NAVAM — Database verification script.

Connects to PostgreSQL and runs a suite of checks to verify the schema,
data integrity, spatial indexes, and WORM trigger correctness.

Requirements:
    pip install psycopg2-binary

Usage:
    export DATABASE_URL="postgresql://navam:navam_dev_secret@localhost:5432/navam"
    python verify_db.py

Exit codes:
    0 — All checks passed
    1 — One or more checks failed
"""

from __future__ import annotations

import os
import sys
import traceback
from typing import Any, Callable

import psycopg2
import psycopg2.extras

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DATABASE_URL: str = os.environ.get(
    "DATABASE_URL",
    "postgresql://navam:navam_dev_secret@localhost:5432/navam",
)

# ANSI colours for terminal output
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
RESET  = "\033[0m"
BOLD   = "\033[1m"


# ---------------------------------------------------------------------------
# Check runner
# ---------------------------------------------------------------------------
class CheckResult:
    def __init__(self, name: str) -> None:
        self.name    = name
        self.passed  = False
        self.detail  = ""
        self.skipped = False


_results: list[CheckResult] = []


def check(name: str, fn: Callable[[], tuple[bool, str]]) -> CheckResult:
    """Run a single named check and record the result."""
    cr = CheckResult(name)
    try:
        passed, detail = fn()
        cr.passed = passed
        cr.detail = detail
    except Exception as exc:
        cr.passed = False
        cr.detail = f"EXCEPTION: {exc}\n{traceback.format_exc()}"
    _results.append(cr)

    symbol = f"{GREEN}✓ PASS{RESET}" if cr.passed else f"{RED}✗ FAIL{RESET}"
    print(f"  {symbol}  {name}")
    if not cr.passed:
        for line in cr.detail.splitlines():
            print(f"         {YELLOW}{line}{RESET}")
    return cr


def skip(name: str, reason: str) -> CheckResult:
    cr = CheckResult(name)
    cr.skipped = True
    cr.detail  = reason
    _results.append(cr)
    print(f"  {YELLOW}⊘ SKIP{RESET}  {name}  ({reason})")
    return cr


# ===========================================================================
# CHECKS
# ===========================================================================

def check_schemas(conn: psycopg2.extensions.connection) -> tuple[bool, str]:
    with conn.cursor() as cur:
        cur.execute("""
            SELECT schema_name FROM information_schema.schemata
            WHERE schema_name IN ('navam', 'audit')
            ORDER BY schema_name;
        """)
        found = {r[0] for r in cur.fetchall()}
        missing = {"navam", "audit"} - found
        if missing:
            return False, f"Missing schemas: {missing}"
        return True, "Schemas: navam, audit"


def check_extensions(conn: psycopg2.extensions.connection) -> tuple[bool, str]:
    with conn.cursor() as cur:
        cur.execute("""
            SELECT extname FROM pg_extension
            WHERE extname IN ('uuid-ossp', 'postgis', 'btree_gist')
            ORDER BY extname;
        """)
        found = {r[0] for r in cur.fetchall()}
        required = {"uuid-ossp", "postgis", "btree_gist"}
        missing = required - found
        if missing:
            return False, f"Missing extensions: {missing}"
        return True, f"Extensions present: {found}"


def check_tables(conn: psycopg2.extensions.connection) -> tuple[bool, str]:
    with conn.cursor() as cur:
        cur.execute("""
            SELECT table_schema || '.' || table_name AS tbl
            FROM information_schema.tables
            WHERE table_schema IN ('navam', 'audit')
              AND table_type = 'BASE TABLE'
            ORDER BY tbl;
        """)
        found = {r[0] for r in cur.fetchall()}
        required = {
            "navam.habitations",
            "navam.data_sources",
            "navam.policy_configs",
            "navam.hazard_scores",
            "navam.priority_scores",
            "navam.safe_sites",
            "navam.site_capacity_assessments",
            "navam.relocation_plans",
            "navam.relocation_decisions",
            "navam.jobs",
            "navam.field_reports",
            "audit.log",
        }
        missing = required - found
        if missing:
            return False, f"Missing tables: {missing}"
        return True, f"All {len(required)} tables present"


def check_row_counts(conn: psycopg2.extensions.connection) -> tuple[bool, str]:
    tables = {
        "navam.habitations":               0,
        "navam.data_sources":              0,
        "navam.policy_configs":            0,
        "navam.hazard_scores":             0,
        "navam.priority_scores":           0,
        "navam.safe_sites":                0,
        "navam.site_capacity_assessments": 0,
    }
    lines = []
    any_seeded = False
    with conn.cursor() as cur:
        for tbl in tables:
            cur.execute(f"SELECT COUNT(*) FROM {tbl};")
            cnt = cur.fetchone()[0]
            lines.append(f"{tbl}: {cnt}")
            if cnt > 0:
                any_seeded = True
    return any_seeded, "\n".join(lines)


def check_habitation_count(conn: psycopg2.extensions.connection) -> tuple[bool, str]:
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM navam.habitations WHERE data_source='SYNTHETIC';")
        cnt = cur.fetchone()[0]
        if cnt == 0:
            return False, "No synthetic habitations found — run seed_data.py first."
        if cnt < 400:
            return False, f"Only {cnt} habitations found; expected ~500."
        return True, f"{cnt} synthetic habitations present"


def check_spatial_index_habitations(conn: psycopg2.extensions.connection) -> tuple[bool, str]:
    with conn.cursor() as cur:
        cur.execute("""
            SELECT indexname FROM pg_indexes
            WHERE tablename = 'habitations'
              AND schemaname = 'navam'
              AND indexdef ILIKE '%gist%';
        """)
        rows = [r[0] for r in cur.fetchall()]
        if not rows:
            return False, "No GIST indexes found on navam.habitations"
        return True, f"GIST indexes on habitations: {rows}"


def check_spatial_index_safe_sites(conn: psycopg2.extensions.connection) -> tuple[bool, str]:
    with conn.cursor() as cur:
        cur.execute("""
            SELECT indexname FROM pg_indexes
            WHERE tablename = 'safe_sites'
              AND schemaname = 'navam'
              AND indexdef ILIKE '%gist%';
        """)
        rows = [r[0] for r in cur.fetchall()]
        if not rows:
            return False, "No GIST indexes found on navam.safe_sites"
        return True, f"GIST indexes on safe_sites: {rows}"


def check_all_indexes(conn: psycopg2.extensions.connection) -> tuple[bool, str]:
    with conn.cursor() as cur:
        cur.execute("""
            SELECT indexname FROM pg_indexes
            WHERE schemaname IN ('navam', 'audit')
            ORDER BY indexname;
        """)
        rows = [r[0] for r in cur.fetchall()]
        if len(rows) < 10:
            return False, f"Only {len(rows)} indexes found — schema may be incomplete."
        return True, f"{len(rows)} indexes present"


def check_postgis_geometry(conn: psycopg2.extensions.connection) -> tuple[bool, str]:
    """Verify that centroid geometry is valid EPSG:4326."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*) FROM navam.habitations
            WHERE ST_IsValid(centroid::geometry) = FALSE;
        """)
        invalid = cur.fetchone()[0]
        if invalid > 0:
            return False, f"{invalid} habitations have invalid geometry."

        cur.execute("""
            SELECT COUNT(*) FROM navam.habitations
            WHERE ST_SRID(centroid::geometry) != 4326;
        """)
        wrong_srid = cur.fetchone()[0]
        if wrong_srid > 0:
            return False, f"{wrong_srid} habitations have incorrect SRID (expected 4326)."

        cur.execute("""
            SELECT COUNT(*) FROM navam.habitations
            WHERE ST_Y(centroid::geometry) NOT BETWEEN 30.0 AND 30.8
               OR ST_X(centroid::geometry) NOT BETWEEN 79.0 AND 80.2;
        """)
        out_of_bounds = cur.fetchone()[0]
        if out_of_bounds > 0:
            return False, f"{out_of_bounds} habitations fall outside Chamoli geographic bounds."

        cur.execute("SELECT COUNT(*) FROM navam.habitations;")
        total = cur.fetchone()[0]
        return True, f"All {total} habitations have valid EPSG:4326 geometry within Chamoli bounds"


def check_triggers_exist(conn: psycopg2.extensions.connection) -> tuple[bool, str]:
    with conn.cursor() as cur:
        cur.execute("""
            SELECT trigger_name FROM information_schema.triggers
            WHERE trigger_schema IN ('navam', 'audit')
            ORDER BY trigger_name;
        """)
        found = {r[0] for r in cur.fetchall()}
        required = {
            "trg_decisions_immutable_update",
            "trg_decisions_immutable_delete",
            "trg_audit_immutable_update",
            "trg_audit_immutable_delete",
            "trg_habitations_updated_at",
            "trg_safe_sites_updated_at",
            "trg_relocation_plans_updated_at",
        }
        missing = required - found
        if missing:
            return False, f"Missing triggers: {missing}"
        return True, f"All {len(required)} required triggers present"


def check_worm_decision_update(conn: psycopg2.extensions.connection) -> tuple[bool, str]:
    """
    Verify that UPDATE on relocation_decisions raises restrict_violation.
    Inserts a temporary test row (via a throwaway plan + habitation lookup),
    attempts UPDATE, expects failure, then cleans up.
    """
    with conn.cursor() as cur:
        # We need a real habitation_id and safe_site_id for FK constraints
        cur.execute("SELECT id FROM navam.habitations LIMIT 1;")
        hab_row = cur.fetchone()
        cur.execute("SELECT id FROM navam.safe_sites LIMIT 1;")
        site_row = cur.fetchone()

        if not hab_row or not site_row:
            return False, "Cannot test WORM: no habitations or safe_sites seeded yet."

        hab_id  = hab_row[0]
        site_id = site_row[0]

        # Insert a plan first
        cur.execute("""
            INSERT INTO navam.relocation_plans (plan_name, district_code, created_by)
            VALUES ('_VERIFY_TEST_PLAN', '05016', 'verify_script')
            RETURNING id;
        """)
        plan_id = cur.fetchone()[0]

        # Insert a decision
        cur.execute("""
            INSERT INTO navam.relocation_decisions (
                plan_id, habitation_id, target_site_id,
                decision_type, decision_by_user_id, decision_by_role, population_affected
            ) VALUES (%s, %s, %s, 'DEFER', 'verify_script', 'SYSTEM', 0)
            RETURNING id;
        """, (plan_id, hab_id, site_id))
        decision_id = cur.fetchone()[0]

        worm_blocked = False
        try:
            cur.execute("""
                UPDATE navam.relocation_decisions
                SET notes = 'attempted mutation'
                WHERE id = %s;
            """, (decision_id,))
        except psycopg2.errors.RestrictViolation:
            worm_blocked = True
            conn.rollback()   # rollback the failed UPDATE

        if not worm_blocked:
            # Clean up the test row (trigger did NOT fire — fail)
            conn.rollback()
            return False, "WORM trigger did NOT block UPDATE on relocation_decisions!"

        # Now test DELETE
        delete_blocked = False
        try:
            cur.execute("""
                DELETE FROM navam.relocation_decisions WHERE id = %s;
            """, (decision_id,))
        except psycopg2.errors.RestrictViolation:
            delete_blocked = True
            conn.rollback()

        if not delete_blocked:
            conn.rollback()
            return False, "WORM trigger did NOT block DELETE on relocation_decisions!"

        # Clean up the inserted test rows (rollback the whole savepoint)
        conn.rollback()
        return True, "WORM triggers correctly blocked UPDATE and DELETE on relocation_decisions"


def check_worm_audit_log(conn: psycopg2.extensions.connection) -> tuple[bool, str]:
    """Verify that UPDATE / DELETE on audit.log are blocked."""
    with conn.cursor() as cur:
        # Insert a test audit log entry
        cur.execute("""
            INSERT INTO audit.log (user_id, action, resource_type)
            VALUES ('verify_script', 'VERIFY_WORM_TEST', 'TEST')
            RETURNING id;
        """)
        log_id = cur.fetchone()[0]

        update_blocked = False
        try:
            cur.execute("""
                UPDATE audit.log SET action = 'MUTATED' WHERE id = %s;
            """, (log_id,))
        except psycopg2.errors.RestrictViolation:
            update_blocked = True
            conn.rollback()

        if not update_blocked:
            conn.rollback()
            return False, "WORM trigger did NOT block UPDATE on audit.log!"

        delete_blocked = False
        try:
            cur.execute("""
                DELETE FROM audit.log WHERE id = %s;
            """, (log_id,))
        except psycopg2.errors.RestrictViolation:
            delete_blocked = True
            conn.rollback()

        if not delete_blocked:
            conn.rollback()
            return False, "WORM trigger did NOT block DELETE on audit.log!"

        conn.rollback()
        return True, "WORM triggers correctly blocked UPDATE and DELETE on audit.log"


def check_updated_at_trigger(conn: psycopg2.extensions.connection) -> tuple[bool, str]:
    """Verify that updated_at is auto-updated on navam.habitations."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id, updated_at FROM navam.habitations
            WHERE data_source = 'SYNTHETIC'
            LIMIT 1;
        """)
        row = cur.fetchone()
        if not row:
            return False, "No synthetic habitations found to test updated_at trigger."

        hab_id, old_ts = row[0], row[1]

        # Force a small sleep to guarantee timestamp difference
        import time
        time.sleep(0.01)

        cur.execute("""
            UPDATE navam.habitations
            SET village_name = village_name || ''
            WHERE id = %s
            RETURNING updated_at;
        """, (hab_id,))
        new_ts = cur.fetchone()[0]
        conn.rollback()  # Don't leave a dirty update

        if new_ts <= old_ts:
            return False, f"updated_at was NOT updated: old={old_ts}, new={new_ts}"
        return True, f"updated_at trigger works correctly (old={old_ts}, new={new_ts})"


def check_hazard_score_range(conn: psycopg2.extensions.connection) -> tuple[bool, str]:
    with conn.cursor() as cur:
        cur.execute("""
            SELECT COUNT(*) FROM navam.hazard_scores
            WHERE score < 0 OR score > 100;
        """)
        out_of_range = cur.fetchone()[0]
        if out_of_range > 0:
            return False, f"{out_of_range} hazard scores outside [0, 100] range."

        cur.execute("""
            SELECT hazard_type, COUNT(*), ROUND(AVG(score),2), ROUND(MIN(score),2), ROUND(MAX(score),2)
            FROM navam.hazard_scores
            GROUP BY hazard_type
            ORDER BY hazard_type;
        """)
        stats = cur.fetchall()
        detail = "Score statistics:\n" + "\n".join(
            f"  {r[0]:12s}: count={r[1]:4d}, avg={r[2]:5.1f}, min={r[3]:5.1f}, max={r[4]:5.1f}"
            for r in stats
        )
        return True, detail


def check_priority_tier_distribution(conn: psycopg2.extensions.connection) -> tuple[bool, str]:
    with conn.cursor() as cur:
        cur.execute("""
            SELECT priority_tier, COUNT(*), ROUND(AVG(score),2)
            FROM navam.priority_scores
            GROUP BY priority_tier
            ORDER BY priority_tier;
        """)
        rows = cur.fetchall()
        if not rows:
            return False, "No priority scores found."

        total = sum(r[1] for r in rows)
        lines = [f"Priority tier distribution (total={total}):"]
        for row in rows:
            pct = 100 * row[1] / total if total else 0
            lines.append(f"  {row[0]:12s}: {row[1]:4d} ({pct:5.1f}%) — avg_score={row[2]}")
        return True, "\n".join(lines)


def check_fk_integrity(conn: psycopg2.extensions.connection) -> tuple[bool, str]:
    """
    Spot-check FK integrity: hazard_scores → habitations,
    priority_scores → habitations, priority_scores → policy_configs.
    """
    with conn.cursor() as cur:
        checks_passed = []

        cur.execute("""
            SELECT COUNT(*) FROM navam.hazard_scores hs
            LEFT JOIN navam.habitations h ON h.id = hs.habitation_id
            WHERE h.id IS NULL;
        """)
        orphans = cur.fetchone()[0]
        if orphans > 0:
            return False, f"{orphans} orphaned hazard_scores (no matching habitation)."
        checks_passed.append("hazard_scores→habitations FK OK")

        cur.execute("""
            SELECT COUNT(*) FROM navam.priority_scores ps
            LEFT JOIN navam.habitations h ON h.id = ps.habitation_id
            WHERE h.id IS NULL;
        """)
        orphans = cur.fetchone()[0]
        if orphans > 0:
            return False, f"{orphans} orphaned priority_scores (no matching habitation)."
        checks_passed.append("priority_scores→habitations FK OK")

        cur.execute("""
            SELECT COUNT(*) FROM navam.priority_scores ps
            LEFT JOIN navam.policy_configs pc ON pc.id = ps.policy_config_id
            WHERE pc.id IS NULL;
        """)
        orphans = cur.fetchone()[0]
        if orphans > 0:
            return False, f"{orphans} orphaned priority_scores (no matching policy_config)."
        checks_passed.append("priority_scores→policy_configs FK OK")

        return True, "; ".join(checks_passed)


def check_postgis_spatial_query(conn: psycopg2.extensions.connection) -> tuple[bool, str]:
    """Test a real spatial query: find habitations within 20 km of Gopeshwar."""
    with conn.cursor() as cur:
        # Gopeshwar (district HQ): 30.4084°N, 79.3200°E
        cur.execute("""
            SELECT COUNT(*) FROM navam.habitations
            WHERE ST_DWithin(
                centroid::geography,
                ST_SetSRID(ST_MakePoint(79.3200, 30.4084), 4326)::geography,
                20000  -- 20 km in metres
            );
        """)
        count = cur.fetchone()[0]
        if count == 0:
            return False, "Spatial DWithin query returned 0 results near Gopeshwar — geometry may be malformed."
        return True, f"Spatial DWithin(20 km from Gopeshwar): {count} habitations found"


# ===========================================================================
# MAIN
# ===========================================================================
def main() -> None:
    print(f"\n{BOLD}{CYAN}{'='*60}{RESET}")
    print(f"{BOLD}{CYAN}NAVAM Database Verification — SIH 2026{RESET}")
    print(f"{CYAN}Target: {DATABASE_URL.split('@')[-1]}{RESET}")
    print(f"{CYAN}{'='*60}{RESET}\n")

    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = False
        psycopg2.extras.register_uuid()
    except psycopg2.OperationalError as exc:
        print(f"{RED}FATAL: Cannot connect to database.{RESET}\n{exc}", file=sys.stderr)
        sys.exit(1)

    print(f"{BOLD}── Schema & Extensions ──────────────────────────{RESET}")
    check("PostgreSQL schemas exist (navam, audit)",   lambda: check_schemas(conn))
    check("Required extensions present",               lambda: check_extensions(conn))
    check("All 12 required tables exist",              lambda: check_tables(conn))

    print(f"\n{BOLD}── Row Counts ───────────────────────────────────{RESET}")
    check("Non-empty tables (seeded)",                 lambda: check_row_counts(conn))
    check("~500 synthetic habitations seeded",         lambda: check_habitation_count(conn))

    print(f"\n{BOLD}── Indexes ──────────────────────────────────────{RESET}")
    check("GIST spatial index on habitations.centroid",lambda: check_spatial_index_habitations(conn))
    check("GIST spatial index on safe_sites.centroid", lambda: check_spatial_index_safe_sites(conn))
    check("All operational B-tree indexes present",    lambda: check_all_indexes(conn))

    print(f"\n{BOLD}── Geometry & Spatial ───────────────────────────{RESET}")
    check("All habitation geometries valid EPSG:4326", lambda: check_postgis_geometry(conn))
    check("Spatial DWithin query near Gopeshwar",      lambda: check_postgis_spatial_query(conn))

    print(f"\n{BOLD}── Triggers ─────────────────────────────────────{RESET}")
    check("All 7 required triggers exist",             lambda: check_triggers_exist(conn))
    check("WORM: relocation_decisions UPDATE/DELETE blocked", lambda: check_worm_decision_update(conn))
    check("WORM: audit.log UPDATE/DELETE blocked",     lambda: check_worm_audit_log(conn))
    check("updated_at auto-update trigger works",      lambda: check_updated_at_trigger(conn))

    print(f"\n{BOLD}── Data Quality ─────────────────────────────────{RESET}")
    check("Hazard scores in [0, 100] range",           lambda: check_hazard_score_range(conn))
    check("Priority tier distribution",                lambda: check_priority_tier_distribution(conn))
    check("Foreign key integrity",                     lambda: check_fk_integrity(conn))

    conn.close()

    # -----------------------------------------------------------------------
    # Final summary
    # -----------------------------------------------------------------------
    total   = len(_results)
    passed  = sum(1 for r in _results if r.passed)
    failed  = sum(1 for r in _results if not r.passed and not r.skipped)
    skipped = sum(1 for r in _results if r.skipped)

    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}Results: {passed}/{total} passed", end="")
    if skipped:
        print(f"  ({skipped} skipped)", end="")
    print(RESET)

    if failed == 0:
        print(f"{GREEN}{BOLD}✓ ALL CHECKS PASSED — database is correctly configured.{RESET}")
        sys.exit(0)
    else:
        print(f"{RED}{BOLD}✗ {failed} CHECK(S) FAILED — review output above.{RESET}")
        sys.exit(1)


if __name__ == "__main__":
    main()
