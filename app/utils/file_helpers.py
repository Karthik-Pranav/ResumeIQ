"""Utility helpers for file validation and text extraction."""

from fastapi import HTTPException, UploadFile, status


ALLOWED_CONTENT_TYPES = {"application/pdf"}
MAX_FILE_SIZE_MB = 5
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024


async def validate_pdf(file: UploadFile) -> bytes:
    """Validate that the uploaded file is a PDF within size limits.

    Args:
        file: The uploaded file from the request.

    Returns:
        The raw bytes of the validated PDF.

    Raises:
        HTTPException: If the file is not a PDF or exceeds the size limit.
    """
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid file type '{file.content_type}'. Only PDF files are accepted.",
        )

    contents = await file.read()

    if len(contents) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds the {MAX_FILE_SIZE_MB} MB limit.",
        )

    return contents



