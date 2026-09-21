# NAVAM Review Standard

**Project:** NAVAM — Near-real-time Analysis of Vulnerability and Adaptive Migration  
**Team:** THE SIX SENSE  
**Status:** Binding — applies to all pull requests, schema changes, and feature work  
**Date:** 2026-09-20  
**Version:** 1.0

---

## Purpose

This document defines the non-negotiable review rules for NAVAM. They exist because NAVAM operates at the intersection of machine learning, geospatial data, government identity, and life-safety decisions. In this domain, a silent regression is not a bug — it is a liability. A UI claim without implementation is not an exaggeration — it is a misrepresentation to evaluators and, eventually, to emergency managers who might stake lives on it.

Every rule below has a rationale. The rationale is not decoration. If a reviewer does not understand *why* a rule exists, they are not qualified to waive it.

---

## Rule 1 — Every Architectural Decision Has an ADR

### Statement

No architectural decision — choice of database, ML framework, authentication system, tile server, message broker, or CI platform — is merged without a corresponding Architecture Decision Record (ADR) in `docs/adr/`.

### Rationale

Architectural decisions have long tails. A choice made in sprint 1 (e.g., PostGIS over a flat-file store) has implications for sprint 12 (spatial indexing strategy, replication, tile serving performance). When the original decider has left the team or forgotten the reasoning, the ADR is the institutional memory.

ADRs also serve evaluators. A judge who asks "why PostGIS?" should be able to read ADR-001 and get a complete, honest answer including the tradeoffs. An answer that exists only in someone's head is an answer that does not exist.

**ADR format:** Nygard format — Status, Date, Deciders, Context, Decision, Consequences. See `docs/adr/ADR-001.md` for the template.

**Enforcement:** PRs that introduce a new technology, replace an existing component, or change a protocol between components must link the corresponding ADR. A reviewer who approves such a PR without an ADR is themselves in violation of this standard.

---

## Rule 2 — No UI Claim Without Implementation

### Statement

Any feature shown or described in the dashboard, documentation, or demo script must be implemented and verifiable. "Coming soon," "will show," or "placeholder" UI elements are prohibited in demo-facing paths.

### Rationale

SIH evaluators are experienced. They have seen hundreds of demos where a slick slide deck does not match a working system. NAVAM's competitive advantage is operational reality — a real scoring pipeline, real audit ledger, real tile serving. Undermining that with fake UI panels destroys the credibility of everything else.

This rule applies in both directions:
- A UI element that exists but is not documented must be removed or documented.
- A documented feature that is not implemented must be removed from documentation until it is.

**Enforcement:** The Design Lead signs off on all demo-path UI. The Design Lead must have run the full demo locally before approving any PR that touches dashboard components. Screenshots in PRs are encouraged; live recordings are required for major feature PRs.

**Scope clarification:** Offline snapshot pages (`?demo=offline`) are exempt — these are explicitly labelled as static fallbacks and their static nature is part of the demo script.

---

## Rule 3 — Every Gap Becomes a Task Within 24 Hours

### Statement

When a review identifies a gap — missing implementation, missing test, missing documentation, incorrect claim — a GitHub Issue must be created within 24 hours of the review comment. The issue must be assigned, labelled, and linked to the PR.

### Rationale

Review comments that are not tracked become technical debt that is invisible at sprint planning. In a time-pressured SIH sprint, invisible debt is the most dangerous kind — it surfaces as a failed demo.

The 24-hour rule is not arbitrary. It is short enough that the context of the gap is still fresh in the reviewer's mind, and long enough that the reviewer does not interrupt their current work to file it immediately.

**Enforcement:** PRs may not be merged if they have open "gap" review comments older than 24 hours without a linked issue. The author is responsible for filing the issue, not the reviewer.

**Issue label:** All gap issues must carry the label `gap` in addition to any relevant component label (`ml`, `api`, `ui`, `data`, `infra`).

---

## Rule 4 — Provenance Is First-Class

### Statement

Every piece of information that influences a priority score or relocation recommendation must have a traceable provenance chain:

**Dataset → Version → Feature → Model → Policy → Prediction → Explanation → Decision**

### Rationale

NAVAM's output — "evacuate these 892 people to this camp" — is only as trustworthy as its inputs. A score computed from an undated shapefile from an unknown source is not a defensible recommendation. A score computed from GSI Landslide Susceptibility Zone v2.1 (2024), ingested on 2026-09-20 at 03:15 IST by Airflow DAG `ingest_gsi_lsz` (run ID: abc123), used as feature `lsz_score` in model version `xgb-v1.3`, is a defensible recommendation.

Provenance is tracked at multiple levels:
- **Dataset provenance:** The `data_sources` table records source agency, version, ingestion timestamp, and Airflow run ID for every dataset.
- **Feature provenance:** Features are computed by deterministic, versioned transformers. Transformer version is stored alongside feature values.
- **Model provenance:** MLflow records model version, training dataset hashes, hyperparameters, and evaluation metrics.
- **Decision provenance:** The audit ledger records the exact recommendation (including model version and score CI) that the Collector saw when they made their decision.

**Enforcement:** PRs that add a new data source must update `data_sources` schema and the corresponding Airflow DAG to populate provenance fields. PRs that change a feature computation must bump the transformer version. Reviewers check provenance completeness as a first-class criterion, not an afterthought.

---

## Rule 5 — Operational Correctness Is Not Polish

### Statement

The following operational properties are treated as correctness requirements, not nice-to-haves:

1. **Timezone correctness:** All timestamps stored in PostGIS are UTC. All user-facing timestamps are displayed in IST (UTC+5:30) with explicit timezone label. No ambiguous timestamp is acceptable.
2. **Idempotency:** All Airflow DAG tasks and Celery scoring workers must be idempotent — running the same task twice with the same input must produce the same result and must not create duplicate records.
3. **Audit completeness:** Every state-changing API action (approve recommendation, override score, acknowledge alert) must produce an audit record. The audit record must be written in the same database transaction as the state change — not as a separate call.
4. **Failure modes:** Every external dependency (IMD feed, CWC feed, GSI feed) must have a documented and implemented failure mode. A feed going offline must produce a degraded-mode alert in the dashboard, not a silent stale score.

### Rationale

Operational bugs are the hardest to catch in a demo and the most embarrassing when caught. A timestamp shown as "2026-09-19 22:05 UTC" when the event happened at "2026-09-20 03:35 IST" is the same event — but a judge who notices the discrepancy will lose confidence in the entire system.

Idempotency prevents the Kafka replay scenario from creating phantom scores during the demo. Audit completeness is the entire point of ADR-006. Failure mode documentation prevents a live feed dropout from silently breaking the scoring pipeline during the demo.

**Enforcement:** Reviewers of data pipeline and API PRs must explicitly verify each of the four properties above. A PR that introduces a new external dependency must include a failure mode test.

---

## Rule 6 — Vertical Slices, Always

### Statement

Feature development proceeds as vertical slices: a thin, working, end-to-end implementation of the critical path before any horizontal expansion. A new hazard type is not "implemented" when the data is ingested. It is implemented when it flows from ingestion through scoring through the API into the dashboard with a visible, tested result.

### Rationale

Horizontal expansion (adding five more data sources before any of them reach the UI) creates a system that is wide but shallow — it looks comprehensive on paper but has no working path to test. At demo time, everything is "mostly done" and nothing is demonstrable.

Vertical slices ensure that at any point in development, there is a working demo path. The demo is not something built at the end — it is the integration test that runs every sprint.

**Application to NAVAM:** The critical path is: IMD rainfall → Kafka → Airflow DAG → PostGIS feature table → Scoring Worker → ML Serving → PostGIS score materialised view → FastAPI → Dashboard map layer. This path must be green before any secondary paths (additional hazard types, additional API endpoints, additional dashboard panels) are started.

**Enforcement:** Sprint planning must begin with the question: "What is the vertical slice for this sprint?" A sprint that does not produce a runnable demo increment is a failed sprint, regardless of how many horizontal components were completed.

---

## Emergency-Merge Prohibitions

The following two categories of change **may never be emergency-merged** — not by the team lead, not by the architect, not under demo-day pressure:

### 1. Schema Changes

Any change to the PostGIS schema (table additions, column renames, type changes, constraint additions or removals, index changes) requires:
- A migration script in `db/migrations/` with a sequential version number
- A rollback script
- Explicit sign-off from the Architect reviewer
- A full integration test run (not just unit tests)

**Reason:** Schema changes are irreversible in production. A migration applied without a rollback script in a demo environment becomes an unrecoverable state if it fails mid-run. A schema change that breaks a running Celery worker causes cascading failures across the scoring pipeline.

### 2. Auth / Audit / Decision Ledger

Any change to authentication logic (Keycloak configuration, JWT validation, role definitions), audit log schema or triggers, or the recommendation decision workflow requires:
- Sign-off from both the Architect and the Backend Lead
- An explicit security review comment addressing: authentication bypass risk, audit gap risk, and decision integrity risk
- A full end-to-end test demonstrating the audit record is written correctly for the changed path

**Reason:** These components are the trust foundation of NAVAM. A silent regression in the audit trigger means decisions are made without a record. A bug in the role-check middleware means a BDO user could approve a Collector-level decision. These are not fixable after the fact.

---

## Reviewers of Record

| Domain | Reviewer of Record | Scope |
|--------|-------------------|-------|
| Schema and API | Architect | All PostGIS schema changes, all FastAPI route additions, all ADRs |
| ML and Data | ML Lead | All model changes, all feature engineering, all data pipeline PRs, all MAPIE configuration |
| UI and Claims | Design Lead | All dashboard component changes, all demo script updates, all documentation claims about UI behaviour |

A PR touching multiple domains requires sign-off from all relevant reviewers of record.

---

## Waiver Process

A rule may be waived only in the following circumstances:
1. The waiving team member documents the waiver in the PR description, naming the rule, the reason, and the mitigating action.
2. The Reviewer of Record for the affected domain explicitly approves the waiver in a PR comment.
3. A follow-up issue is filed within 24 hours to restore full compliance (see Rule 3).

No rule may be waived more than once for the same reason. Recurring waivers indicate the rule needs to be updated, not permanently ignored.

---

*This document is binding from the date of first commit.*  
*Owner: Architect, THE SIX SENSE*  
*Next review: After SIH 2026 Grand Finale*