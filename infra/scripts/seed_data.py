#!/usr/bin/env python3
"""infra/scripts/seed_data.py
NAVAM — Synthetic data seeder for SIH 2026 demo.

Populates the database with ~500 synthetic habitations in Chamoli district,
Uttarakhand, along with hazard scores, priority scores, safe sites, and
capacity assessments.

Requirements:
    pip install psycopg2-binary shapely

Usage:
    export DATABASE_URL="postgresql://navam:navam_dev_secret@localhost:5432/navam"
    python seed_data.py

Environment Variables:
    DATABASE_URL    PostgreSQL connection URL (default: postgresql://navam:navam_dev_secret@localhost:5432/navam)
    SEED_COUNT      Number of habitations to generate (default: 500)
    SEED_RESET      If '1', delete existing synthetic data before re-seeding

IMPORTANT: All data is tagged data_source='SYNTHETIC'.
           This is NOT real habitation or hazard data.
"""

from __future__ import annotations

import json
import math
import os
import random
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Load .env from project root
root_env = Path(__file__).resolve().parents[2] / ".env"
if root_env.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(root_env, override=True)
    except ImportError:
        pass

import psycopg2
import psycopg2.extras

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DATABASE_URL: str = os.environ.get(
    "DATABASE_URL",
    "postgresql://navam:navam_dev_secret@localhost:5432/navam",
)
SEED_COUNT: int = int(os.environ.get("SEED_COUNT", "500"))
SEED_RESET: bool = os.environ.get("SEED_RESET", "0") == "1"

# Seed for reproducibility
RANDOM_SEED = 42
random.seed(RANDOM_SEED)

# ---------------------------------------------------------------------------
# Chamoli district geographic bounds (EPSG:4326)
# ---------------------------------------------------------------------------
CHAMOLI_LAT_MIN = 30.10
CHAMOLI_LAT_MAX = 30.65
CHAMOLI_LON_MIN = 79.15
CHAMOLI_LON_MAX = 79.95

DISTRICT_CODE   = "05016"
STATE_CODE       = "05"
DISTRICT_NAME    = "Chamoli"
STATE_NAME       = "Uttarakhand"

# ---------------------------------------------------------------------------
# Real Chamoli blocks
# ---------------------------------------------------------------------------
BLOCKS: list[dict[str, str]] = [
    {"code": "0501601", "name": "Chamoli"},
    {"code": "0501602", "name": "Dasholi"},
    {"code": "0501603", "name": "Gairsain"},
    {"code": "0501604", "name": "Joshimath"},
    {"code": "0501605", "name": "Karnaprayag"},
    {"code": "0501606", "name": "Narayanbadri"},
    {"code": "0501607", "name": "Pokhari"},
    {"code": "0501608", "name": "Tharali"},
    {"code": "0501609", "name": "Dewal"},
]

# Each block carries a rough elevation band (metres) and spatial bias
BLOCK_META: dict[str, dict[str, Any]] = {
    "Chamoli":       {"elev_range": (1400, 2200), "flood_bias": 0.6,  "lat_c": 30.40, "lon_c": 79.32},
    "Dasholi":       {"elev_range": (1600, 2800), "flood_bias": 0.4,  "lat_c": 30.48, "lon_c": 79.40},
    "Gairsain":      {"elev_range": (1200, 1800), "flood_bias": 0.5,  "lat_c": 30.20, "lon_c": 79.55},
    "Joshimath":     {"elev_range": (1800, 3800), "flood_bias": 0.25, "lat_c": 30.55, "lon_c": 79.58},
    "Karnaprayag":   {"elev_range": (1200, 2000), "flood_bias": 0.7,  "lat_c": 30.27, "lon_c": 79.22},
    "Narayanbadri":  {"elev_range": (1400, 2500), "flood_bias": 0.45, "lat_c": 30.38, "lon_c": 79.70},
    "Pokhari":       {"elev_range": (1500, 2500), "flood_bias": 0.4,  "lat_c": 30.30, "lon_c": 79.80},
    "Tharali":       {"elev_range": (1300, 2200), "flood_bias": 0.55, "lat_c": 30.22, "lon_c": 79.62},
    "Dewal":         {"elev_range": (1600, 3000), "flood_bias": 0.35, "lat_c": 30.15, "lon_c": 79.72},
}

# ---------------------------------------------------------------------------
# Real Garhwali village name components
# ---------------------------------------------------------------------------
REAL_VILLAGE_PREFIXES = [
    "Gopeshwar", "Ukhimath", "Mandal", "Devgram", "Salna", "Baijnath",
    "Kulsari", "Nandprayag", "Rudraprayag", "Pipalkoti", "Helang",
    "Chamoli", "Gaura", "Urgam", "Ghingrana", "Kalpeshwar", "Khilla",
    "Tharali", "Dewal", "Narayan", "Bhageshwar", "Pauri", "Ransi",
    "Ghat", "Simli", "Bidoli", "Lambagarh", "Mayali", "Dumak",
    "Kirshi", "Jakhand", "Gairoli", "Kunwari", "Panwali", "Bedni",
    "Lata", "Malari", "Niti", "Mana", "Ghastoli", "Sutol",
    "Ramni", "Bhadragaon", "Kanaul", "Deval", "Srikot", "Gwari",
    "Dhauliganga", "Birahi", "Nalgaon", "Singoli", "Jhinjhipani",
    "Padoli", "Gwar", "Raioli", "Semra", "Thali", "Basuki",
    "Jakholi", "Kandara", "Karanprayag", "Bugyani", "Khirsu",
    "Pokhari", "Binta", "Naila", "Siror", "Kafol", "Jakhani",
    "Chhibro", "Ranthali", "Munsiyari", "Dunagiri", "Auli",
    "Bhavishya", "Kiran", "Surya", "Devali", "Uttarkashi",
]

VILLAGE_SUFFIXES = [
    "Gaon", "Khera", "Tola", "Patti", "Mafi", "Nagar", "Basti",
    "Dhar", "Bugyali", "Khal", "Ghat", "Pora", "Tal", "",
]

HINDI_SUFFIXES = ["गाँव", "खेड़ा", "टोला", "पट्टी", "बस्ती", "नगर", "धार"]


def _make_village_name(idx: int) -> tuple[str, str]:
    """Generate a plausible village name (English + Hindi transliteration)."""
    if idx < len(REAL_VILLAGE_PREFIXES):
        prefix = REAL_VILLAGE_PREFIXES[idx]
    else:
        prefix = f"Village_{idx:03d}"

    suffix = random.choice(VILLAGE_SUFFIXES)
    en_name = f"{prefix} {suffix}".strip() if suffix else prefix
    hi_name = f"{prefix} {random.choice(HINDI_SUFFIXES)}"
    return en_name, hi_name


def _gauss_clamp(mu: float, sigma: float, lo: float, hi: float) -> float:
    """Gaussian draw clamped to [lo, hi]."""
    return max(lo, min(hi, random.gauss(mu, sigma)))


# ---------------------------------------------------------------------------
# Elevation → hazard score helpers
# ---------------------------------------------------------------------------
def _flood_score(elevation_m: float, flood_bias: float) -> float:
    """
    Lower elevation ≈ river valleys → higher flood risk.
    Score 0–100; normalised from elevation band.
    """
    # Normalise elevation: 1200 m → high risk, 4200 m → low risk
    norm = (elevation_m - 1200) / (4200 - 1200)           # 0 at low, 1 at high
    base_score = (1.0 - norm) * 75 + random.gauss(0, 8)   # 0–75 range, noise
    bias_boost  = flood_bias * random.uniform(0, 20)
    return max(0.0, min(100.0, base_score + bias_boost))


def _landslide_score(elevation_m: float) -> float:
    """
    Mid-elevation (1500–2800 m) ≈ steep slopes + weathered rock → highest landslide risk.
    Bell-shaped around 2200 m.
    """
    peak = 2200.0
    sigma_ls = 700.0
    base = 80 * math.exp(-0.5 * ((elevation_m - peak) / sigma_ls) ** 2)
    return max(0.0, min(100.0, base + random.gauss(0, 9)))


def _erosion_score() -> float:
    """Moderate erosion risk across the district (15–65)."""
    return max(0.0, min(100.0, random.gauss(38, 12)))


def _ci_band(score: float, half_width: float) -> tuple[float, float]:
    """Return symmetric 90% CI clamped to [0, 100]."""
    return (
        round(max(0.0, score - half_width), 2),
        round(min(100.0, score + half_width), 2),
    )


# ---------------------------------------------------------------------------
# Priority score computation
# ---------------------------------------------------------------------------
def _compute_priority(
    flood_score: float,
    landslide_score: float,
    erosion_score: float,
    elderly_pct: float,
    sc_st_pct: float,
    literacy_rate: float,
    housing_pucca_pct: float,
) -> dict[str, Any]:
    """
    Monsoon-season composite priority score formula.

    hazard_score  = 0.40·flood + 0.35·landslide + 0.15·erosion
    vuln_index    = 0.30·(elderly/100) + 0.25·(sc_st/100)
                  + 0.25·(1−literacy/100) + 0.20·(1−pucca/100)
    final_score   = 0.70·hazard_score + 0.30·(vuln_index × 100)
    """
    flood_w, ls_w, erosion_w = 0.40, 0.35, 0.15
    hazard_score = flood_w * flood_score + ls_w * landslide_score + erosion_w * erosion_score

    vuln_index = (
        (elderly_pct / 100) * 0.30
        + (sc_st_pct / 100) * 0.25
        + (1.0 - literacy_rate / 100) * 0.25
        + (1.0 - housing_pucca_pct / 100) * 0.20
    )
    final_score = hazard_score * 0.70 + vuln_index * 100 * 0.30
    final_score  = max(0.0, min(100.0, final_score))

    if final_score > 80:
        tier = "IMMEDIATE"
    elif final_score > 60:
        tier = "SHORT_TERM"
    elif final_score > 40:
        tier = "MEDIUM_TERM"
    else:
        tier = "MONITOR"

    flood_contrib     = round(flood_w * flood_score * 0.70, 3)
    ls_contrib        = round(ls_w * landslide_score * 0.70, 3)
    erosion_contrib   = round(erosion_w * erosion_score * 0.70, 3)
    vuln_contrib      = round(vuln_index * 100 * 0.30, 3)

    score_breakdown = {
        "flood_contribution":      flood_contrib,
        "landslide_contribution":  ls_contrib,
        "erosion_contribution":    erosion_contrib,
        "vulnerability_contribution": vuln_contrib,
        "hazard_raw":              round(hazard_score, 3),
        "vuln_index_raw":          round(vuln_index * 100, 3),
    }

    # SHAP-style top-3 contributors (simplified linear attribution)
    contributors = [
        {"feature": "flood_score",      "shap_value": round(flood_contrib, 3),   "feature_value": round(flood_score / 100, 4)},
        {"feature": "landslide_score",  "shap_value": round(ls_contrib, 3),      "feature_value": round(landslide_score / 100, 4)},
        {"feature": "erosion_score",    "shap_value": round(erosion_contrib, 3), "feature_value": round(erosion_score / 100, 4)},
        {"feature": "elderly_pct",      "shap_value": round((elderly_pct / 100) * 0.30 * 30, 3), "feature_value": round(elderly_pct, 2)},
        {"feature": "literacy_inverse", "shap_value": round((1 - literacy_rate / 100) * 0.25 * 30, 3), "feature_value": round(1 - literacy_rate / 100, 4)},
        {"feature": "housing_kutcha",   "shap_value": round((1 - housing_pucca_pct / 100) * 0.20 * 30, 3), "feature_value": round(1 - housing_pucca_pct / 100, 4)},
    ]
    shap_top3 = sorted(contributors, key=lambda x: abs(x["shap_value"]), reverse=True)[:3]

    return {
        "score":          round(final_score, 2),
        "tier":           tier,
        "score_breakdown": score_breakdown,
        "shap_values":    shap_top3,
        "ci_lower_90":    round(max(0.0, final_score - random.uniform(8, 15)), 2),
        "ci_upper_90":    round(min(100.0, final_score + random.uniform(8, 15)), 2),
    }


# ===========================================================================
# SEED FUNCTIONS
# ===========================================================================

def seed_data_sources(cur: psycopg2.extensions.cursor) -> str:
    """Seed 1 — data_sources record. Returns the UUID."""
    ds_id = str(uuid.uuid4())
    cur.execute("""
        INSERT INTO navam.data_sources (
            id, source_system, source_dataset, source_uri, source_version,
            source_timestamp, transform_version, quality_flags, record_count, notes
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        ON CONFLICT DO NOTHING
        RETURNING id;
    """, (
        ds_id,
        "SYNTHETIC",
        "Chamoli Demo Dataset v1.0",
        None,
        "v1.0",
        datetime.now(timezone.utc),
        "sih2026-demo-seed",
        json.dumps({"null_rate": 0.0, "out_of_range_count": 0, "spatial_validity": True}),
        SEED_COUNT,
        "Synthetic data for SIH 2026 demo. Chamoli district, Uttarakhand. NOT real habitation data.",
    ))
    row = cur.fetchone()
    if row:
        return row[0]

    # Already existed — fetch it
    cur.execute("SELECT id FROM navam.data_sources WHERE source_system='SYNTHETIC' AND source_dataset='Chamoli Demo Dataset v1.0' LIMIT 1;")
    return cur.fetchone()[0]


def seed_policy_configs(cur: psycopg2.extensions.cursor) -> str:
    """Seed 2 — Default active policy config. Returns the UUID."""
    pc_id = str(uuid.uuid4())
    cur.execute("""
        INSERT INTO navam.policy_configs (
            id, policy_name, version, effective_from,
            weights, season_weights, thresholds, vulnerability_weights,
            is_active, author_id, approver_id, change_reason
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        ON CONFLICT (policy_name, version) DO NOTHING
        RETURNING id;
    """, (
        pc_id,
        "Default Monsoon Policy",
        1,
        datetime.now(timezone.utc),
        json.dumps({"flood": 0.35, "landslide": 0.30, "erosion": 0.15, "drought": 0.10, "cyclone": 0.10}),
        json.dumps({
            "MONSOON": {"flood": 0.40, "landslide": 0.35, "erosion": 0.15, "drought": 0.07, "cyclone": 0.03},
            "DRY":     {"flood": 0.20, "landslide": 0.20, "erosion": 0.30, "drought": 0.20, "cyclone": 0.10},
        }),
        json.dumps({"IMMEDIATE": 80, "SHORT_TERM": 60, "MEDIUM_TERM": 40}),
        json.dumps({"elderly_pct": 0.30, "sc_st_pct": 0.25, "literacy_inverse": 0.25, "housing_kutcha": 0.20}),
        True,
        "system",
        "architect",
        "Initial policy configuration for SIH 2026 demo — Chamoli district.",
    ))
    row = cur.fetchone()
    if row:
        return row[0]

    cur.execute("SELECT id FROM navam.policy_configs WHERE policy_name='Default Monsoon Policy' AND version=1 LIMIT 1;")
    return cur.fetchone()[0]


def seed_habitations(
    cur: psycopg2.extensions.cursor,
    ds_id: str,
) -> list[dict[str, Any]]:
    """Seed 3 — ~500 synthetic habitations. Returns list of habitation dicts."""

    # Check if already seeded
    cur.execute("SELECT COUNT(*) FROM navam.habitations WHERE data_source='SYNTHETIC';")
    existing = cur.fetchone()[0]
    if existing >= SEED_COUNT:
        print(f"  Habitations already seeded ({existing} rows). Skipping.")
        cur.execute("""
            SELECT id, lgd_village_code, lgd_block_code, block_name,
                   ST_Y(centroid::geometry) AS lat, ST_X(centroid::geometry) AS lon,
                   elevation_m, population_sc, population_st, population_total,
                   literacy_rate, elderly_pct, housing_pucca_pct
            FROM navam.habitations
            WHERE data_source='SYNTHETIC'
            ORDER BY lgd_village_code;
        """)
        rows = cur.fetchall()
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in rows]

    habitations: list[dict[str, Any]] = []
    records: list[tuple] = []

    for i in range(SEED_COUNT):
        block = BLOCKS[i % len(BLOCKS)]
        block_name = block["name"]
        block_meta = BLOCK_META[block_name]

        # Spatial position: cluster around block centre with Gaussian spread
        lat = _gauss_clamp(block_meta["lat_c"], 0.12, CHAMOLI_LAT_MIN, CHAMOLI_LAT_MAX)
        lon = _gauss_clamp(block_meta["lon_c"], 0.18, CHAMOLI_LON_MIN, CHAMOLI_LON_MAX)

        # Elevation — realistic mountain terrain
        elev_lo, elev_hi = block_meta["elev_range"]
        elev_mu = (elev_lo + elev_hi) / 2
        elevation_m = round(_gauss_clamp(elev_mu, (elev_hi - elev_lo) / 4, elev_lo, elev_hi), 1)

        # Village name
        village_name, village_name_hi = _make_village_name(i)

        # Population — log-normal (realistic mountain village sizes)
        pop_total = int(max(200, min(4000, random.lognormvariate(6.5, 0.8))))
        # SC/ST percentages — Chamoli has significant tribal population
        sc_pct = random.uniform(5, 20)
        st_pct = random.uniform(3, 25)
        pop_sc = int(pop_total * sc_pct / 100)
        pop_st = int(pop_total * st_pct / 100)

        households = max(40, int(pop_total / random.uniform(3.8, 5.5)))
        literacy_rate = round(_gauss_clamp(70, 10, 55, 90), 1)
        # More remote (high elevation) → lower literacy, higher elderly
        elevation_factor = (elevation_m - 1200) / (4200 - 1200)  # 0→low, 1→high
        elderly_pct = round(_gauss_clamp(12 + elevation_factor * 8, 3, 8, 25), 1)
        female_pct = round(_gauss_clamp(50, 3, 42, 58), 1)
        # Higher elevation → more kutcha housing (less pucca)
        housing_pucca_pct = round(_gauss_clamp(55 - elevation_factor * 30, 10, 20, 80), 1)
        area_sqkm = round(random.uniform(0.5, 12.0), 4)

        # LGD village code — synthetic but unique
        lgd_village_code = f"0501{block['code'][-2:]}{i+1:04d}"

        hab_id = str(uuid.uuid4())
        sc_st_pct = round(sc_pct + st_pct, 2)

        hab: dict[str, Any] = {
            "id":                  hab_id,
            "lgd_village_code":    lgd_village_code,
            "lgd_block_code":      block["code"],
            "lgd_district_code":   DISTRICT_CODE,
            "lgd_state_code":      STATE_CODE,
            "village_name":        village_name,
            "village_name_hi":     village_name_hi,
            "block_name":          block_name,
            "district_name":       DISTRICT_NAME,
            "state_name":          STATE_NAME,
            "lat":                 lat,
            "lon":                 lon,
            "elevation_m":         elevation_m,
            "area_sqkm":           area_sqkm,
            "population_total":    pop_total,
            "population_sc":       pop_sc,
            "population_st":       pop_st,
            "households":          households,
            "literacy_rate":       literacy_rate,
            "elderly_pct":         elderly_pct,
            "female_pct":          female_pct,
            "housing_pucca_pct":   housing_pucca_pct,
            "sc_st_pct":           sc_st_pct,
            "flood_bias":          block_meta["flood_bias"],
        }
        habitations.append(hab)

        records.append((
            hab_id,
            lgd_village_code,
            block["code"],
            DISTRICT_CODE,
            STATE_CODE,
            village_name,
            village_name_hi,
            block_name,
            DISTRICT_NAME,
            STATE_NAME,
            f"SRID=4326;POINT({lon} {lat})",   # WKT for PostGIS
            elevation_m,
            area_sqkm,
            pop_total,
            pop_sc,
            pop_st,
            households,
            literacy_rate,
            elderly_pct,
            female_pct,
            housing_pucca_pct,
            "SYNTHETIC",
            2011,
        ))

    # Batch insert with ON CONFLICT DO NOTHING (idempotent)
    psycopg2.extras.execute_values(
        cur,
        """
        INSERT INTO navam.habitations (
            id, lgd_village_code, lgd_block_code, lgd_district_code, lgd_state_code,
            village_name, village_name_hi, block_name, district_name, state_name,
            centroid, elevation_m, area_sqkm, population_total, population_sc, population_st,
            households, literacy_rate, elderly_pct, female_pct, housing_pucca_pct,
            data_source, source_year
        ) VALUES %s
        ON CONFLICT (lgd_village_code) DO NOTHING
        """,
        records,
        template="""(
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            ST_GeomFromEWKT(%s), %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s
        )""",
        page_size=100,
    )
    print(f"  Inserted {len(records)} habitations.")
    return habitations


def seed_hazard_scores(
    cur: psycopg2.extensions.cursor,
    habitations: list[dict[str, Any]],
    ds_id: str,
) -> dict[str, dict[str, float]]:
    """
    Seed 4 — Hazard scores.
    Returns dict: habitation_id → {flood, landslide, erosion}
    """
    cur.execute("SELECT COUNT(*) FROM navam.hazard_scores WHERE data_source='SYNTHETIC';")
    existing = cur.fetchone()[0]
    if existing >= len(habitations) * 3:
        print(f"  Hazard scores already seeded ({existing} rows). Fetching existing...")
        cur.execute("""
            SELECT habitation_id, hazard_type, score
            FROM navam.hazard_scores
            WHERE data_source='SYNTHETIC';
        """)
        scores_map: dict[str, dict[str, float]] = {}
        for row in cur.fetchall():
            hid, htype, score = row[0], row[1], float(row[2])
            scores_map.setdefault(str(hid), {})[htype] = score
        return scores_map

    valid_from = datetime(2026, 6, 1, tzinfo=timezone.utc)  # monsoon season start
    valid_to   = datetime(2026, 9, 30, tzinfo=timezone.utc)

    records: list[tuple] = []
    scores_map: dict[str, dict[str, float]] = {}

    for hab in habitations:
        hid = hab["id"]
        elev = hab["elevation_m"]
        flood_b = hab["flood_bias"]

        fl_score  = round(_flood_score(elev, flood_b), 2)
        ls_score  = round(_landslide_score(elev), 2)
        er_score  = round(_erosion_score(), 2)

        fl_ci  = _ci_band(fl_score, random.uniform(10, 16))
        ls_ci  = _ci_band(ls_score, random.uniform(12, 18))
        er_ci  = _ci_band(er_score, random.uniform(8, 14))

        scores_map[hid] = {"FLOOD": fl_score, "LANDSLIDE": ls_score, "EROSION": er_score}

        for hazard_type, score, ci_lo, ci_hi, raw_val, raw_unit in [
            ("FLOOD",     fl_score, fl_ci[0], fl_ci[1], round(max(0, (100 - fl_score) / 15), 3), "m_depth"),
            ("LANDSLIDE", ls_score, ls_ci[0], ls_ci[1], round(ls_score / 100, 4), "probability"),
            ("EROSION",   er_score, er_ci[0], er_ci[1], round(er_score * 2.5, 2), "t_ha_yr"),
        ]:
            records.append((
                str(uuid.uuid4()),
                hid,
                hazard_type,
                score,
                ci_lo,
                ci_hi,
                raw_val,
                raw_unit,
                ds_id,
                "SYNTHETIC_v1.0",
                valid_from,
                valid_to,
                "MONSOON",
                "SYNTHETIC",
            ))

    psycopg2.extras.execute_values(
        cur,
        """
        INSERT INTO navam.hazard_scores (
            id, habitation_id, hazard_type, score, ci_lower_90, ci_upper_90,
            raw_value, raw_unit, source_dataset_id, model_version,
            valid_from, valid_to, season, data_source
        ) VALUES %s
        ON CONFLICT DO NOTHING
        """,
        records,
        page_size=150,
    )
    print(f"  Inserted {len(records)} hazard score rows ({len(habitations)} habitations × 3 hazards).")
    return scores_map


def seed_priority_scores(
    cur: psycopg2.extensions.cursor,
    habitations: list[dict[str, Any]],
    scores_map: dict[str, dict[str, float]],
    policy_config_id: str,
) -> dict[str, str]:
    """
    Seed 5 — Priority scores.
    Returns dict: habitation_id → tier
    """
    cur.execute("SELECT COUNT(*) FROM navam.priority_scores;")
    existing = cur.fetchone()[0]
    if existing >= len(habitations):
        print(f"  Priority scores already seeded ({existing} rows). Fetching existing...")
        cur.execute("SELECT habitation_id, priority_tier FROM navam.priority_scores;")
        return {str(r[0]): r[1] for r in cur.fetchall()}

    records: list[tuple] = []
    tier_map: dict[str, str] = {}

    # First pass: compute all scores for ranking
    computed: list[dict[str, Any]] = []
    for hab in habitations:
        hid = hab["id"]
        hs = scores_map.get(hid, {"FLOOD": 30.0, "LANDSLIDE": 30.0, "EROSION": 30.0})
        result = _compute_priority(
            flood_score=hs["FLOOD"],
            landslide_score=hs["LANDSLIDE"],
            erosion_score=hs["EROSION"],
            elderly_pct=hab["elderly_pct"],
            sc_st_pct=hab["sc_st_pct"],
            literacy_rate=hab["literacy_rate"],
            housing_pucca_pct=hab["housing_pucca_pct"],
        )
        result["habitation_id"] = hid
        computed.append(result)

    # Sort for district rank
    computed.sort(key=lambda x: x["score"], reverse=True)
    for dist_rank, c in enumerate(computed, start=1):
        c["district_rank"] = dist_rank

    computed_by_score = sorted(computed, key=lambda x: x["score"], reverse=True)
    for nat_rank, c in enumerate(computed_by_score, start=1):
        c["national_rank"] = nat_rank  # same as district for single-district demo

    now = datetime.now(timezone.utc)
    for c in computed:
        hid = c["habitation_id"]
        tier_map[hid] = c["tier"]
        # Copula-approximated joint probability: P(flood AND landslide) ~ flood_score/100 * ls_score/100
        hs = scores_map.get(hid, {})
        joint_p = round((hs.get("FLOOD", 30) / 100) * (hs.get("LANDSLIDE", 30) / 100), 6)

        records.append((
            str(uuid.uuid4()),
            hid,
            policy_config_id,
            c["score"],
            c["ci_lower_90"],
            c["ci_upper_90"],
            c["tier"],
            c["national_rank"],
            c["district_rank"],
            json.dumps(c["score_breakdown"]),
            json.dumps(c["shap_values"]),
            joint_p,
            "MONSOON",
            now,
        ))

    psycopg2.extras.execute_values(
        cur,
        """
        INSERT INTO navam.priority_scores (
            id, habitation_id, policy_config_id, score, ci_lower_90, ci_upper_90,
            priority_tier, national_rank, district_rank, score_breakdown,
            shap_values, joint_hazard_probability, season, computed_at
        ) VALUES %s
        ON CONFLICT DO NOTHING
        """,
        records,
        page_size=100,
    )
    print(f"  Inserted {len(records)} priority score rows.")
    return tier_map


def seed_safe_sites(
    cur: psycopg2.extensions.cursor,
    ds_id: str,
) -> list[dict[str, Any]]:
    """Seed 6 — 20 synthetic safe sites across Chamoli."""
    cur.execute("SELECT COUNT(*) FROM navam.safe_sites WHERE data_source='SYNTHETIC';")
    existing = cur.fetchone()[0]
    if existing >= 20:
        print(f"  Safe sites already seeded ({existing} rows). Fetching existing...")
        cur.execute("""
            SELECT id, site_code, water_yield_lpd
            FROM navam.safe_sites
            WHERE data_source='SYNTHETIC';
        """)
        rows = cur.fetchall()
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in rows]

    SITE_TEMPLATES = [
        ("GVT_LAND",   "GOVERNMENT_LAND", "Gopeshwar Govt Land",       30.41, 79.32),
        ("JOSHI_CAMP",  "CAMP",           "Joshimath Relief Camp",      30.56, 79.57),
        ("KARNA_SITE",  "GOVERNMENT_LAND","Karnaprayag Flat Zone",      30.27, 79.22),
        ("GAIR_FIELD",  "GOVERNMENT_LAND","Gairsain Open Ground",       30.21, 79.56),
        ("THAR_SITE",   "CAMP",           "Tharali Transit Camp",       30.22, 79.63),
        ("DASH_PLATEAU","GOVERNMENT_LAND","Dasholi Highland Plateau",   30.47, 79.41),
        ("POKH_CAMP",   "CAMP",           "Pokhari Relief Zone",        30.31, 79.81),
        ("NARAY_SITE",  "GOVERNMENT_LAND","Narayanbadri Plains",        30.38, 79.71),
        ("DEWAL_CAMP",  "CAMP",           "Dewal Transit Site",         30.14, 79.73),
        ("BIRAHI_GVT",  "GOVERNMENT_LAND","Birahi Govt Flat",           30.44, 79.48),
        ("MANDAL_SITE", "GOVERNMENT_LAND","Mandal Relief Ground",       30.45, 79.36),
        ("PIPALK_CAMP", "CAMP",           "Pipalkoti Emergency Camp",   30.49, 79.45),
        ("SUTOL_SITE",  "GOVERNMENT_LAND","Sutol Valley Site",          30.25, 79.68),
        ("SRIKOT_GVT",  "GOVERNMENT_LAND","Srikot Government Land",     30.35, 79.50),
        ("LATA_CAMP",   "CAMP",           "Lata Village Camp",          30.52, 79.64),
        ("MANA_SITE",   "GOVERNMENT_LAND","Mana Border Site",           30.60, 79.75),
        ("URGAM_SITE",  "GOVERNMENT_LAND","Urgam Valley Ground",        30.43, 79.52),
        ("HELANG_CAMP", "CAMP",           "Helang Transit Camp",        30.50, 79.50),
        ("NITI_SITE",   "GOVERNMENT_LAND","Niti Pass Approach Zone",    30.58, 79.82),
        ("GHAT_CAMP",   "CAMP",           "Ghat Emergency Site",        30.32, 79.38),
    ]

    sites: list[dict[str, Any]] = []
    records: list[tuple] = []

    for site_code, site_type, site_name, lat, lon in SITE_TEMPLATES:
        site_id = str(uuid.uuid4())
        area_sqkm = round(random.uniform(0.05, 0.40), 4)
        area_sqm  = area_sqkm * 1_000_000

        water_yield_lpd  = random.randint(10_000, 150_000)
        elevation_m      = round(random.uniform(1300, 3200), 1)
        road_access      = random.random() > 0.2     # 80% have road access
        infra_factor     = 1.0 if road_access else 0.6

        # Capacity limits
        land_capacity   = int(area_sqm * 0.50)           # 0.5 persons/sqm
        water_capacity  = int(water_yield_lpd / 45)       # 45 lpd per person
        infra_capacity  = int(land_capacity * infra_factor)
        practical       = min(land_capacity, water_capacity, infra_capacity)
        # Clamp to realistic 500–5000
        practical       = max(500, min(5000, practical))

        sens_low  = int(practical * 0.80)
        sens_high = int(practical * 1.20)

        # Find nearest block
        nearest_block = min(BLOCKS, key=lambda b: (BLOCK_META[b["name"]]["lat_c"] - lat)**2 + (BLOCK_META[b["name"]]["lon_c"] - lon)**2)

        capacity_breakdown = {
            "land_sqm":         int(area_sqm),
            "persons_per_sqm":  0.50,
            "water_lpd":        water_yield_lpd,
            "lpd_per_person":   45,
            "road_access":      road_access,
            "infra_factor":     infra_factor,
            "land_capacity":    land_capacity,
            "water_capacity":   water_capacity,
            "infra_capacity":   infra_capacity,
        }

        site: dict[str, Any] = {
            "id":               site_id,
            "site_code":        site_code,
            "water_yield_lpd":  water_yield_lpd,
            "practical_capacity": practical,
            "capacity_breakdown": capacity_breakdown,
            "sensitivity_low":  sens_low,
            "sensitivity_high": sens_high,
            "land_capacity":    land_capacity,
            "water_capacity":   water_capacity,
            "infra_capacity":   infra_capacity,
        }
        sites.append(site)

        water_source = random.choice(["RIVER", "BOREWELL", "RIVER"])
        nearest_road = round(random.uniform(0.1, 8.0), 3)

        records.append((
            site_id,
            site_code,
            site_name,
            f"{site_name} स्थल",
            f"SRID=4326;POINT({lon} {lat})",
            area_sqkm,
            DISTRICT_CODE,
            nearest_block["code"],
            int(area_sqm * 0.5),
            elevation_m,
            True,                                           # hazard_free_verified
            road_access,
            nearest_road,
            water_source,
            water_yield_lpd,
            site_type,
            "AVAILABLE",
            "SYNTHETIC",
            ds_id,
            f"Synthetic safe site for SIH 2026 demo. {site_name}.",
        ))

    psycopg2.extras.execute_values(
        cur,
        """
        INSERT INTO navam.safe_sites (
            id, site_code, site_name, site_name_hi, centroid, area_sqkm,
            lgd_district_code, lgd_block_code, max_theoretical_capacity,
            elevation_m, hazard_free_verified, road_access, nearest_road_dist_km,
            water_source_type, water_yield_lpd, site_type, current_status,
            data_source, source_dataset_id, notes
        ) VALUES %s
        ON CONFLICT (site_code) DO NOTHING
        """,
        records,
        template="""(
            %s, %s, %s, %s, ST_GeomFromEWKT(%s), %s,
            %s, %s, %s,
            %s, %s, %s, %s,
            %s, %s, %s, %s,
            %s, %s, %s
        )""",
        page_size=25,
    )
    print(f"  Inserted {len(records)} safe sites.")
    return sites


def seed_capacity_assessments(
    cur: psycopg2.extensions.cursor,
    sites: list[dict[str, Any]],
) -> None:
    """Seed 7 — One capacity assessment per safe site."""
    cur.execute("SELECT COUNT(*) FROM navam.site_capacity_assessments;")
    existing = cur.fetchone()[0]
    if existing >= len(sites):
        print(f"  Capacity assessments already seeded ({existing} rows). Skipping.")
        return

    records: list[tuple] = []
    now = datetime.now(timezone.utc)

    for site in sites:
        records.append((
            str(uuid.uuid4()),
            site["id"],
            now,
            site["land_capacity"],
            site["water_capacity"],
            site["infra_capacity"],
            site["practical_capacity"],
            json.dumps(site["capacity_breakdown"]),
            site["sensitivity_low"],
            site["sensitivity_high"],
            "system-seeder",
            "ALGORITHMIC",
            "Generated by NAVAM synthetic data seeder (SIH 2026).",
        ))

    psycopg2.extras.execute_values(
        cur,
        """
        INSERT INTO navam.site_capacity_assessments (
            id, safe_site_id, assessment_date,
            land_capacity, water_capacity, infrastructure_capacity, practical_capacity,
            capacity_breakdown, sensitivity_low, sensitivity_high,
            assessed_by, assessment_method, notes
        ) VALUES %s
        ON CONFLICT DO NOTHING
        """,
        records,
        page_size=25,
    )
    print(f"  Inserted {len(records)} capacity assessments.")


# ===========================================================================
# MAIN
# ===========================================================================
def main() -> None:
    print("=" * 60)
    print("NAVAM Synthetic Data Seeder — SIH 2026")
    print(f"Target database: {DATABASE_URL.split('@')[-1]}")   # hide credentials
    print(f"Habitation count: {SEED_COUNT}")
    print("=" * 60)

    try:
        conn = psycopg2.connect(DATABASE_URL)
    except psycopg2.OperationalError as exc:
        print(f"\nERROR: Could not connect to database.\n{exc}", file=sys.stderr)
        sys.exit(1)

    conn.autocommit = False
    psycopg2.extras.register_uuid()

    try:
        with conn.cursor() as cur:
            # ------------------------------------------------------------------
            # Optional reset
            # ------------------------------------------------------------------
            if SEED_RESET:
                print("\n[RESET] Deleting existing synthetic data...")
                cur.execute("DELETE FROM navam.site_capacity_assessments;")
                cur.execute("DELETE FROM navam.safe_sites WHERE data_source='SYNTHETIC';")
                cur.execute("DELETE FROM navam.priority_scores;")
                cur.execute("DELETE FROM navam.hazard_scores WHERE data_source='SYNTHETIC';")
                cur.execute("DELETE FROM navam.habitations WHERE data_source='SYNTHETIC';")
                cur.execute("DELETE FROM navam.policy_configs WHERE author_id='system';")
                cur.execute("DELETE FROM navam.data_sources WHERE source_system='SYNTHETIC';")
                conn.commit()
                print("  Reset complete.\n")

            # ------------------------------------------------------------------
            # Seed 1: data_sources
            # ------------------------------------------------------------------
            print("\n[1/7] Seeding data_sources...")
            ds_id = seed_data_sources(cur)
            conn.commit()
            print(f"  data_source_id = {ds_id}")

            # ------------------------------------------------------------------
            # Seed 2: policy_configs
            # ------------------------------------------------------------------
            print("\n[2/7] Seeding policy_configs...")
            policy_config_id = seed_policy_configs(cur)
            conn.commit()
            print(f"  policy_config_id = {policy_config_id}")

            # ------------------------------------------------------------------
            # Seed 3: habitations
            # ------------------------------------------------------------------
            print(f"\n[3/7] Seeding {SEED_COUNT} habitations...")
            habitations = seed_habitations(cur, ds_id)
            conn.commit()

            # ------------------------------------------------------------------
            # Seed 4: hazard_scores
            # ------------------------------------------------------------------
            print("\n[4/7] Seeding hazard_scores...")
            scores_map = seed_hazard_scores(cur, habitations, ds_id)
            conn.commit()

            # ------------------------------------------------------------------
            # Seed 5: priority_scores
            # ------------------------------------------------------------------
            print("\n[5/7] Computing & seeding priority_scores...")
            tier_map = seed_priority_scores(cur, habitations, scores_map, policy_config_id)
            conn.commit()

            # ------------------------------------------------------------------
            # Seed 6: safe_sites
            # ------------------------------------------------------------------
            print("\n[6/7] Seeding safe_sites...")
            sites = seed_safe_sites(cur, ds_id)
            conn.commit()

            # ------------------------------------------------------------------
            # Seed 7: site_capacity_assessments
            # ------------------------------------------------------------------
            print("\n[7/7] Seeding capacity_assessments...")
            seed_capacity_assessments(cur, sites)
            conn.commit()

            # ------------------------------------------------------------------
            # Summary counts
            # ------------------------------------------------------------------
            print("\n" + "=" * 60)
            print("Seed complete:")

            for label, query in [
                ("Habitations",           "SELECT COUNT(*) FROM navam.habitations"),
                ("Hazard score rows",     "SELECT COUNT(*) FROM navam.hazard_scores"),
                ("Priority scores",       "SELECT COUNT(*) FROM navam.priority_scores"),
                ("Safe sites",            "SELECT COUNT(*) FROM navam.safe_sites"),
                ("Capacity assessments",  "SELECT COUNT(*) FROM navam.site_capacity_assessments"),
            ]:
                cur.execute(query)
                cnt = cur.fetchone()[0]
                print(f"  {label}: {cnt}")

            # Tier breakdown
            cur.execute("""
                SELECT priority_tier, COUNT(*)
                FROM navam.priority_scores
                GROUP BY priority_tier
                ORDER BY priority_tier;
            """)
            tier_counts = {row[0]: row[1] for row in cur.fetchall()}
            for tier in ("IMMEDIATE", "SHORT_TERM", "MEDIUM_TERM", "MONITOR"):
                print(f"  {tier} tier: {tier_counts.get(tier, 0)}")

            print("=" * 60)

    except Exception as exc:
        conn.rollback()
        print(f"\nERROR during seeding: {exc}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
