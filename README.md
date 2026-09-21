# NAVAM

```
 ███╗   ██╗ █████╗ ██╗   ██╗ █████╗ ███╗   ███╗
 ████╗  ██║██╔══██╗██║   ██║██╔══██╗████╗ ████║
 ██╔██╗ ██║███████║██║   ██║███████║██╔████╔██║
 ██║╚██╗██║██╔══██║╚██╗ ██╔╝██╔══██║██║╚██╔╝██║
 ██║ ╚████║██║  ██║ ╚████╔╝ ██║  ██║██║ ╚═╝ ██║
 ╚═╝  ╚═══╝╚═╝  ╚═╝  ╚═══╝  ╚═╝  ╚═╝╚═╝     ╚═╝
```

**Near-real-time Analysis of Vulnerability and Adaptive Migration**

[![CI](https://github.com/the-six-sense/navam/actions/workflows/ci.yml/badge.svg)](https://github.com/the-six-sense/navam/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg)](https://fastapi.tiangolo.com)

> **NAVAM doesn't predict disasters. It tells authorities what to do before they happen — and shows its work.**

---

## Problem Statement

**SIH 2026 — Problem ID: SIH26191**
**Ministry: Ministry of Home Affairs (MHA) / NDRF**

India faces an average of 250+ disaster events per year. The critical gap is not prediction — it is **decision lag**: the time between a hazard signal and the first actionable evacuation order. In the 2013 Kedarnath and 2023 Sikkim disasters, thousands of lives were lost not because the hazard was invisible, but because the response chain was too slow.

NAVAM closes that gap. It ingests real-time data from IMD, CWC, GSI, and NDMA; scores every habitation across Uttarakhand for composite risk; and presents district-level responders with a ranked, explainable action plan — **not a dashboard to stare at, but an order to execute**.

---

## Team

**THE SIX SENSE** — Smart India Hackathon 2026

---

## Quick Start

Five commands from zero to running demo:

```bash
# 1. Clone
git clone https://github.com/the-six-sense/navam.git && cd navam

# 2. Configure environment
cp .env.example .env
# Edit .env if needed — defaults work for local dev

# 3. Start demo stack (boots in < 60s)
make demo

# 4. Seed synthetic data
make db-seed

# 5. Open the dashboard
make open   # → http://localhost:5173
```

> **Prerequisites:** Docker Desktop 4.x, `make`, Python 3.12, Node.js 20

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  Data Sources                                                    │
│  IMD Rainfall · CWC Flood Gauge · GSI Landslide · LGD Registry │
└──────────────────────────────┬──────────────────────────────────┘
                               │ Kafka (imd-rainfall · cwc-flood
                               │        gsi-landslide · lgd-updates)
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│  Worker Service (Kafka consumer)                                 │
│  Normalises · enriches · triggers risk re-scoring               │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌────────────────┐    ┌────────────────────┐    ┌───────────────┐
│  PostGIS DB    │◄───│  FastAPI (NAVAM    │───►│  ML Serving   │
│  + Redis cache │    │   API)             │    │  (sklearn +   │
│                │    │  REST + WebSocket  │    │   OR-Tools)   │
└────────────────┘    └────────────────────┘    └───────────────┘
                               │
                     ┌─────────┴──────────┐
                     │  Martin Tile Server │
                     │  PostGIS → MVT     │
                     └─────────┬──────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │  Web Dashboard       │
                    │  (React + MapLibre)  │
                    └──────────────────────┘
```

Full architecture documentation → [`docs/architecture/`](docs/architecture/)

---

## The Seven Screens

NAVAM presents exactly seven decision screens — no more, no less. Each screen answers a specific question a district responder would ask under pressure.

| # | Screen | Question Answered |
|---|--------|-------------------|
| 1 | **Risk Heatmap** | Which habitations are in danger right now? |
| 2 | **Habitation Scorecard** | Why is this habitation at risk? (SHAP explainability) |
| 3 | **Evacuation Priority Queue** | Who do we move first? |
| 4 | **Route Optimiser** | Which routes are safe? Which are blocked? |
| 5 | **Resource Allocation** | Which trucks, teams, and helipads are available? |
| 6 | **Conflict Detector** | Are two teams heading to the same site simultaneously? |
| 7 | **Audit Log / Decision Trail** | What was done, when, and by whom? |

---

## API Documentation

| Endpoint | Description |
|----------|-------------|
| `http://localhost:8000/docs` | Swagger UI (interactive) |
| `http://localhost:8000/redoc` | ReDoc (printable) |
| `http://localhost:8000/health` | Liveness probe |
| `http://localhost:8000/health/deep` | Deep health (DB + Redis + ML) |

---

## Observability

| Service | URL | Credentials |
|---------|-----|-------------|
| Grafana | `http://localhost:3001` | admin / admin |
| Prometheus | `http://localhost:9090` | — |
| MLflow | `http://localhost:5001` | — |
| Airflow | `http://localhost:8082` | airflow / airflow |
| Keycloak | `http://localhost:8080` | admin / admin |

---

## Tech Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| API | FastAPI + uvicorn | 0.111 / 0.29 |
| Database | PostgreSQL + PostGIS | 16 + 3.4 |
| Cache | Redis | 7 |
| Messaging | Apache Kafka (Confluent) | 7.6 |
| Tile server | Martin (Rust, MapLibre) | 0.13 |
| Auth | Keycloak | 24.0 |
| ML training | scikit-learn, XGBoost | latest |
| Route optimisation | Google OR-Tools | 9.x |
| ML tracking | MLflow | 2.13 |
| Orchestration | Apache Airflow | 2.9 |
| Observability | Prometheus + Grafana + Loki | 2.52 / 10.4 / 3.0 |
| Container orchestration | AWS EKS (Helm + ArgoCD) | 1.30 |
| IaC | Terraform | 1.8 |
| Frontend | React + MapLibre GL JS | 18 / 4.x |
| CI/CD | GitHub Actions | — |

---

## Repository Structure

```
NAVAM/
├── apps/
│   ├── api/            # FastAPI backend
│   ├── web/            # React frontend (MapLibre)
│   └── worker/         # Kafka event consumer
├── services/
│   ├── ml/
│   │   ├── training/   # Model training scripts
│   │   └── serving/    # FastAPI inference server
│   └── airflow/
│       └── dags/       # Orchestration DAGs
├── infra/
│   ├── docker/         # Dockerfiles and compose configs
│   ├── k8s/navam/      # Helm chart (umbrella)
│   ├── terraform/      # AWS infrastructure (IaC)
│   └── scripts/        # Seed and maintenance scripts
├── docs/               # Architecture, ADRs, runbooks
├── data/
│   └── sample/         # Curated sample GeoJSON (synthetic)
├── docker-compose.yml       # Full dev stack (14 services)
├── docker-compose.demo.yml  # Minimal demo stack (8 services)
├── Makefile                 # All dev workflow commands
├── pyproject.toml           # Python tool config
└── .env.example             # Environment template
```

---

## Development

### Useful commands

```bash
make up          # Start full dev stack
make demo        # Start minimal demo stack
make down        # Stop all containers
make logs        # Tail API + ML serving logs
make db-migrate  # Run Alembic migrations
make db-seed     # Load synthetic data
make test        # Run all tests
make lint        # Lint Python + JS
make health      # Deep health check
make score HABITATION_ID=<uuid>  # Score a habitation
```

### Vertical Slice Discipline

Every feature is a **vertical slice** — frontend + API + DB + test in one PR.

- No PR touches more than one domain without reviewer sign-off.
- Tests live next to the code they test.
- Migrations are atomic and reversible.

→ See [CONTRIBUTING.md](CONTRIBUTING.md) for the full review standard.

---

## Data Disclaimer

All habitation data, population figures, and hazard readings used in the development and demo environment are **entirely synthetic**, generated by [`infra/scripts/seed_data.py`](infra/scripts/seed_data.py). They are not derived from any classified, restricted, or personally identifiable government dataset. The system is designed to connect to authoritative sources (IMD, CWC, GSI, LGD) via their official APIs when deployed in a government environment.

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

*Built with ❤️ for Smart India Hackathon 2026 · Problem SIH26191 · MHA/NDRF*
