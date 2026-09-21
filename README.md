# 🌍 NAVAM

### Near-real-time Analysis of Vulnerability and Adaptive Migration

<p align="center">
  <strong>AI × GIS × Disaster Intelligence × Human-Centered Decision Support</strong>
</p>

<p align="center">
  <em>Turning hazard intelligence into explainable, actionable relocation decisions.</em>
</p>

<p align="center">

![Status](https://img.shields.io/badge/Status-SIH%202026-0A7BFF?style=for-the-badge)
![AI](https://img.shields.io/badge/AI%2FML-Explainable-7C3AED?style=for-the-badge)
![GIS](https://img.shields.io/badge/GIS-PostGIS-16A34A?style=for-the-badge)
![Backend](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge)
![Frontend](https://img.shields.io/badge/Frontend-React-61DAFB?style=for-the-badge)

</p>

---

## 🚨 The Problem

During disasters, authorities don't only need to know **where a hazard exists**.

They need to answer:

> **Which habitation is most vulnerable?**
> **Who needs immediate attention?**
> **Where can affected people be safely relocated?**
> **Does the relocation site actually have enough capacity?**
> **Why did the system make this recommendation?**

Existing hazard information is often distributed across different datasets, systems, and agencies.

**NAVAM connects these pieces into one decision-support workflow.**

---

# 🧠 What is NAVAM?

**NAVAM** is an AI-powered, GIS-enabled disaster-management decision-support platform designed to transform multi-source hazard and vulnerability data into **explainable, traceable, and actionable relocation intelligence**.

```text
     🌧️ Hazard Data
           │
           ▼
   🗺️ Geospatial Analysis
           │
           ▼
   👥 Vulnerability Analysis
           │
           ▼
    🧠 Risk / Priority Engine
           │
           ▼
    🔍 Explainable AI
           │
           ▼
   📍 Safe Site Discovery
           │
           ▼
   📊 Carrying Capacity
           │
           ▼
   🚨 Relocation Recommendation
           │
           ▼
   👨‍💼 Human Authority Decision
           │
           ▼
      📜 Audit Ledger
```

---

# ✨ Core Capabilities

| Capability                      | Description                                                                |
| ------------------------------- | -------------------------------------------------------------------------- |
| 🗺️ **GIS Intelligence**        | Interactive visualization of hazards, habitations, infrastructure and risk |
| 🌊 **Multi-Hazard Analysis**    | Analyze supported hazard datasets within a common spatial framework        |
| 👥 **Vulnerability Assessment** | Combine hazard exposure, population and vulnerability indicators           |
| 🧠 **AI Risk Scoring**          | Generate habitation-level priority scores                                  |
| 🔍 **Explainable AI**           | Show *why* a habitation received its risk/priority score                   |
| 📍 **Relocation Intelligence**  | Identify and rank potential safer relocation sites                         |
| 🏕️ **Carrying Capacity**       | Evaluate whether candidate sites can accommodate affected populations      |
| 🚨 **Alerts**                   | Surface critical conditions and operational issues                         |
| 📱 **Field Reporting**          | Capture field observations, location and evidence                          |
| 📜 **Audit Ledger**             | Maintain traceable records of authority decisions                          |
| 🔗 **Data Provenance**          | Track data → feature → model → prediction → decision                       |
| ⚡ **Near-Real-Time Pipeline**   | Process incoming data through an automated geospatial/ML pipeline          |

---

# 🎯 The NAVAM Decision Chain

NAVAM is built around one central principle:

### **Hazard → Vulnerability → Priority → Safe Site → Capacity → Action**

Instead of stopping at:

> **"This area is at risk."**

NAVAM attempts to answer:

> **"This habitation requires attention, these factors contributed to its priority, these relocation sites are available, this site has sufficient capacity, and here is the evidence behind the recommendation."**

---

# 🖥️ Platform Overview

```text
┌──────────────────────────────────────────────────────────┐
│                         NAVAM                             │
│          Disaster Intelligence Command Center             │
├─────────────┬─────────────────────────────┬──────────────┤
│             │                             │              │
│  Dashboard  │          GIS MAP            │  Priority    │
│             │                             │  Habitations │
│  Hazards    │     🗺️ Interactive         │              │
│             │        Intelligence         │  🚨 Critical │
│  Sites      │                             │  ⚠️ High     │
│             │                             │  🟡 Medium   │
│  Reports    │                             │              │
│             │                             │              │
│  Audit      │                             │              │
└─────────────┴─────────────────────────────┴──────────────┘
```

---

# 🧠 Explainable AI

NAVAM does not treat AI as a black box.

Every prediction should be accompanied by understandable contributing factors.

### Example

```text
PRIORITY
━━━━━━━━━━━━━━━━━━━━━━━━━━
        87.4
       CRITICAL

Contributing Factors

██████████████  Landslide Susceptibility
███████████     Rainfall Exposure
█████████       Population Exposure
██████          Accessibility
████            Historical Events
```

The system can expose:

* Model version
* Input features
* Feature contributions
* Prediction
* Confidence / uncertainty
* Data timestamp

---

# 📍 Intelligent Relocation

Once a habitation reaches a configured priority threshold, NAVAM evaluates potential relocation sites.

### Site Evaluation

```text
             Candidate Site
                    │
       ┌────────────┼────────────┐
       ▼            ▼            ▼
    Safety       Capacity     Accessibility
       │            │            │
       └────────────┼────────────┘
                    ▼
             Site Suitability
                    │
                    ▼
          Relocation Recommendation
```

### Example

| Parameter           |      Value |
| ------------------- | ---------: |
| Affected Population |        892 |
| Available Capacity  |      1,050 |
| Distance            |     8.2 km |
| Safety              |       High |
| Accessibility       |       High |
| Capacity Status     | Sufficient |

---

# 📊 Data & AI Pipeline

```text
┌─────────────────────┐
│ External Data       │
│ IMD / CWC / GSI ... │
└──────────┬──────────┘
           ▼
      ┌──────────┐
      │  Kafka   │
      └────┬─────┘
           ▼
      ┌──────────┐
      │ Airflow  │
      └────┬─────┘
           ▼
┌──────────────────────┐
│ Data Validation &    │
│ Transformation       │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│ PostgreSQL + PostGIS │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│ Feature Engineering  │
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│ ML / Priority Engine │
└──────────┬───────────┘
           ▼
      ┌──────────┐
      │   SHAP   │
      └────┬─────┘
           ▼
┌──────────────────────┐
│ Explainable Decision │
└──────────┬───────────┘
           ▼
      ┌──────────┐
      │ FastAPI  │
      └────┬─────┘
           ▼
      ┌──────────┐
      │  React   │
      └──────────┘
```

---

# 🏗️ Architecture

```text
                    ┌──────────────────┐
                    │   Data Sources   │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Data Engineering │
                    │ Kafka + Airflow  │
                    └────────┬─────────┘
                             │
                             ▼
                  ┌───────────────────────┐
                  │ PostgreSQL + PostGIS  │
                  └───────────┬───────────┘
                              │
                ┌─────────────┴─────────────┐
                ▼                           ▼
       ┌─────────────────┐         ┌─────────────────┐
       │ GIS Processing  │         │ Feature Engine  │
       │ GeoPandas/GDAL  │         │ Python          │
       └────────┬────────┘         └────────┬────────┘
                │                           │
                └─────────────┬─────────────┘
                              ▼
                     ┌─────────────────┐
                     │ ML / Risk Engine│
                     │ XGBoost / RF    │
                     └────────┬────────┘
                              ▼
                     ┌─────────────────┐
                     │ SHAP / MLflow   │
                     └────────┬────────┘
                              ▼
                     ┌─────────────────┐
                     │     FastAPI     │
                     └────────┬────────┘
                              ▼
                     ┌─────────────────┐
                     │ React Dashboard │
                     │    MapLibre     │
                     └─────────────────┘
```

---

# 🛠️ Technology Stack

### Frontend

* React
* TypeScript
* Vite
* Tailwind CSS
* MapLibre GL JS
* ECharts / Recharts

### Backend

* Python
* FastAPI
* Celery
* REST APIs

### Data & GIS

* PostgreSQL
* PostGIS
* GeoPandas
* Shapely
* Rasterio
* GDAL
* QGIS

### AI / ML

* Python
* NumPy
* Pandas
* Scikit-learn
* XGBoost
* SHAP
* MLflow

### Data Engineering

* Apache Kafka
* Apache Airflow

### Infrastructure

* Docker
* GitHub Actions
* Keycloak
* Linux

---

# 🔐 Trust, Security & Auditability

NAVAM is designed for a high-stakes decision-support environment.

### 🔗 Data Provenance

```text
Dataset
   ↓
Version
   ↓
Feature
   ↓
Model
   ↓
Prediction
   ↓
Explanation
   ↓
Decision
```

### 📜 Auditability

Every important state-changing action is recorded.

Examples:

* Recommendation approval
* Recommendation rejection
* Score override
* Alert acknowledgement
* Role changes

### ⏱️ Operational Correctness

NAVAM enforces:

* UTC timestamps in storage
* IST display for users
* Idempotent pipeline tasks
* Transactional audit records
* Explicit dependency failure states

---

# 👥 User Roles

```text
SUPER_ADMIN
     │
     ├── System configuration
     ├── User management
     └── Audit access

STATE_AUTHORITY
     │
     └── State-level intelligence

DISTRICT_AUTHORITY
     │
     ├── Risk review
     ├── Recommendations
     └── Decisions

FIELD_OFFICER
     │
     └── Field reporting

ANALYST
     │
     ├── Data
     └── ML analysis

VIEWER
     │
     └── Read-only access
```

---

# 🚀 Getting Started

## Prerequisites

Make sure you have:

* Node.js
* Python 3.11+
* PostgreSQL
* PostGIS
* Docker
* Git

## Clone

```bash
git clone https://github.com/<your-username>/navam.git
cd navam
```

## Environment

Create your environment configuration:

```bash
cp .env.example .env
```

Configure:

```env
DATABASE_URL=
POSTGIS_URL=
REDIS_URL=
KAFKA_BROKER=
KEYCLOAK_URL=
MLFLOW_URL=
```

## Run with Docker

```bash
docker compose up --build
```

## Frontend

```bash
cd frontend
npm install
npm run dev
```

## Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

---

# 📁 Project Structure

```text
navam/
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── features/
│   │   ├── services/
│   │   ├── hooks/
│   │   └── types/
│   └── package.json
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── gis/
│   │   ├── ml/
│   │   └── audit/
│   └── requirements.txt
│
├── pipelines/
│   ├── dags/
│   ├── transformers/
│   ├── validators/
│   └── loaders/
│
├── db/
│   └── migrations/
│
├── docs/
│   └── adr/
│
├── docker-compose.yml
└── README.md
```

---

# 🧪 Testing

NAVAM follows an end-to-end testing philosophy.

```text
Unit Tests
    ↓
Integration Tests
    ↓
Pipeline Tests
    ↓
API Tests
    ↓
E2E Tests
    ↓
Demo Verification
```

Critical workflow:

```text
Login
  ↓
Select Habitation
  ↓
View Risk
  ↓
View Explanation
  ↓
View Relocation Site
  ↓
Review Recommendation
  ↓
Approve / Reject / Override
  ↓
Verify Audit Record
```

---

# 🗺️ Roadmap

### Phase 01 — Foundation

* [x] Architecture
* [ ] Repository setup
* [ ] Authentication
* [ ] PostGIS

### Phase 02 — GIS Intelligence

* [ ] Interactive map
* [ ] Hazard layers
* [ ] Habitation layers
* [ ] Population exposure

### Phase 03 — AI Intelligence

* [ ] Feature engineering
* [ ] Risk scoring
* [ ] ML model
* [ ] SHAP explanations

### Phase 04 — Relocation

* [ ] Candidate sites
* [ ] Capacity assessment
* [ ] Site ranking
* [ ] Recommendations

### Phase 05 — Governance

* [ ] Approval workflow
* [ ] Overrides
* [ ] Audit ledger
* [ ] RBAC

### Phase 06 — Field Operations

* [ ] Field reporting
* [ ] GPS
* [ ] Offline mode
* [ ] Synchronization

---

# 🧩 Engineering Principles

NAVAM follows a few non-negotiable principles:

### 01 — No Fake Intelligence

If a feature is shown, it must actually work.

### 02 — Explain Everything

A high-impact recommendation must have an understandable reason.

### 03 — Trace Everything

Every important output should be traceable back to its data and model.

### 04 — Humans Decide

NAVAM provides decision support; authorized authorities remain responsible for decisions.

### 05 — Build Vertical

A feature is complete only when it works from **data ingestion → processing → scoring → API → UI**.

### 06 — Fail Loudly

A broken external feed should produce an explicit degraded state rather than silently showing stale information.

---

# 🏆 Smart India Hackathon 2026

**NAVAM — THE SIX SENSE**

Developed as a disaster-management decision-support solution for **Smart India Hackathon 2026**.

### Focus Areas

`Disaster Management` · `Artificial Intelligence` · `GIS` · `Geospatial Intelligence` · `Machine Learning` · `Relocation Planning` · `Decision Support`

---

# 👨‍💻 Team

### THE SIX SENSE

Building technology for better disaster intelligence, faster decisions, and safer communities.

---

# 📄 License

Add your project's chosen license here.

---

<p align="center">

### 🌍 From Hazard Intelligence to Safer Decisions.

**NAVAM — Understand. Prioritize. Relocate. Protect.**

</p>
