# NAVAM Demo Script — Full Rehearsal Document

**Team:** THE SIX SENSE  
**Event:** SIH 2026 Grand Finale  
**System:** NAVAM — Near-real-time Analysis of Vulnerability and Adaptive Migration  
**District:** Chamoli, Uttarakhand (synthetic demo data, clearly labelled in UI and database)  
**Total runtime:** 7 minutes presentation + 5 minutes Q&A  
**Last revised:** 2026-09-20

---

> **North-star sentence — memorise this:**
> *"NAVAM doesn't predict disasters. It tells authorities what to do before they happen — and shows its work."*

---

## PRE-DEMO CHECKLIST (15 minutes before)

- [ ] Laptop plugged into power — no battery risk
- [ ] Browser open on `http://localhost:3000` — dashboard loaded, Chamoli district visible
- [ ] Backup tab open on `http://localhost:3000/?demo=offline` — static snapshot if live fails
- [ ] `docker compose up` confirmed running — all containers green
- [ ] Martin tile server responding: `curl http://localhost:3000/tiles/habitations/0/0/0.pbf` returns 200
- [ ] PostGIS seeded: `psql -c "SELECT COUNT(*) FROM habitations WHERE demo_synthetic = TRUE;"` returns > 0
- [ ] Projector resolution set — dashboard renders at 1920×1080
- [ ] Phone camera backup: screen-record the entire session
- [ ] Water on desk. Deep breath. You know this system.

---

## SCENE BREAKDOWN

---

### SCENE 1 — HOOK (0:00–0:45)

**Who speaks:** Team Lead (or strongest speaker)

**Dialogue:**

> "Imagine it is July 14th, 2013. The Kedarnath cloud-burst has already happened. Over 5,000 people are dead. Authorities are scrambling, phone lines are down, and no one has a list of which villages to evacuate first — or where to send them.
>
> We cannot change 2013. But we can change the next time.
>
> My name is [NAME], and this is NAVAM — Near-real-time Analysis of Vulnerability and Adaptive Migration. NAVAM doesn't predict disasters. It tells authorities what to do before they happen — and shows its work."

**What to click:** Nothing. Stand. Make eye contact. Let the hook land.

**Backup line if nerves strike:**

> "The question NAVAM answers is not 'will a disaster happen?' It answers: 'Which people, in which order, to which safe site, with what capacity, right now?' That is the decision layer that has been missing from India's disaster management stack."

**Timing note:** 45 seconds maximum. Do not rush.

---

### SCENE 2 — THE PROBLEM STATEMENT (0:45–1:30)

**Who speaks:** Team Lead or Data Lead

**Dialogue:**

> "Today, district authorities in high-risk Himalayan districts receive hazard advisories from agencies like NDEM, IMD, and CWC. These advisories tell them *a zone is at risk*. They do not tell the District Collector which 8 villages to move, in which order, to which relief camp, and whether that camp has enough beds.
>
> The gap between 'hazard advisory' and 'executable evacuation order' is filled, today, by institutional memory, WhatsApp messages, and guesswork.
>
> NAVAM fills that gap with a defensible, auditable, machine-assisted decision layer."

**What to click:** Navigate to the **Problem** slide or the **About** panel in the dashboard sidebar.

**Backup line:**

> "Every disaster management authority in India knows what *might* happen. Nobody has a system that tells them what to *do* — in order — right now. That is NAVAM."

---

### SCENE 3 — LIVE DEMO: THE DASHBOARD (1:30–3:00)

**Who speaks:** Frontend Lead (driving the screen)

**Dialogue:**

> "This is the NAVAM decision dashboard. We are looking at Chamoli district, Uttarakhand. The data you see is synthetic and clearly tagged — but the pipeline running it is the same pipeline that would ingest real IMD, CWC, and GSI feeds in production."

**Step 3a — Map view (1:30–2:00)**

*Click:* Open the map view. Chamoli district boundary loads from Martin tile server.

> "Each dot is a habitation. The colour encodes the **Priority Score**: red means evacuate now, amber means elevated risk, green means monitor. The score range is 0 to 100."

*Click:* Hover over a red dot — fictional village **Niti Tola**, Joshimath block.

> "Niti Tola has a priority score of **87**. Notice the confidence interval beneath it: **78 to 92**. That interval is not decorative. It is a statistically guaranteed 90% coverage interval produced by Conformalized Quantile Regression. We are telling the Collector: 'The true risk is most likely 87, but could be as low as 78 or as high as 92. Act accordingly.'"

**Step 3b — Score breakdown (2:00–2:30)**

*Click:* Click the habitation dot — detail panel opens on the right.

> "The detail panel breaks the score into its components. Flood susceptibility: 0.74. Landslide susceptibility: 0.68. Exposed population: 892 people. Access degradation — road washout risk: 0.81. Seasonal multiplier: 1.2, because we are in peak monsoon. Joint hazard probability from the Gaussian copula: 0.71."

*Click:* Click **Explain Score** button — SHAP waterfall chart appears.

> "This SHAP waterfall chart shows the contribution of each feature to the final score. Access degradation is the dominant driver here. A human reviewer can see exactly why this village is flagged — this is not a black box."

**Step 3c — Recommended action (2:30–3:00)**

*Click:* Click **Recommended Action** tab.

> "NAVAM recommends relocating 892 residents of Niti Tola to **Pipalkoti Relief Camp**. That camp has a carrying capacity of 1,400. Of that, 320 are already allocated. Available capacity: 1,080 — sufficient for this relocation. Estimated evacuation window: 6–8 hours via NH-58."

**Backup if demo crashes at this point:**

> "I'll switch to our offline snapshot — the logic is identical, the data is the same." *(Open backup tab `?demo=offline`)*

---

### SCENE 4 — LIVE DEMO: THE DECISION LEDGER (3:00–4:15)

**Who speaks:** Backend Lead or Team Lead

**Dialogue:**

> "Every action in NAVAM is logged. When a District Collector approves a relocation recommendation, that approval — their identity, timestamp, the exact recommendation they saw, and the model version that generated it — is written to an immutable audit ledger."

*Click:* Navigate to **Audit Log** panel.

> "Here is the ledger. Each entry is append-only. We use a PostgreSQL table with a trigger that blocks UPDATE and DELETE operations — not application-level logic, but a database-level constraint. This is what we call WORM semantics — Write Once, Read Many.
>
> The Collector cannot be blamed for a decision they did not make. The system cannot silently change a recommendation after the fact. Every stakeholder in a post-disaster review can see exactly what was recommended, by which model version, and what the Collector decided."

*Click:* Click one audit entry to expand it.

> "This entry shows: Recommendation ID, habitation LGD code, model version 1.3, score 87 CI 78–92, recommended camp Pipalkoti, approved by District Collector Chamoli at 14:32 IST, action APPROVED."

**Backup line if audit page fails:**

> "The schema for the audit ledger is in our ADR-006 document — the design is the point, and we can walk through it."

---

### SCENE 5 — LIVE DEMO: THE INGESTION PIPELINE (4:15–5:00)

**Who speaks:** Data/ML Lead

**Dialogue:**

> "Where does the data come from? NAVAM's ingestion pipeline, built on Apache Kafka and Apache Airflow, consumes feeds from IMD for rainfall, CWC for river discharge, GSI for landslide susceptibility polygons, and LGD for official habitation identifiers.
>
> In this demo, we are replaying a synthetic monsoon surge event. Watch the scores update."

*Click:* Trigger the demo event — click **Simulate Rainfall Surge** button — scores on map update in near-real-time.

> "You can see scores shifting — Niti Tola went from 81 to 87 after the rainfall threshold was breached. The Scoring Worker recomputed scores for affected habitations within seconds and pushed updates through the API."

**Backup if simulation button fails:**

> "The simulation is a Kafka message replay — I'll trigger it from the CLI instead." *(Alt+Tab to terminal, run `python scripts/replay_event.py --event monsoon_surge`)*

---

### SCENE 6 — ARCHITECTURE OVERVIEW (5:00–5:45)

**Who speaks:** System Architect or Backend Lead

*Click:* Open **Architecture** slide or the C4 diagram in docs.

**Dialogue:**

> "The NAVAM stack: A React and MapLibre frontend serves the decision dashboard. A FastAPI gateway handles all API traffic. A separate FastAPI ML microservice serves the XGBoost model with MAPIE uncertainty wrappers. Celery workers handle score computation asynchronously. Airflow DAGs orchestrate nightly data ingestion. Martin — a high-performance Rust tile server — serves vector tiles directly from PostGIS. Keycloak handles authentication with role-based access for Collector, SDMA Analyst, and BDO roles. Everything is containerised on Kubernetes. Prometheus and Grafana monitor the stack.
>
> The architecture is designed for 766 districts and 1.2 million habitations. Scores are precomputed nightly into materialized views, so API responses are sub-second even at national scale."

---

### SCENE 7 — CLOSE (5:45–6:00)

**Who speaks:** Team Lead

**Dialogue:**

> "NAVAM is not a forecasting system. It is a decision-support system. It consumes hazard intelligence that already exists — from NDEM, IMD, CWC, GSI — and transforms it into executable, explainable, auditable evacuation recommendations.
>
> The District Collector makes every decision. The model earns trust by showing its work.
>
> *NAVAM doesn't predict disasters. It tells authorities what to do before they happen — and shows its work.*
>
> We are THE SIX SENSE. Thank you."

**What to click:** Nothing. Step back. Let the sentence land.

---

## Q&A SECTION (6:00–12:00)

**Stance:** Calm, specific, honest. If you don't know something, say: "That's outside our current scope — here's how we'd address it in Phase 2."

---

### Q1 — "How is this different from NDEM?"

**Expected question context:** Judge may be familiar with the National Disaster Management ecosystem and wonder if NAVAM duplicates existing government infrastructure.

**Rehearsed answer:**

> "We consume NDEM's hazard intelligence and add the decision layer. NDEM tells you a zone is at risk. NAVAM tells the Collector which 8 villages to move, in which order, to which site, with what capacity — and why.
>
> Think of NDEM as the meteorologist and NAVAM as the logistics commander. We are complementary, not competitive. In fact, our ingestion pipeline explicitly labels NDEM as a data source. We are downstream of NDEM, not a replacement."

**If pressed further:**

> "NDEM's mandate is hazard assessment and alerting. Our mandate is evacuation decision support. The gap between those two mandates is where lives are lost. NAVAM closes that gap."

---

### Q2 — "How accurate is your ML model?"

**Expected question context:** Judge may challenge the trustworthiness of an ML model making life-safety recommendations.

**Rehearsed answer:**

> "Our XGBoost model uses Conformalized Quantile Regression via MAPIE, which gives statistically guaranteed 90% coverage intervals. Every score shows a point estimate AND a range: 87 (CI: 78–92). We report uncertainty honestly rather than hiding it.
>
> On our synthetic validation set, held out during training, the model achieves an AUC-ROC of 0.84. But the accuracy metric is secondary to the uncertainty metric — we would rather show a wide interval and tell the Collector to be cautious than show a falsely precise number and create false confidence."

**If pressed on real-world accuracy:**

> "With real IMD, CWC, and GSI data, we expect model performance to improve significantly. The synthetic data is conservative by design — we trained on low-information scenarios to avoid overfitting to clean data."

---

### Q3 — "Is this data real?"

**Expected question context:** Judge may challenge authenticity of the demo.

**Rehearsed answer:**

> "The pipeline is real — the algorithms, scoring, audit, and carrying capacity logic all run on live architecture. The habitation data for this demo is synthetic, clearly tagged in the UI and database, seeded to Chamoli district boundaries.
>
> A production deployment ingests real IMD, CWC, GSI, and Census data. Our ingestion DAGs are already written for those API formats. The synthetic data was chosen because real habitation vulnerability data requires government MoU access — we are in conversations about that for Phase 1 deployment."

**If asked why Chamoli:**

> "Chamoli is one of the highest-risk districts in Uttarakhand — it experienced the 2021 Chamoli disaster, and the 2013 Kedarnath event falls within its cultural memory. It is a maximally meaningful demonstration context."

---

### Q4 — "What happens if the ML model is wrong?"

**Expected question context:** Judge probes the safety architecture and failure modes.

**Rehearsed answer:**

> "The system never acts autonomously. A District Collector makes every relocation decision, which is logged immutably with their identity and timestamp. The model's uncertainty intervals signal when to be cautious.
>
> Human-in-the-loop is not a feature — it is an architectural constraint. There is no API endpoint that issues an evacuation order. The API returns a *recommendation*. The *decision* is a separate action requiring an authenticated, role-authorised Collector user. Those are two different database records.
>
> If the model is wrong and a bad recommendation is approved, the audit ledger records exactly what the model said, what uncertainty it reported, and what the Collector decided. Post-event review is possible. Model retraining incorporates the feedback signal."

**If asked about model drift:**

> "MLflow tracks all model versions, hyperparameters, and evaluation metrics. We alert on score distribution drift using Prometheus metrics. If drift is detected, the system flags recommendations with an elevated uncertainty marker until the model is retrained."

---

### Q5 — "Can this scale nationally?"

**Expected question context:** Judge assesses viability beyond the demo district.

**Rehearsed answer:**

> "The architecture is designed for 766 districts and 1.2 million habitations. The scoring pipeline runs on Kubernetes, precomputes results nightly, and serves sub-second API responses from materialized views. Phase 1 targets 10 districts. National rollout is Phase 3 at 24 months.
>
> The key design decision that enables scale is the separation of *computation* from *serving*. We do not compute scores on API request — we precompute nightly and cache in PostGIS materialized views. An API read for all habitations in a district is a single indexed scan. Martin serves vector tiles directly from PostGIS at tile-cache speeds.
>
> The only bottleneck at national scale is the ML serving microservice — which we address with model batching and a GPU inference option for Phase 3."

**If asked about government cloud:**

> "We are targeting NIC Cloud or MeitY-approved GovCloud infrastructure for production. All components are cloud-agnostic — no vendor lock-in. Kubernetes manifests deploy to any conformant cluster."

---

## EMERGENCY PROTOCOLS

### If the live server goes down completely
1. Open backup tab: `http://localhost:3000/?demo=offline`
2. Say: *"I'll switch to our static snapshot — identical data, identical logic."*
3. Continue the demo as scripted — the offline snapshot has all panels pre-populated.

### If the projector disconnects
1. One team member continues narrating from memory.
2. Another reconnects the projector.
3. Do not go silent — keep talking.

### If a judge asks something you do not know
> *"That is a great question. That is outside our current implementation scope — our Phase 2 roadmap addresses it as follows: [brief honest answer]. I do not want to speculate beyond what we have built."*

### If you run over time
- Cut Scene 5 (ingestion pipeline) — it is the lowest-priority scene.
- The close sentence (Scene 7) is **non-negotiable** — always deliver it.

---

## TEAM ROLE ASSIGNMENTS

| Scene | Primary Speaker | Screen Driver | Backup Speaker |
|-------|----------------|--------------|----------------|
| Scene 1: Hook | Team Lead | — | ML Lead |
| Scene 2: Problem | Team Lead | — | Data Lead |
| Scene 3: Dashboard | Frontend Lead | Frontend Lead | Team Lead |
| Scene 4: Audit Ledger | Backend Lead | Backend Lead | Team Lead |
| Scene 5: Pipeline | Data Lead | Data Lead | ML Lead |
| Scene 6: Architecture | Architect | Architect | Backend Lead |
| Scene 7: Close | Team Lead | — | — |
| Q&A | All | — | — |

---

## TIMING SHEET

| Scene | Start | End | Duration |
|-------|-------|-----|----------|
| Pre-demo setup | −15:00 | 0:00 | 15 min |
| Scene 1: Hook | 0:00 | 0:45 | 45 sec |
| Scene 2: Problem | 0:45 | 1:30 | 45 sec |
| Scene 3: Dashboard | 1:30 | 3:00 | 90 sec |
| Scene 4: Audit Ledger | 3:00 | 4:15 | 75 sec |
| Scene 5: Pipeline | 4:15 | 5:00 | 45 sec |
| Scene 6: Architecture | 5:00 | 5:45 | 45 sec |
| Scene 7: Close | 5:45 | 6:00 | 15 sec |
| Buffer | 6:00 | 7:00 | 60 sec |
| Q&A | 7:00 | 12:00 | 5 min |

---

## THE CLOSING SENTENCE

This is the last thing said. Every team member must know it cold.

> **"NAVAM doesn't predict disasters. It tells authorities what to do before they happen — and shows its work."**

---

*Document status: FINAL — commit as first file in repository.*  
*Owner: Team Lead, THE SIX SENSE*  
*Next review: 48 hours before demo day*