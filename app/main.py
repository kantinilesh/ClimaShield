"""
ClimaShield – FastAPI Application (Phase 4)
Entry point with scheduler integration and lifecycle management.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.api.admin_routes import admin_router
from app.config import settings
from app.services.logger import setup_logging, log_event


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle: init DB, start scheduler."""
    setup_logging()

    # Initialize database tables
    from app.db.database import init_db
    init_db()
    log_event("system", f"ClimaShield v{settings.app_version} starting up – DB initialized")

    print(f"🛡️  {settings.app_name} v{settings.app_version} starting up…")
    print(f"📡  Agent ID: {settings.erc8004_agent_id}")
    print(f"🔗  Registry: {settings.erc8004_registry}")
    print(f"💾  Database initialized")

    # Start background scheduler
    try:
        from app.services.scheduler import start_scheduler
        start_scheduler()
        print("⏰  Background scheduler started (oracle check every 5 min)")
    except Exception as e:
        print(f"⚠️  Scheduler not started: {e}")

    yield  # App runs here

    # Shutdown
    try:
        from app.services.scheduler import stop_scheduler
        stop_scheduler()
    except Exception:
        pass
    log_event("system", "ClimaShield shutting down")


app = FastAPI(
    title="ClimaShield API",
    description=(
        "AI Parametric Insurance Platform – Protects gig workers and farmers "
        "from environmental disruptions (rain, floods, extreme heat, pollution). "
        "Phase 4: Production-ready with automated monitoring, simulation, and testing."
    ),
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routes
app.include_router(router)
app.include_router(admin_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
