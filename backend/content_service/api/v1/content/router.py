from typing import Annotated
import asyncio
import json
from fastapi import APIRouter, Depends, Header, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

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
from content_service.core.services.service import ContentService
from libs.db.db import get_async_db
from libs.service.auth import AuthService
from libs.cache.progress_tracker import ProgressTracker
from libs import ExceptionBase, ErrorCode

router = APIRouter(tags=["Exam Evaluation"], prefix="/exam")


def get_content_service(db: AsyncSession = Depends(get_async_db)) -> ContentService:
    return ContentService(db)


def get_auth_service(db: AsyncSession = Depends(get_async_db)) -> AuthService:
    return AuthService(db)


@router.post("/upload-answer-key", response_model=AnswerKeyUploadResponse)
async def upload_answer_key(
    authorization: Annotated[str | None, Header()] = None,
    exam_title: str = Form(..., min_length=3, max_length=255),
    answer_key: UploadFile = File(..., description="Answer key PDF file"),
    content_service: ContentService = Depends(get_content_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Upload answer key PDF and parse it using OpenAI.

    Steps:
    1. Validate user authentication
    2. Save PDF to uploads folder
    3. Trigger Celery task to:
       - Extract text from PDF
       - Send to OpenAI for parsing
       - Save structured Q&A to database
    4. Return evaluation ID for tracking
    """
    # Validate authentication
    if not authorization:
        raise ExceptionBase(ErrorCode.UNAUTHORIZED)

    # Validate PDF file type
    if not answer_key.filename.lower().endswith(".pdf"):
        raise ExceptionBase(ErrorCode.INVALID_FILE_TYPE)

    # Get user from token
    user = await auth_service.get_user_from_token(authorization)
    return await content_service.upload_answer_key(exam_title, answer_key, user.id)


@router.get("/{evaluation_id}", response_model=ExamDetailResponse)
async def get_exam_detail(
    evaluation_id: str,
    authorization: Annotated[str | None, Header()] = None,
    content_service: ContentService = Depends(get_content_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Get exam details including progress, status, and questions.
    """
    # Validate authentication
    if not authorization:
        raise ExceptionBase(ErrorCode.UNAUTHORIZED)

    # Get user from token
    user = await auth_service.get_user_from_token(authorization)
    return await content_service.get_exam_detail(evaluation_id, user.id)


@router.get("/list/all", response_model=ExamListResponse)
async def get_all_exams(
    authorization: Annotated[str | None, Header()] = None,
    content_service: ContentService = Depends(get_content_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Get all exams for the authenticated user.
    """
    # Validate authentication
    if not authorization:
        raise ExceptionBase(ErrorCode.UNAUTHORIZED)

    # Get user from token
    user = await auth_service.get_user_from_token(authorization)
    return await content_service.get_all_exams(user.id)


@router.post("/{evaluation_id}/upload-student-sheet", response_model=StudentAnswerUploadResponse)
async def upload_student_sheet(
    evaluation_id: str,
    authorization: Annotated[str | None, Header()] = None,
    student_name: str = Form(..., min_length=2, max_length=255),
    student_sheet: UploadFile = File(..., description="Student answer sheet PDF file"),
    content_service: ContentService = Depends(get_content_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Upload student answer sheet for evaluation.

    Steps:
    1. Validate user authentication and ownership of exam
    2. Validate PDF file type
    3. Trigger Celery task to:
       - Extract text from student PDF
       - Parse student answers
       - Compare with answer key
       - Generate evaluation
    4. Return student response ID for tracking
    """
    # Validate authentication
    if not authorization:
        raise ExceptionBase(ErrorCode.UNAUTHORIZED)

    # Validate PDF file type
    if not student_sheet.filename.lower().endswith(".pdf"):
        raise ExceptionBase(ErrorCode.INVALID_FILE_TYPE)

    # Get user from token
    user = await auth_service.get_user_from_token(authorization)
    return await content_service.upload_student_sheet(evaluation_id, student_name, student_sheet, user.id)


@router.get("/{evaluation_id}/students", response_model=list[StudentListItem])
async def get_exam_students(
    evaluation_id: str,
    authorization: Annotated[str | None, Header()] = None,
    content_service: ContentService = Depends(get_content_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Get list of students who uploaded answer sheets for this exam.

    Returns:
        List of students with their scores and status
    """
    # Verify token and get user
    if not authorization:
        raise ExceptionBase(ErrorCode.INVALID_TOKEN)

    user = await auth_service.get_user_from_token(authorization)
    return await content_service.get_exam_students(evaluation_id, user.id)


@router.get("/student/{student_response_id}", response_model=StudentDetailResponse)
async def get_student_detail(
    student_response_id: int,
    authorization: Annotated[str | None, Header()] = None,
    content_service: ContentService = Depends(get_content_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Get detailed evaluation results for a specific student.

    Returns:
        Detailed student results with question-by-question breakdown
    """
    # Verify token and get user
    if not authorization:
        raise ExceptionBase(ErrorCode.INVALID_TOKEN)

    user = await auth_service.get_user_from_token(authorization)
    return await content_service.get_student_detail(student_response_id, user.id)


@router.post("/student/{student_response_id}/chat", response_model=ChatResponse)
async def chat_about_student(
    student_response_id: int,
    chat_request: ChatRequest,
    authorization: Annotated[str | None, Header()] = None,
    content_service: ContentService = Depends(get_content_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Chat with AI about student performance.

    Provides context-aware responses based on:
    - Student's answers
    - Expected answers
    - Scores and feedback
    - Previous chat history

    Returns:
        AI response about student performance
    """
    # Verify token and get user
    if not authorization:
        raise ExceptionBase(ErrorCode.INVALID_TOKEN)

    user = await auth_service.get_user_from_token(authorization)

    # Convert Pydantic models to dicts for service layer
    chat_history = [{"role": msg.role, "content": msg.content} for msg in chat_request.chat_history]

    answer = await content_service.chat_with_student_context(
        student_response_id=student_response_id,
        question=chat_request.question,
        chat_history=chat_history,
        user_id=user.id,
    )

    return ChatResponse(answer=answer)


@router.get("/{evaluation_id}/progress-stream")
async def stream_evaluation_progress(
    evaluation_id: str,
    token: str,  # Query parameter instead of header (EventSource limitation)
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Server-Sent Events (SSE) endpoint for real-time evaluation progress.

    Streams progress updates as the evaluation is being processed.
    Client should use EventSource to connect to this endpoint.

    Note: Token is passed as query parameter because EventSource doesn't support custom headers.

    Returns:
        SSE stream with progress updates
    """
    # Verify token from query parameter
    if not token:
        raise ExceptionBase(ErrorCode.INVALID_TOKEN)

    # Add "Bearer " prefix if not present
    auth_token = token if token.startswith("Bearer ") else f"Bearer {token}"
    await auth_service.get_user_from_token(auth_token)

    async def event_generator():
        """Generate SSE events with progress updates."""
        try:
            # Send initial connection message
            yield f"data: {json.dumps({'type': 'connected', 'message': 'Connected to progress stream'})}\n\n"

            # Poll Redis for progress updates
            last_progress = None
            max_iterations = 300  # 5 minutes max (300 * 1 second)
            iteration = 0

            while iteration < max_iterations:
                # Get current progress from Redis
                progress_data = ProgressTracker.get_progress("evaluation", evaluation_id)

                if progress_data:
                    # Only send if progress changed
                    if progress_data != last_progress:
                        yield f"data: {json.dumps(progress_data)}\n\n"
                        last_progress = progress_data

                    # If completed or failed, send final message and close
                    if progress_data.get("status") in ["completed", "failed"]:
                        yield f"data: {json.dumps({'type': 'done', 'status': progress_data.get('status')})}\n\n"
                        break

                # Wait before next poll
                await asyncio.sleep(1)
                iteration += 1

            # If max iterations reached, send timeout message
            if iteration >= max_iterations:
                yield f"data: {json.dumps({'type': 'timeout', 'message': 'Stream timeout'})}\n\n"

        except Exception as e:
            print(f"SSE stream error: {str(e)}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )


@router.get("/student/{student_response_id}/progress-stream")
async def stream_student_progress(
    student_response_id: int,
    token: str,  # Query parameter instead of header (EventSource limitation)
    auth_service: AuthService = Depends(get_auth_service),
):
    """
    Server-Sent Events (SSE) endpoint for real-time student evaluation progress.

    Streams progress updates as the student's answers are being evaluated.
    Client should use EventSource to connect to this endpoint.

    Note: Token is passed as query parameter because EventSource doesn't support custom headers.

    Returns:
        SSE stream with progress updates
    """
    # Verify token from query parameter
    if not token:
        raise ExceptionBase(ErrorCode.INVALID_TOKEN)

    # Add "Bearer " prefix if not present
    auth_token = token if token.startswith("Bearer ") else f"Bearer {token}"
    await auth_service.get_user_from_token(auth_token)

    async def event_generator():
        """Generate SSE events with progress updates."""
        try:
            # Send initial connection message
            yield f"data: {json.dumps({'type': 'connected', 'message': 'Connected to student progress stream'})}\n\n"

            # Poll Redis for progress updates
            last_progress = None
            max_iterations = 600  # 10 minutes max (600 * 1 second)
            iteration = 0

            while iteration < max_iterations:
                # Get current progress from Redis
                progress_data = ProgressTracker.get_progress("student_response", str(student_response_id))

                if progress_data:
                    # Only send if progress changed
                    if progress_data != last_progress:
                        yield f"data: {json.dumps(progress_data)}\n\n"
                        last_progress = progress_data

                    # If completed or failed, send final message and close
                    if progress_data.get("status") in ["completed", "failed"]:
                        yield f"data: {json.dumps({'type': 'done', 'status': progress_data.get('status')})}\n\n"
                        break

                # Wait before next poll
                await asyncio.sleep(1)
                iteration += 1

            # If max iterations reached, send timeout message
            if iteration >= max_iterations:
                yield f"data: {json.dumps({'type': 'timeout', 'message': 'Stream timeout'})}\n\n"

        except Exception as e:
            print(f"SSE stream error: {str(e)}")
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )
