"""Utility helpers for file validation and text extraction."""

import os

from fastapi import HTTPException, UploadFile, status


ALLOWED_CONTENT_TYPES = {"application/pdf"}
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "5"))
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# The PDF specification requires all PDF files to start with this header.
_PDF_MAGIC = b"%PDF"


async def validate_pdf(file: UploadFile) -> bytes:
    """Validate that the uploaded file is a PDF within size limits.

    Checks performed (in order):
        1. MIME content-type must be ``application/pdf``.
        2. File size must be within the configured limit.
        3. File content must start with the ``%PDF`` magic bytes.

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

    # Read in chunks to avoid loading arbitrarily large uploads into memory.
    # If the limit is exceeded mid-stream we reject immediately.
    _READ_CHUNK = 64 * 1024  # 64 KB
    chunks: list[bytes] = []
    total_size = 0

    while True:
        chunk = await file.read(_READ_CHUNK)
        if not chunk:
            break
        total_size += len(chunk)
        if total_size > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds the {MAX_FILE_SIZE_MB} MB limit.",
            )
        chunks.append(chunk)

    contents = b"".join(chunks)

    # Defence-in-depth: verify PDF magic bytes so a spoofed content-type
    # with non-PDF content is rejected before reaching PyMuPDF.
    if not contents[:4].startswith(_PDF_MAGIC):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="The uploaded file is not a valid PDF (missing PDF header).",
        )

    return contents
