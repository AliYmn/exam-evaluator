import uuid
import base64
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile

from sqlalchemy import select
from libs.models.exam import Evaluation, EvaluationStatus, StudentResponse
from libs import ExceptionBase, ErrorCode
from content_service.api.v1.content.schemas import (
    AnswerKeyUploadResponse,
    ExamDetailResponse,
    ExamListResponse,
    ExamListItem,
    QuestionDetail,
    StudentAnswerUploadResponse,
)
from content_service.core.worker.tasks import process_answer_key_task, process_student_answer_task


class ContentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def upload_answer_key(self, exam_title: str, answer_key: UploadFile, user_id: int) -> AnswerKeyUploadResponse:
        """
        Upload answer key PDF and trigger background processing.

        Steps:
        1. Generate unique evaluation ID
        2. Read PDF bytes (no disk save)
        3. Create DB record with PENDING status
        4. Trigger Celery task with PDF bytes
        5. Return response
        """
        try:
            # Generate unique evaluation ID
            evaluation_id = f"eval_{uuid.uuid4().hex[:12]}"

            # Read PDF content as bytes
            pdf_bytes = await answer_key.read()

            # Encode bytes to base64 for Celery serialization
            pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")

            # Create DB record
            evaluation = Evaluation(
                user_id=user_id,
                evaluation_id=evaluation_id,
                exam_title=exam_title,
                status=EvaluationStatus.PENDING,
                answer_key_filename=answer_key.filename,
                answer_key_path=f"memory://{evaluation_id}",  # Virtual path
                current_message="Answer key uploaded, parsing in progress...",
            )

            self.db.add(evaluation)
            await self.db.commit()
            await self.db.refresh(evaluation)

            # Trigger Celery task with base64 encoded PDF
            process_answer_key_task.delay(evaluation_id, pdf_base64, answer_key.filename)

            return AnswerKeyUploadResponse(
                evaluation_id=evaluation_id,
                status=EvaluationStatus.PENDING,
                message="Answer key uploaded successfully. Processing in background.",
            )

        except Exception:
            await self.db.rollback()
            raise ExceptionBase(ErrorCode.INTERNAL_SERVER_ERROR)

    async def get_exam_detail(self, evaluation_id: str, user_id: int) -> ExamDetailResponse:
        """
        Get detailed information about an exam including progress and questions.
        """
        try:
            # Query evaluation
            result = await self.db.execute(
                select(Evaluation).where(Evaluation.evaluation_id == evaluation_id, Evaluation.user_id == user_id)
            )
            evaluation = result.scalar_one_or_none()

            if not evaluation:
                raise ExceptionBase(ErrorCode.NOT_FOUND)

            # Parse questions from answer_key_data if available
            questions = None
            if (
                evaluation.answer_key_data
                and isinstance(evaluation.answer_key_data, dict)
                and "questions" in evaluation.answer_key_data
            ):
                questions = [QuestionDetail(**q) for q in evaluation.answer_key_data["questions"]]

            return ExamDetailResponse(
                evaluation_id=evaluation.evaluation_id,
                exam_title=evaluation.exam_title or "Untitled Exam",
                status=evaluation.status,
                progress_percentage=evaluation.progress_percentage or 0.0,
                current_message=evaluation.current_message or "",
                total_questions=(
                    evaluation.answer_key_data.get("total_questions")
                    if evaluation.answer_key_data and isinstance(evaluation.answer_key_data, dict)
                    else None
                ),
                max_possible_score=evaluation.max_possible_score,
                questions=questions,
                error_message=evaluation.error_message,
                created_at=evaluation.created_date.isoformat(),
                updated_at=evaluation.updated_date.isoformat(),
            )

        except ExceptionBase:
            raise
        except Exception:
            raise ExceptionBase(ErrorCode.INTERNAL_SERVER_ERROR)

    async def get_all_exams(self, user_id: int) -> ExamListResponse:
        """
        Get all exams for a user.
        """
        try:
            # Query all evaluations for user
            result = await self.db.execute(
                select(Evaluation).where(Evaluation.user_id == user_id).order_by(Evaluation.created_date.desc())
            )
            evaluations = result.scalars().all()

            exams = [
                ExamListItem(
                    evaluation_id=eval.evaluation_id,
                    exam_title=eval.exam_title or "Untitled Exam",
                    status=eval.status,
                    progress_percentage=eval.progress_percentage or 0.0,
                    total_questions=(
                        eval.answer_key_data.get("total_questions")
                        if eval.answer_key_data and isinstance(eval.answer_key_data, dict)
                        else None
                    ),
                    created_at=eval.created_date.isoformat(),
                )
                for eval in evaluations
            ]

            return ExamListResponse(exams=exams, total=len(exams))

        except ExceptionBase:
            raise
        except Exception as e:
            # Log the actual error for debugging
            print(f"Error in get_all_exams: {str(e)}")
            import traceback

            traceback.print_exc()
            raise ExceptionBase(ErrorCode.INTERNAL_SERVER_ERROR)

    async def upload_student_sheet(
        self, evaluation_id: str, student_name: str, student_sheet: UploadFile, user_id: int
    ) -> StudentAnswerUploadResponse:
        """
        Upload student answer sheet and trigger background processing.

        Steps:
        1. Verify evaluation exists and belongs to user
        2. Verify answer key is parsed (status = COMPLETED)
        3. Read PDF bytes
        4. Create StudentResponse DB record
        5. Trigger Celery task with PDF bytes
        6. Return response
        """
        try:
            # Verify evaluation exists and belongs to user
            result = await self.db.execute(
                select(Evaluation).where(Evaluation.evaluation_id == evaluation_id, Evaluation.user_id == user_id)
            )
            evaluation = result.scalar_one_or_none()

            if not evaluation:
                raise ExceptionBase(ErrorCode.NOT_FOUND)

            # Verify answer key is parsed
            if evaluation.status != EvaluationStatus.COMPLETED:
                raise ExceptionBase(ErrorCode.BAD_REQUEST)

            if not evaluation.answer_key_data:
                raise ExceptionBase(ErrorCode.BAD_REQUEST)

            # Read PDF content as bytes
            pdf_bytes = await student_sheet.read()

            # Encode bytes to base64 for Celery serialization
            pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")

            # Generate unique student_id
            student_id = f"student_{uuid.uuid4().hex[:8]}"

            # Create StudentResponse DB record
            student_response = StudentResponse(
                evaluation_id=evaluation.id,
                student_id=student_id,
                student_name=student_name,
                pdf_filename=student_sheet.filename,
                pdf_path=f"memory://{student_id}",  # In-memory processing
                max_score=evaluation.max_possible_score or 0.0,
            )

            self.db.add(student_response)
            await self.db.commit()
            await self.db.refresh(student_response)

            # Trigger Celery task with base64 encoded PDF
            process_student_answer_task.delay(student_response.id, evaluation_id, pdf_base64, student_sheet.filename)

            return StudentAnswerUploadResponse(
                student_response_id=student_response.id,
                evaluation_id=evaluation_id,
                student_name=student_name,
                status="pending",
                message="Student answer sheet uploaded successfully. Processing in background.",
            )

        except ExceptionBase:
            raise
        except Exception as e:
            await self.db.rollback()
            print(f"Error in upload_student_sheet: {str(e)}")
            import traceback

            traceback.print_exc()
            raise ExceptionBase(ErrorCode.INTERNAL_SERVER_ERROR)

    async def get_exam_students(self, evaluation_id: str, user_id: int):
        """
        Get list of students for an exam.

        Args:
            evaluation_id: Evaluation ID
            user_id: User ID (for authorization)

        Returns:
            List of students with their scores and status
        """
        try:
            # Verify evaluation exists and belongs to user
            result = await self.db.execute(
                select(Evaluation).where(Evaluation.evaluation_id == evaluation_id, Evaluation.user_id == user_id)
            )
            evaluation = result.scalar_one_or_none()

            if not evaluation:
                raise ExceptionBase(ErrorCode.NOT_FOUND)

            # Get all students for this evaluation
            result = await self.db.execute(
                select(StudentResponse)
                .where(StudentResponse.evaluation_id == evaluation.id)
                .order_by(StudentResponse.created_date.desc())
            )
            students = result.scalars().all()

            # Determine status for each student based on their data
            from libs.models.exam import QuestionResponse
            from datetime import datetime, timedelta

            student_list = []
            for student in students:
                # Check if there are any question responses
                qr_result = await self.db.execute(
                    select(QuestionResponse).where(QuestionResponse.student_response_id == student.id)
                )
                questions = qr_result.scalars().all()
                has_questions = len(questions) > 0

                # Check if evaluation is completed
                if student.total_score > 0 or student.summary:
                    status = "completed"
                else:
                    # Check for timeout or failure
                    # If created more than 10 minutes ago and still no score, consider it failed
                    time_since_creation = (
                        datetime.utcnow() - student.created_date if student.created_date else timedelta(0)
                    )

                    if time_since_creation > timedelta(minutes=10):
                        # If no questions or all have "Pending evaluation", it's failed
                        if not questions or all(q.feedback == "Pending evaluation" for q in questions):
                            status = "failed"
                        else:
                            status = "processing"
                    else:
                        status = "processing"

                student_list.append(
                    {
                        "student_response_id": student.id,
                        "student_id": student.student_id,
                        "student_name": student.student_name or "Unknown",
                        "total_score": student.total_score,
                        "max_score": student.max_score,
                        "percentage": student.percentage,
                        "status": status,
                        "has_questions": has_questions,
                        "created_at": student.created_date.isoformat() if student.created_date else "",
                    }
                )

            return student_list

        except ExceptionBase:
            raise
        except Exception as e:
            print(f"Error in get_exam_students: {str(e)}")
            import traceback

            traceback.print_exc()
            raise ExceptionBase(ErrorCode.INTERNAL_SERVER_ERROR)

    async def get_student_detail(self, student_response_id: int, user_id: int):
        """
        Get detailed evaluation results for a student.

        Args:
            student_response_id: Student response ID
            user_id: User ID (for authorization)

        Returns:
            Detailed student results with question-by-question breakdown
        """
        try:
            from libs.models.exam import QuestionResponse
            from sqlalchemy.orm import selectinload

            # Get student response with evaluation for authorization (eager load evaluation)
            result = await self.db.execute(
                select(StudentResponse)
                .options(selectinload(StudentResponse.evaluation))
                .join(Evaluation, StudentResponse.evaluation_id == Evaluation.id)
                .where(StudentResponse.id == student_response_id, Evaluation.user_id == user_id)
            )
            student = result.scalar_one_or_none()

            if not student:
                raise ExceptionBase(ErrorCode.NOT_FOUND)

            # Get evaluation separately to avoid lazy loading issues
            evaluation = student.evaluation

            # Get all question responses
            result = await self.db.execute(
                select(QuestionResponse)
                .where(QuestionResponse.student_response_id == student_response_id)
                .order_by(QuestionResponse.question_number)
            )
            question_responses = result.scalars().all()

            # If no question responses yet, create placeholders from answer key
            if not question_responses and evaluation.answer_key_data:
                answer_key_questions = evaluation.answer_key_data.get("questions", [])
                questions = []
                for q in answer_key_questions:
                    questions.append(
                        {
                            "question_number": q.get("number", 0),
                            "question_text": q.get("question_text", ""),
                            "expected_answer": q.get("expected_answer", ""),
                            "student_answer": "[Cevap çıkarılıyor...]",
                            "score": 0.0,
                            "max_score": q.get("max_score", 10),
                            "feedback": "Değerlendirme bekleniyor...",
                            "is_correct": False,
                        }
                    )
            else:
                # Build question details from existing responses
                questions = []
                for qr in question_responses:
                    # Extract additional data if available
                    additional_data = qr.additional_data or {}

                    questions.append(
                        {
                            "question_number": qr.question_number,
                            "question_text": additional_data.get("question_text", ""),
                            "expected_answer": qr.expected_answer,
                            "student_answer": qr.student_answer,
                            "score": qr.score,
                            "max_score": qr.max_score,
                            "feedback": qr.feedback,
                            "is_correct": additional_data.get("is_correct", False),
                        }
                    )

            return {
                "student_response_id": student.id,
                "student_id": student.student_id,
                "student_name": student.student_name or "Unknown",
                "total_score": student.total_score,
                "max_score": student.max_score,
                "percentage": student.percentage,
                "summary": student.summary,
                "strengths": student.strengths or [],
                "weaknesses": student.weaknesses or [],
                "topic_gaps": student.topic_gaps or [],
                "questions": questions,
                "created_at": student.created_date.isoformat() if student.created_date else "",
                "updated_at": student.updated_date.isoformat() if student.updated_date else "",
            }

        except ExceptionBase:
            raise
        except Exception as e:
            print(f"Error in get_student_detail: {str(e)}")
            import traceback

            traceback.print_exc()
            raise ExceptionBase(ErrorCode.INTERNAL_SERVER_ERROR)

    async def chat_with_student_context(
        self, student_response_id: int, question: str, chat_history: list, user_id: int
    ):
        """
        Chat about student performance with AI, using full context.
        Also saves the chat to FollowUpQuestion model.

        Args:
            student_response_id: Student response ID
            question: User's question
            chat_history: Previous messages [{"role": "user/assistant", "content": "..."}]
            user_id: User ID (for authorization)

        Returns:
            AI response text
        """
        try:
            from libs.models.exam import QuestionResponse, FollowUpQuestion

            # Get student response with evaluation for authorization
            result = await self.db.execute(
                select(StudentResponse)
                .join(Evaluation, StudentResponse.evaluation_id == Evaluation.id)
                .where(StudentResponse.id == student_response_id, Evaluation.user_id == user_id)
            )
            student = result.scalar_one_or_none()

            if not student:
                raise ExceptionBase(ErrorCode.NOT_FOUND)

            # Get evaluation
            result = await self.db.execute(select(Evaluation).where(Evaluation.id == student.evaluation_id))
            evaluation = result.scalar_one_or_none()

            # Get all question responses
            result = await self.db.execute(
                select(QuestionResponse)
                .where(QuestionResponse.student_response_id == student_response_id)
                .order_by(QuestionResponse.question_number)
            )
            question_responses = result.scalars().all()

            # Build questions data for context
            questions_data = []
            for qr in question_responses:
                additional_data = qr.additional_data or {}
                questions_data.append(
                    {
                        "number": qr.question_number,
                        "expected_answer": qr.expected_answer,
                        "student_answer": qr.student_answer,
                        "score": qr.score,
                        "max_score": qr.max_score,
                        "feedback": qr.feedback,
                        "is_correct": additional_data.get("is_correct", False),
                    }
                )

            # Call Agent for chat
            from content_service.core.agents import ExamEvaluationAgent

            agent = ExamEvaluationAgent()
            ai_response = agent.chat_about_student(
                question=question,
                student_name=student.student_name or "Unknown",
                total_score=student.total_score,
                max_score=student.max_score,
                percentage=student.percentage,
                summary=student.summary or "",
                questions_data=questions_data,
                chat_history=chat_history,
            )

            # Save to database
            followup = FollowUpQuestion(
                evaluation_id=evaluation.id,
                user_id=user_id,
                student_response_id=student_response_id,
                question=question,
                answer=ai_response,
                context={
                    "student_id": student.student_id,
                    "student_name": student.student_name,
                    "total_score": student.total_score,
                    "percentage": student.percentage,
                },
            )
            self.db.add(followup)
            await self.db.commit()

            return ai_response

        except ExceptionBase:
            raise
        except Exception as e:
            print(f"Error in chat_with_student_context: {str(e)}")
            import traceback

            traceback.print_exc()
            raise ExceptionBase(ErrorCode.INTERNAL_SERVER_ERROR)
