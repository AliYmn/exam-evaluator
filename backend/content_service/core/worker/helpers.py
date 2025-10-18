"""
Task helpers for Celery background processing
PDF extraction, progress tracking utilities
"""

import base64
import io
from pypdf import PdfReader

from libs.cache.progress_tracker import ProgressTracker


def decode_pdf_base64(pdf_base64: str) -> bytes:
    """
    Decode base64-encoded PDF to bytes.

    Args:
        pdf_base64: Base64 encoded PDF string

    Returns:
        PDF bytes
    """
    return base64.b64decode(pdf_base64)


def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    """
    Extract all text from PDF bytes.

    Args:
        pdf_bytes: PDF file content as bytes

    Returns:
        Extracted text as string

    Raises:
        ValueError: If no text could be extracted
        Exception: If PDF reading fails
    """
    try:
        # Create BytesIO object from bytes
        pdf_stream = io.BytesIO(pdf_bytes)

        # Read PDF from stream
        reader = PdfReader(pdf_stream)
        text = ""

        for page in reader.pages:
            text += page.extract_text() + "\n"

        if not text.strip():
            raise ValueError("No text could be extracted from PDF")

        return text.strip()

    except Exception as e:
        raise Exception(f"Failed to extract text from PDF: {str(e)}")


class ProgressReporter:
    """
    Helper class for reporting progress updates.
    Reduces duplication in task code.
    """

    def __init__(self, evaluation_id: str, student_response_id: int = None):
        self.evaluation_id = evaluation_id
        self.student_response_id = student_response_id

    def report_evaluation_progress(self, percentage: float, message: str, status: str = "processing", **kwargs):
        """
        Report progress for answer key evaluation.

        Args:
            percentage: Progress percentage (0-100)
            message: Progress message
            status: Status ("processing", "completed", "failed")
            **kwargs: Additional fields (e.g., total_questions)
        """
        ProgressTracker.set_evaluation_progress(
            evaluation_id=self.evaluation_id, percentage=percentage, message=message, status=status, **kwargs
        )

    def report_student_progress(
        self,
        percentage: float,
        message: str,
        status: str = "processing",
        total_questions: int = 0,
        evaluated_questions: int = 0,
    ):
        """
        Report progress for student evaluation.

        Args:
            percentage: Progress percentage (0-100)
            message: Progress message
            status: Status ("processing", "completed", "failed")
            total_questions: Total number of questions
            evaluated_questions: Number of questions evaluated so far
        """
        if not self.student_response_id:
            raise ValueError("student_response_id required for student progress")

        ProgressTracker.set_student_progress(
            student_response_id=self.student_response_id,
            evaluation_id=self.evaluation_id,
            percentage=percentage,
            message=message,
            status=status,
            total_questions=total_questions,
            evaluated_questions=evaluated_questions,
        )
