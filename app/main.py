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
# CORS — allow all origins during development; tighten for production.
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],            # TODO: restrict in production
    allow_credentials=True,
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