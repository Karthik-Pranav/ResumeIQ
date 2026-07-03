"""Router for the /analyze endpoint."""

from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.models.schemas import AnalysisResponse
from app.services.analysis_service import analyze_resume
from app.utils.file_helpers import validate_pdf
from app.utils.pdf_parser import extract_text_from_pdf
from app.utils.rate_limiter import rate_limit_dependency

router = APIRouter(prefix="/analyze", tags=["Analysis"])


@router.post(
    "",
    dependencies=[Depends(rate_limit_dependency)],
    response_model=AnalysisResponse,
    summary="Analyse a resume against a job description",
    description=(
        "Upload a PDF resume and provide a job description. "
        "The endpoint returns a match score, strengths, and gaps."
    ),
)
async def analyze(
    resume: UploadFile = File(..., description="PDF resume file"),
    job_description: str = Form(..., description="Target job description text"),
) -> AnalysisResponse:
    """Accept a resume PDF and job description, return analysis results."""
    pdf_bytes = await validate_pdf(resume)
    resume_text = extract_text_from_pdf(pdf_bytes)
    result = await analyze_resume(resume_text, job_description)
    return result
