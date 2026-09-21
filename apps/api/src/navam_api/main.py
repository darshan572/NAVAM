from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .routers import habitations, scores, sites, decisions, policies, jobs, audit, integrations, health, dashboard
from .middleware.correlation import CorrelationMiddleware
from .middleware.rate_limit import RateLimitMiddleware
from .middleware.audit_middleware import AuditMiddleware

app = FastAPI(title="NAVAM API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(CorrelationMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(AuditMiddleware)

# Root routes
app.include_router(health.router)
app.include_router(habitations.router)
app.include_router(scores.router)
app.include_router(sites.router)
app.include_router(decisions.router)
app.include_router(policies.router)
app.include_router(jobs.router)
app.include_router(audit.router)
app.include_router(integrations.router)
app.include_router(dashboard.router)

# /api/v1 routes
app.include_router(health.router, prefix="/api/v1")
app.include_router(habitations.router, prefix="/api/v1")
app.include_router(scores.router, prefix="/api/v1")
app.include_router(sites.router, prefix="/api/v1")
app.include_router(decisions.router, prefix="/api/v1")
app.include_router(policies.router, prefix="/api/v1")
app.include_router(jobs.router, prefix="/api/v1")
app.include_router(audit.router, prefix="/api/v1")
app.include_router(integrations.router, prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"type": "about:blank", "title": "Internal Server Error", "status": 500, "detail": str(exc)},
    )
