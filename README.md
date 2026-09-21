# 🌍 NAVAM

```text
 ███╗   ██╗ █████╗ ██╗   ██╗ █████╗ ███╗   ███╗
 ████╗  ██║██╔══██╗██║   ██║██╔══██╗████╗ ████║
 ██╔██╗ ██║███████║██║   ██║███████║██╔████╔██║
 ██║╚██╗██║██╔══██║╚██╗ ██╔╝██╔══██║██║╚██╔╝██║
 ██║ ╚████║██║  ██║ ╚████╔╝ ██║  ██║██║ ╚═╝ ██║
 ╚═╝  ╚═══╝╚═╝  ╚═╝  ╚═══╝  ╚═╝  ╚═╝╚═╝     ╚═╝
```

### **Near-real-time Analysis of Vulnerability and Adaptive Migration**

<p align="center">
  <strong>AI × GIS × Real-Time Data × Decision Intelligence</strong>
</p>

<p align="center">
  <em>From hazard signals to explainable, actionable relocation decisions.</em>
</p>

<p align="center">

[![SIH 2026](https://img.shields.io/badge/Smart%20India%20Hackathon-2026-orange?style=for-the-badge)](https://www.sih.gov.in/)
[![Problem](https://img.shields.io/badge/Problem-SIH26191-red?style=for-the-badge)](#problem-statement)
[![CI](https://github.com/the-six-sense/navam/actions/workflows/ci.yml/badge.svg)](https://github.com/the-six-sense/navam/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg)](https://fastapi.tiangolo.com/)

</p>

---

> ## 🚨 NAVAM doesn't just show where danger is.
>
> ## **It helps authorities decide what to do next — and shows why.**

---

# 🧭 What is NAVAM?

**NAVAM** is a geospatial and AI-powered disaster-management decision-support platform designed to transform multi-source hazard data into **habitation-level risk intelligence, evacuation priorities, relocation recommendations, and auditable decisions.**

Instead of forcing responders to interpret disconnected datasets, NAVAM connects the complete decision chain:

```text
        🌧️ HAZARD SIGNALS
               │
               ▼
        🗺️ GEO-SPATIAL ANALYSIS
               │
               ▼
        👥 VULNERABILITY
               │
               ▼
        🧠 RISK SCORING
               │
               ▼
        🔍 EXPLAINABLE AI
               │
               ▼
        🚨 EVACUATION PRIORITY
               │
               ▼
        📍 SAFE SITE SELECTION
               │
               ▼
        📦 RESOURCE ALLOCATION
               │
               ▼
        📜 AUDITABLE DECISION
```

---

# 🎯 Problem Statement

### **SIH 2026 — SIH26191**

**Ministry:** Ministry of Home Affairs
**Domain:** Disaster Management
**Team:** THE SIX SENSE

The critical challenge in disaster response is not only detecting a hazard. Authorities must rapidly determine:

* **Which habitations are most vulnerable?**
* **Who needs attention first?**
* **Which routes remain usable?**
* **Where can affected populations be relocated?**
* **Does the destination have sufficient capacity?**
* **Which resources are available?**
* **Why did the system recommend this action?**
* **Who made the final decision?**

NAVAM is designed around this operational gap.

---

# ⚡ The NAVAM Difference

Traditional disaster dashboards often answer:

> **"What is happening?"**

NAVAM is designed to move one step further:

> **"What should the response team examine next?"**

### From:

```text
Hazard Map
    ↓
Human Interpretation
    ↓
Manual Prioritisation
    ↓
Manual Planning
```

### To:

```text
Live / Updated Data
       ↓
Spatial Intelligence
       ↓
Risk & Vulnerability Analysis
       ↓
Explainable Priority
       ↓
Route + Resource Analysis
       ↓
Relocation Intelligence
       ↓
Human Decision
       ↓
Audit Trail
```

---

# 🖥️ Seven Decision Screens

NAVAM is intentionally organized around **seven decision-oriented screens**.

|      # | Screen                           | Decision Question                                    |
| -----: | -------------------------------- | ---------------------------------------------------- |
| **01** | 🗺️ **Risk Heatmap**             | Which habitations are in danger right now?           |
| **02** | 🧠 **Habitation Scorecard**      | Why is this habitation at risk?                      |
| **03** | 🚨 **Evacuation Priority Queue** | Who should be moved first?                           |
| **04** | 🛣️ **Route Optimiser**          | Which routes are usable or blocked?                  |
| **05** | 🚚 **Resource Allocation**       | Where are teams and resources required?              |
| **06** | ⚠️ **Conflict Detector**         | Are response resources being deployed inefficiently? |
| **07** | 📜 **Audit / Decision Trail**    | What happened, when, and by whom?                    |

---

# 🧠 Explainable Risk Intelligence

NAVAM does not intend to turn disaster response into a black-box prediction.

Each score can be decomposed into contributing factors.

### Example

```text
┌────────────────────────────────────────────┐
│        HABITATION PRIORITY                 │
│                                            │
│                 87.4                       │
│                CRITICAL                    │
├────────────────────────────────────────────┤
│                                            │
│  Landslide Susceptibility   ████████████   │
│  Rainfall Exposure          ██████████     │
│  Population Exposure        ████████       │
│  Accessibility              ██████         │
│  Historical Events          ████           │
│                                            │
└────────────────────────────────────────────┘
```

The system is designed to expose:

* Model version
* Input features
* Feature contribution
* Prediction
* Confidence / uncertainty
* Data timestamp

---

# 📍 Adaptive Relocation Intelligence

When a habitation reaches a critical priority level, NAVAM evaluates potential relocation sites.

```text
                 AFFECTED HABITATION
                         │
                         ▼
               ┌──────────────────┐
               │ Candidate Sites   │
               └────────┬─────────┘
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
      Safety         Capacity       Accessibility
        │               │               │
        └───────────────┼───────────────┘
                        ▼
                Site Suitability
                        │
                        ▼
             Relocation Recommendation
```

### Candidate Site Example

| Parameter           |     Result |
| ------------------- | ---------: |
| Affected Population |        892 |
| Available Capacity  |      1,050 |
| Distance            |     8.2 km |
| Safety              |       High |
| Accessibility       |       High |
| Capacity            | Sufficient |

---

# 🏗️ System Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│                        DATA SOURCES                         │
│       IMD · CWC · GSI · LGD · Other GIS Sources            │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
                    ┌──────────────────┐
                    │      Kafka       │
                    │ Event Streaming  │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │      Worker      │
                    │ Normalize /      │
                    │ Enrich / Score   │
                    └────────┬─────────┘
                             │
              ┌──────────────┴──────────────┐
              ▼                             ▼
     ┌─────────────────┐          ┌─────────────────┐
     │ PostgreSQL      │          │ ML Serving      │
     │ + PostGIS       │          │ sklearn/XGBoost │
     │ + Redis         │          │ + OR-Tools      │
     └────────┬────────┘          └────────┬────────┘
              │                            │
              └──────────────┬─────────────┘
                             ▼
                    ┌──────────────────┐
                    │     FastAPI      │
                    │ REST + WebSocket │
                    └────────┬─────────┘
                             │
                  ┌──────────┴──────────┐
                  ▼                     ▼
          ┌──────────────┐      ┌───────────────┐
          │ Martin Tiles │      │ React Web App │
          │    MVT       │      │   MapLibre    │
          └──────────────┘      └───────────────┘
```

---

# 🔄 Decision Pipeline

```text
DATA
 │
 ├── IMD Rainfall
 ├── CWC Flood
 ├── GSI Landslide
 └── LGD Registry
 │
 ▼
INGESTION
 │
 ▼
NORMALISATION
 │
 ▼
SPATIAL PROCESSING
 │
 ▼
FEATURE ENGINEERING
 │
 ▼
ML / RISK ENGINE
 │
 ▼
EXPLAINABILITY
 │
 ▼
PRIORITY
 │
 ▼
ROUTE + RESOURCE ANALYSIS
 │
 ▼
RELOCATION INTELLIGENCE
 │
 ▼
AUTHORITY DECISION
 │
 ▼
AUDIT
```

---

# 🛠️ Technology Stack

| Layer             | Technology                  |
| ----------------- | --------------------------- |
| 🎨 Frontend       | React + MapLibre GL JS      |
| ⚡ API             | FastAPI + Uvicorn           |
| 🗄️ Database      | PostgreSQL + PostGIS        |
| 🚀 Cache          | Redis                       |
| 📨 Messaging      | Apache Kafka                |
| 🗺️ Tile Server   | Martin                      |
| 🤖 ML             | Scikit-learn + XGBoost      |
| 🧮 Optimisation   | Google OR-Tools             |
| 📊 ML Tracking    | MLflow                      |
| 🔄 Orchestration  | Apache Airflow              |
| 🔐 Authentication | Keycloak                    |
| 📈 Observability  | Prometheus + Grafana + Loki |
| 🐳 Containers     | Docker                      |
| ☁️ Infrastructure | AWS EKS + Helm + ArgoCD     |
| 🏗️ IaC           | Terraform                   |
| 🔁 CI/CD          | GitHub Actions              |

---

# 📦 Repository Structure

```text
NAVAM/
│
├── apps/
│   ├── api/                    # FastAPI backend
│   ├── web/                    # React + MapLibre frontend
│   └── worker/                 # Kafka event consumer
│
├── services/
│   ├── ml/
│   │   ├── training/           # Model training
│   │   └── serving/            # ML inference
│   │
│   └── airflow/
│       └── dags/               # Data pipelines
│
├── infra/
│   ├── docker/                 # Docker configuration
│   ├── k8s/navam/              # Helm deployment
│   ├── terraform/              # AWS infrastructure
│   └── scripts/                # Seed & maintenance
│
├── docs/
│   ├── architecture/           # System architecture
│   ├── adr/                    # Architecture decisions
│   └── runbooks/               # Operational guides
│
├── data/
│   └── sample/                 # Synthetic demo data
│
├── docker-compose.yml
├── docker-compose.demo.yml
├── Makefile
├── pyproject.toml
└── .env.example
```

---

# 🚀 Quick Start

### Prerequisites

* Docker Desktop 4.x
* `make`
* Python 3.12
* Node.js 20

### 1. Clone

```bash
git clone https://github.com/the-six-sense/navam.git
cd navam
```

### 2. Configure

```bash
cp .env.example .env
```

### 3. Start Demo Stack

```bash
make demo
```

### 4. Seed Demo Data

```bash
make db-seed
```

### 5. Open Dashboard

```bash
make open
```

**Dashboard:** `http://localhost:5173`

---

# 🔌 API & Developer Tools

| Service        | URL                                 |
| -------------- | ----------------------------------- |
| 📚 Swagger     | `http://localhost:8000/docs`        |
| 📖 ReDoc       | `http://localhost:8000/redoc`       |
| ❤️ Health      | `http://localhost:8000/health`      |
| 🔬 Deep Health | `http://localhost:8000/health/deep` |

---

# 📊 Observability

| Service    | URL                     |
| ---------- | ----------------------- |
| Grafana    | `http://localhost:3001` |
| Prometheus | `http://localhost:9090` |
| MLflow     | `http://localhost:5001` |
| Airflow    | `http://localhost:8082` |
| Keycloak   | `http://localhost:8080` |

> Default development credentials are documented in the local environment configuration. **Never use development credentials in production.**

---

# ⚙️ Development Commands

```bash
make up
```

Start the complete development stack.

```bash
make demo
```

Start the minimal demonstration environment.

```bash
make down
```

Stop all services.

```bash
make logs
```

View application logs.

```bash
make db-migrate
```

Run database migrations.

```bash
make db-seed
```

Load synthetic demonstration data.

```bash
make test
```

Run the complete test suite.

```bash
make lint
```

Run linting.

```bash
make health
```

Run the deep system health check.

```bash
make score HABITATION_ID=<uuid>
```

Generate a habitation score.

---

# 🧪 Engineering Discipline

NAVAM follows a **vertical-slice development model**.

Every meaningful feature should travel through the complete stack:

```text
Frontend
   ↓
API
   ↓
Service
   ↓
Database / ML
   ↓
Tests
```

### Core principles

**01 — No UI claim without implementation**

If it appears in the demo, it must work.

**02 — Provenance first**

Every important recommendation should be traceable.

**03 — Explainable decisions**

AI outputs should expose their contributing factors.

**04 — Human authority**

NAVAM supports decisions; authorized officials remain responsible for final action.

**05 — Operational correctness**

Timezone, idempotency, auditability, and failure handling are treated as correctness requirements.

---

# 🔐 Trust & Data Provenance

NAVAM follows a traceability chain:

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
Recommendation
   ↓
Authority Decision
   ↓
Audit Record
```

This allows the team to answer:

> **"Why did NAVAM recommend this?"**

and:

> **"What information and model produced that recommendation?"**

---

# 🧬 Data Disclaimer

All habitation data, population figures, and hazard readings used in the current development and demonstration environment are **synthetic**.

They are not derived from classified, restricted, or personally identifiable government datasets.

The architecture is designed to support authoritative data sources such as **IMD, CWC, GSI, and LGD** when deployed in an appropriate government environment.

---

# 🗺️ Roadmap

### Foundation

* [x] Architecture
* [ ] Authentication
* [ ] PostGIS
* [ ] CI/CD

### GIS Intelligence

* [ ] Interactive risk map
* [ ] Hazard layers
* [ ] Habitation layers
* [ ] Population exposure

### AI Intelligence

* [ ] Feature engineering
* [ ] Risk scoring
* [ ] Model training
* [ ] Explainability

### Response Intelligence

* [ ] Evacuation priority
* [ ] Route optimisation
* [ ] Resource allocation
* [ ] Conflict detection

### Relocation

* [ ] Candidate site identification
* [ ] Carrying capacity
* [ ] Site ranking
* [ ] Recommendation engine

### Governance

* [ ] Authority workflow
* [ ] Decision overrides
* [ ] Audit ledger
* [ ] RBAC

---

# 👥 Team

## THE SIX SENSE

**Smart India Hackathon 2026**

Building technology at the intersection of:

`AI` · `GIS` · `Disaster Management` · `Machine Learning` · `Geospatial Intelligence`

---

# 📄 License

This project is licensed under the **MIT License**.

See [`LICENSE`](LICENSE) for details.

---

<div align="center">

## 🌍 NAVAM

### **See the risk. Understand the why. Decide what happens next.**

**Built with ❤️ by THE SIX SENSE**
Developer : Darshan Kumar

*Smart India Hackathon 2026 · SIH26191*

</div>
