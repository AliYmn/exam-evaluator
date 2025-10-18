"""
Content API Router - Exam Evaluation Endpoints
Clean, dependency-injected routes with reusable helpers
"""

from fastapi import APIRouter, Depends, UploadFile, File, Form
from fastapi.responses import StreamingResponse

from content_service.api.v1.content.schemas import (
    AnswerKeyUploadResponse,
    ExamDetailResponse,
    ExamListResponse,
    StudentAnswerUploadResponse,
    StudentListItem,
    StudentDetailResponse,
    ChatRequest,
    ChatResponse,
)
from content_service.api.v1.content.dependencies import (
    get_content_service,
    get_current_user,
    get_current_user_from_query_token,
)
from content_service.api.v1.content.sse_helpers import create_progress_stream
from content_service.core.services.service import ContentService
from libs.models.user import User
from libs import ExceptionBase, ErrorCode

router = APIRouter(tags=["Exam Evaluation"], prefix="/exam")


@router.post("/upload-answer-key", response_model=AnswerKeyUploadResponse)
async def upload_answer_key(
    exam_title: str = Form(..., min_length=3, max_length=255),
    answer_key: UploadFile = File(..., description="Answer key PDF file"),
    current_user: User = Depends(get_current_user),
    content_service: ContentService = Depends(get_content_service),
):
    """
    Upload answer key PDF and parse it using AI.
    Triggers background Celery task for processing.
    """
    # Validate PDF file type
    if not answer_key.filename.lower().endswith(".pdf"):
        raise ExceptionBase(ErrorCode.INVALID_FILE_TYPE)

    return await content_service.upload_answer_key(exam_title, answer_key, current_user.id)


@router.get("/{evaluation_id}", response_model=ExamDetailResponse)
async def get_exam_detail(
    evaluation_id: str,
    current_user: User = Depends(get_current_user),
    content_service: ContentService = Depends(get_content_service),
):
    """Get exam details including progress, status, and questions."""
    return await content_service.get_exam_detail(evaluation_id, current_user.id)


@router.get("/list/all", response_model=ExamListResponse)
async def get_all_exams(
    current_user: User = Depends(get_current_user),
    content_service: ContentService = Depends(get_content_service),
):
    """Get all exams for the authenticated user."""
    return await content_service.get_all_exams(current_user.id)


@router.post("/{evaluation_id}/upload-student-sheet", response_model=StudentAnswerUploadResponse)
async def upload_student_sheet(
    evaluation_id: str,
    student_name: str = Form(..., min_length=2, max_length=255),
    student_sheet: UploadFile = File(..., description="Student answer sheet PDF file"),
    current_user: User = Depends(get_current_user),
    content_service: ContentService = Depends(get_content_service),
):
    """
    Upload student answer sheet for evaluation.
    Triggers background Celery task for processing.
    """
    # Validate PDF file type
    if not student_sheet.filename.lower().endswith(".pdf"):
        raise ExceptionBase(ErrorCode.INVALID_FILE_TYPE)

    return await content_service.upload_student_sheet(evaluation_id, student_name, student_sheet, current_user.id)


@router.get("/{evaluation_id}/students", response_model=list[StudentListItem])
async def get_exam_students(
    evaluation_id: str,
    current_user: User = Depends(get_current_user),
    content_service: ContentService = Depends(get_content_service),
):
    """Get list of students who uploaded answer sheets for this exam."""
    return await content_service.get_exam_students(evaluation_id, current_user.id)


@router.get("/student/{student_response_id}", response_model=StudentDetailResponse)
async def get_student_detail(
    student_response_id: int,
    current_user: User = Depends(get_current_user),
    content_service: ContentService = Depends(get_content_service),
):
    """Get detailed evaluation results for a specific student."""
    return await content_service.get_student_detail(student_response_id, current_user.id)


@router.post("/student/{student_response_id}/chat", response_model=ChatResponse)
async def chat_about_student(
    student_response_id: int,
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_user),
    content_service: ContentService = Depends(get_content_service),
):
    """
    Chat with AI about student performance.
    Context-aware responses based on student's answers and scores.
    """
    # Convert Pydantic models to dicts for service layer
    chat_history = [{"role": msg.role, "content": msg.content} for msg in chat_request.chat_history]

    answer = await content_service.chat_with_student_context(
        student_response_id=student_response_id,
        question=chat_request.question,
        chat_history=chat_history,
        user_id=current_user.id,
    )

    return ChatResponse(answer=answer)


@router.get("/{evaluation_id}/progress-stream")
async def stream_evaluation_progress(
    evaluation_id: str,
    token: str,  # Query parameter (EventSource limitation)
    _user: User = Depends(get_current_user_from_query_token),
):
    """
    Server-Sent Events (SSE) endpoint for real-time evaluation progress.

    Note: Token is passed as query parameter because EventSource doesn't support custom headers.
    """
    return StreamingResponse(
        create_progress_stream(
            resource_type="evaluation",
            resource_id=evaluation_id,
            max_duration_seconds=300,  # 5 minutes
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/student/{student_response_id}/progress-stream")
async def stream_student_progress(
    student_response_id: int,
    token: str,  # Query parameter (EventSource limitation)
    _user: User = Depends(get_current_user_from_query_token),
):
    """
    Server-Sent Events (SSE) endpoint for real-time student evaluation progress.

    Note: Token is passed as query parameter because EventSource doesn't support custom headers.
    """
    return StreamingResponse(
        create_progress_stream(
            resource_type="student_response",
            resource_id=str(student_response_id),
            max_duration_seconds=600,  # 10 minutes
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
