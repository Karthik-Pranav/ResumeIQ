"""ResumeIQ — FastAPI application entry-point."""

from dotenv import load_dotenv
import os

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import analysis_router

app = FastAPI(
    title="ResumeIQ",
    description="AI-powered resume analysis API that scores resumes against job descriptions.",
    version="0.1.0",
)

# ---------------------------------------------------------------------------
# CORS — reads ALLOWED_ORIGINS from .env (comma-separated).
# Defaults to ["*"] for development; set explicit origins in production.
# allow_credentials is only enabled when specific origins are listed,
# because the CORS spec forbids credentials with wildcard origins.
# ---------------------------------------------------------------------------
_raw_origins = os.getenv("ALLOWED_ORIGINS", "*").strip()
_allowed_origins: list[str] = (
    ["*"] if _raw_origins == "*"
    else [o.strip() for o in _raw_origins.split(",") if o.strip()]
)
_use_credentials = _allowed_origins != ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=_use_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(analysis_router.router)


@app.get("/", tags=["Health"])
async def health_check() -> dict:
    """Simple health-check endpoint."""
    return {"status": "ok", "app": "ResumeIQ", "version": "0.1.0"}