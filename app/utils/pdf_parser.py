"""PDF text extraction using PyMuPDF (fitz).

This module is the single place responsible for turning raw PDF bytes
into clean plain-text that downstream services can consume.
"""

from __future__ import annotations

import re
import logging

import fitz  # PyMuPDF

from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


class PDFExtractionError(Exception):
    """Raised when text extraction from a PDF fails."""


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract and clean text from raw PDF bytes.

    Args:
        pdf_bytes: The raw bytes of a PDF file.

    Returns:
        Cleaned plain-text content of the PDF.

    Raises:
        HTTPException 422: If the file cannot be opened as a valid PDF.
        HTTPException 422: If the PDF contains no extractable text.
    """
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    except Exception as exc:
        logger.warning("Failed to open PDF: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="The uploaded file could not be parsed as a valid PDF.",
        ) from exc

    raw_pages: list[str] = []
    for page_num, page in enumerate(doc, start=1):
        try:
            raw_pages.append(page.get_text("text"))
        except Exception as exc:
            logger.warning("Failed to extract text from page %d: %s", page_num, exc)

    doc.close()

    merged = "\n".join(raw_pages)
    cleaned = _clean_text(merged)

    if not cleaned:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="The PDF contains no extractable text (it may be image-only or empty).",
        )

    return cleaned


def _clean_text(raw: str) -> str:
    """Normalise whitespace and strip artefacts from extracted text.

    - Collapses runs of 3+ newlines into two (preserves paragraph breaks).
    - Replaces multiple spaces / tabs with a single space.
    - Strips leading / trailing whitespace from every line.
    """
    # Collapse excessive blank lines (keep at most one blank line)
    text = re.sub(r"\n{3,}", "\n\n", raw)
    # Replace tabs and multiple spaces with a single space
    text = re.sub(r"[^\S\n]+", " ", text)
    # Strip each line individually
    text = "\n".join(line.strip() for line in text.splitlines())
    # Final trim
    return text.strip()
