import base64
import io
from pypdf import PdfReader
from content_service.core.worker.config import celery_app
from content_service.core.services.gemini import GeminiService
from libs.db.db import get_db_session_sync
from libs.models.exam import Evaluation, EvaluationStatus, StudentResponse, QuestionResponse
from libs.cache.progress_tracker import ProgressTracker
from sqlalchemy import select


@celery_app.task(name="process_answer_key", bind=True)
def process_answer_key_task(self, evaluation_id: str, pdf_base64: str, filename: str):
    """
    Background task to process answer key PDF.

    Steps:
    1. Decode base64 PDF bytes
    2. Extract text from PDF bytes
    3. Send to Gemini for parsing
    4. Update DB with parsed Q&A data
    5. Update status to COMPLETED or FAILED
    """
    with get_db_session_sync() as db:
        try:
            # Update status to PARSING
            evaluation = db.execute(
                select(Evaluation).where(Evaluation.evaluation_id == evaluation_id)
            ).scalar_one_or_none()

            if not evaluation:
                raise ValueError(f"Evaluation {evaluation_id} not found")

            evaluation.status = EvaluationStatus.PARSING
            evaluation.current_message = "Başlıyor..."
            evaluation.progress_percentage = 5.0
            db.commit()

            # Stream progress to Redis - Step 1
            ProgressTracker.set_evaluation_progress(
                evaluation_id=evaluation_id,
                percentage=5.0,
                message="Cevap anahtarı işleniyor...",
                status="processing",
            )

            # Step 1: Decode base64
            evaluation.current_message = "PDF dosyası okunuyor..."
            evaluation.progress_percentage = 15.0
            db.commit()

            ProgressTracker.set_evaluation_progress(
                evaluation_id=evaluation_id,
                percentage=15.0,
                message="PDF dosyası okunuyor...",
                status="processing",
            )

            pdf_bytes = base64.b64decode(pdf_base64)

            # Step 2: Extract text
            evaluation.current_message = "PDF'den metin çıkarılıyor..."
            evaluation.progress_percentage = 25.0
            db.commit()

            ProgressTracker.set_evaluation_progress(
                evaluation_id=evaluation_id,
                percentage=25.0,
                message="PDF'den metin çıkarılıyor...",
                status="processing",
            )

            pdf_text = extract_text_from_pdf_bytes(pdf_bytes)

            # Step 3: Preparing AI
            evaluation.current_message = "AI ile soru analizi başlıyor..."
            evaluation.progress_percentage = 40.0
            db.commit()

            ProgressTracker.set_evaluation_progress(
                evaluation_id=evaluation_id,
                percentage=40.0,
                message="AI ile soru analizi başlıyor...",
                status="processing",
            )

            # Step 4: Parse with Gemini
            evaluation.current_message = "Sorular AI tarafından ayrıştırılıyor..."
            evaluation.progress_percentage = 60.0
            db.commit()

            ProgressTracker.set_evaluation_progress(
                evaluation_id=evaluation_id,
                percentage=60.0,
                message="Sorular AI tarafından ayrıştırılıyor...",
                status="processing",
            )

            gemini_service = GeminiService()
            parsed_data = gemini_service.parse_answer_key(pdf_text)

            evaluation.current_message = "Veriler kaydediliyor..."
            evaluation.progress_percentage = 85.0
            db.commit()

            # Stream progress to Redis
            ProgressTracker.set_evaluation_progress(
                evaluation_id=evaluation_id,
                percentage=85.0,
                message="Veriler kaydediliyor...",
                status="processing",
                total_questions=parsed_data.get("total_questions", 0),
            )

            # Step 5: Update DB with parsed data
            evaluation.answer_key_data = parsed_data
            evaluation.max_possible_score = parsed_data.get("max_possible_score", 0)

            evaluation.current_message = "Sorular veritabanına kaydedildi!"
            evaluation.progress_percentage = 95.0
            db.commit()

            ProgressTracker.set_evaluation_progress(
                evaluation_id=evaluation_id,
                percentage=95.0,
                message="Sorular veritabanına kaydedildi!",
                status="processing",
                total_questions=parsed_data.get("total_questions", 0),
            )

            evaluation.status = EvaluationStatus.COMPLETED
            evaluation.current_message = (
                f"Cevap anahtarı başarıyla işlendi! {parsed_data.get('total_questions', 0)} soru bulundu."
            )
            evaluation.progress_percentage = 100.0
            db.commit()

            # Stream final progress to Redis
            ProgressTracker.set_evaluation_progress(
                evaluation_id=evaluation_id,
                percentage=100.0,
                message=f"Cevap anahtarı başarıyla işlendi! {parsed_data.get('total_questions', 0)} soru bulundu.",
                status="completed",
                total_questions=parsed_data.get("total_questions", 0),
            )

            return {
                "status": "success",
                "evaluation_id": evaluation_id,
                "total_questions": parsed_data.get("total_questions", 0),
                "max_score": parsed_data.get("max_possible_score", 0),
            }

        except Exception as e:
            # Re-query evaluation in case of error
            evaluation = db.execute(
                select(Evaluation).where(Evaluation.evaluation_id == evaluation_id)
            ).scalar_one_or_none()

            if evaluation:
                evaluation.status = EvaluationStatus.FAILED
                evaluation.error_message = str(e)
                evaluation.current_message = "Failed to parse answer key"
                db.commit()

            # Stream error to Redis
            ProgressTracker.set_evaluation_progress(
                evaluation_id=evaluation_id,
                percentage=0.0,
                message=f"Failed to parse answer key: {str(e)}",
                status="failed",
            )

            raise Exception(f"Failed to process answer key: {str(e)}")


def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    """
    Extract all text from PDF bytes.

    Args:
        pdf_bytes: PDF file content as bytes

    Returns:
        Extracted text as string
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


@celery_app.task(name="process_student_answer", bind=True)
def process_student_answer_task(self, student_response_id: int, evaluation_id: str, pdf_base64: str, filename: str):
    """
    Background task to process student answer sheet.

    Steps:
    1. Decode base64 PDF bytes
    2. Extract text from PDF bytes
    3. Send to Gemini for parsing student answers
    4. Match with answer key questions
    5. Update StudentResponse and create QuestionResponse records
    """
    with get_db_session_sync() as db:
        try:
            # Get student response record
            student_response = db.execute(
                select(StudentResponse).where(StudentResponse.id == student_response_id)
            ).scalar_one_or_none()

            if not student_response:
                raise ValueError(f"StudentResponse {student_response_id} not found")

            # Get evaluation and answer key
            evaluation = db.execute(
                select(Evaluation).where(Evaluation.evaluation_id == evaluation_id)
            ).scalar_one_or_none()

            if not evaluation or not evaluation.answer_key_data:
                raise ValueError(f"Evaluation {evaluation_id} not found or has no answer key")

            # Student is being parsed (no explicit status field needed)
            db.commit()

            # Step 1: Decode base64 and extract text from PDF bytes
            pdf_bytes = base64.b64decode(pdf_base64)
            pdf_text = extract_text_from_pdf_bytes(pdf_bytes)

            # Step 2: Parse student answers with Gemini
            gemini_service = GeminiService()
            total_questions = evaluation.answer_key_data.get("total_questions", 0)
            student_answers = gemini_service.parse_student_answer(pdf_text, total_questions)

            # Step 3: Create QuestionResponse records for each question
            answer_key_questions = evaluation.answer_key_data.get("questions", [])

            for answer_key_q in answer_key_questions:
                # Find matching student answer
                student_answer_text = None
                for student_q in student_answers:
                    if student_q.get("number") == answer_key_q.get("number"):
                        student_answer_text = student_q.get("student_answer", "")
                        break

                if not student_answer_text:
                    student_answer_text = "[No answer provided]"

                # Create QuestionResponse
                question_response = QuestionResponse(
                    student_response_id=student_response.id,
                    question_number=answer_key_q.get("number"),
                    student_answer=student_answer_text,
                    expected_answer=answer_key_q.get("expected_answer"),
                    score=0.0,  # Will be evaluated later
                    max_score=answer_key_q.get("max_score", 10),
                    feedback="Pending evaluation",
                )
                db.add(question_response)

            # Student response parsed - ready for evaluation
            student_response.total_score = 0.0  # Will be calculated after evaluation
            db.commit()

            # Trigger evaluation task
            evaluate_student_responses_task.delay(student_response_id, evaluation_id)

            return {
                "status": "success",
                "student_response_id": student_response_id,
                "total_questions": len(answer_key_questions),
            }

        except Exception as e:
            # Re-query student response in case of error
            student_response = db.execute(
                select(StudentResponse).where(StudentResponse.id == student_response_id)
            ).scalar_one_or_none()

            # Mark as failed by leaving it with incomplete data
            print(f"Error in process_student_answer_task: {str(e)}")
            import traceback

            traceback.print_exc()
            raise Exception(f"Failed to process student answer: {str(e)}")


@celery_app.task(name="evaluate_student_responses", bind=True)
def evaluate_student_responses_task(self, student_response_id: int, evaluation_id: str):
    """
    Background task to evaluate student responses using AI.

    Steps:
    1. Get all QuestionResponse records for this student
    2. Get answer key data from Evaluation
    3. For each question:
       - Send to Gemini for evaluation
       - Get score, feedback
       - Update QuestionResponse
    4. Calculate total score
    5. Update StudentResponse with final score
    """
    with get_db_session_sync() as db:
        try:
            # Get student response
            student_response = db.execute(
                select(StudentResponse).where(StudentResponse.id == student_response_id)
            ).scalar_one_or_none()

            if not student_response:
                raise ValueError(f"StudentResponse {student_response_id} not found")

            # Get evaluation and answer key
            evaluation = db.execute(
                select(Evaluation).where(Evaluation.evaluation_id == evaluation_id)
            ).scalar_one_or_none()

            if not evaluation or not evaluation.answer_key_data:
                raise ValueError(f"Evaluation {evaluation_id} not found or has no answer key")

            # Student is being evaluated (no explicit status field needed)
            db.commit()

            # Get all question responses for this student
            question_responses = (
                db.execute(select(QuestionResponse).where(QuestionResponse.student_response_id == student_response_id))
                .scalars()
                .all()
            )

            if not question_responses:
                raise ValueError(f"No question responses found for student {student_response_id}")

            # Get answer key questions
            answer_key_questions = evaluation.answer_key_data.get("questions", [])
            answer_key_map = {q.get("number"): q for q in answer_key_questions}

            # Initialize Gemini service
            gemini_service = GeminiService()
            total_score = 0.0
            total_questions = len(question_responses)

            # Initial progress
            ProgressTracker.set_student_progress(
                student_response_id=student_response_id,
                evaluation_id=evaluation_id,
                percentage=0.0,
                message=f"Starting evaluation of {total_questions} questions...",
                status="processing",
                total_questions=total_questions,
                evaluated_questions=0,
            )

            # Evaluate each question
            for idx, qr in enumerate(question_responses, 1):
                # Get answer key for this question
                answer_key = answer_key_map.get(qr.question_number)
                if not answer_key:
                    continue

                # Evaluate with Gemini
                evaluation_result = gemini_service.evaluate_answer(
                    question_number=qr.question_number,
                    question_text=answer_key.get("question_text", ""),
                    expected_answer=qr.expected_answer,
                    student_answer=qr.student_answer,
                    max_score=qr.max_score,
                    keywords=answer_key.get("keywords", []),
                )

                # Update QuestionResponse
                qr.score = evaluation_result["score"]
                qr.feedback = evaluation_result["feedback"]
                qr.additional_data = {
                    "is_correct": evaluation_result.get("is_correct", False),
                }

                total_score += evaluation_result["score"]

                # Update progress after each question (0-70% range for questions)
                question_progress = (idx / total_questions) * 70.0
                ProgressTracker.set_student_progress(
                    student_response_id=student_response_id,
                    evaluation_id=evaluation_id,
                    percentage=question_progress,
                    message=f"Evaluated question {idx}/{total_questions}",
                    status="processing",
                    total_questions=total_questions,
                    evaluated_questions=idx,
                )

            # Update student response with final score
            student_response.total_score = total_score
            # Status is "completed" when total_score > 0 and summary exists

            # Calculate performance summary
            max_possible = sum(qr.max_score for qr in question_responses)
            percentage = (total_score / max_possible * 100) if max_possible > 0 else 0

            # Update max_score and percentage fields
            student_response.max_score = max_possible
            student_response.percentage = round(percentage, 2)

            student_response.performance_summary = {
                "total_score": total_score,
                "max_possible_score": max_possible,
                "percentage": round(percentage, 2),
                "total_questions": len(question_responses),
                "correct_answers": sum(
                    1 for qr in question_responses if qr.additional_data and qr.additional_data.get("is_correct")
                ),
            }

            # Progress: Analyzing performance (70-90%)
            ProgressTracker.set_student_progress(
                student_response_id=student_response_id,
                evaluation_id=evaluation_id,
                percentage=75.0,
                message="Analyzing strengths and weaknesses...",
                status="processing",
                total_questions=total_questions,
                evaluated_questions=total_questions,
            )

            # Analyze strengths and weaknesses
            questions_data = []
            for qr in question_responses:
                questions_data.append(
                    {
                        "question_number": qr.question_number,
                        "score": qr.score,
                        "max_score": qr.max_score,
                        "expected_answer": qr.expected_answer,
                        "student_answer": qr.student_answer,
                        "feedback": qr.feedback,
                        "is_correct": qr.additional_data.get("is_correct", False) if qr.additional_data else False,
                    }
                )

            performance_analysis = gemini_service.analyze_student_performance(
                student_name=student_response.student_name or "Öğrenci",
                total_score=total_score,
                max_score=max_possible,
                percentage=percentage,
                questions_data=questions_data,
            )

            student_response.strengths = performance_analysis.get("strengths", [])
            student_response.weaknesses = performance_analysis.get("weaknesses", [])

            db.commit()

            # Final progress: Completed (100%)
            ProgressTracker.set_student_progress(
                student_response_id=student_response_id,
                evaluation_id=evaluation_id,
                percentage=100.0,
                message="Evaluation completed successfully!",
                status="completed",
                total_questions=total_questions,
                evaluated_questions=total_questions,
            )

            return {
                "status": "success",
                "student_response_id": student_response_id,
                "total_score": total_score,
                "max_possible_score": max_possible,
                "percentage": percentage,
            }

        except Exception as e:
            # Re-query student response in case of error
            student_response = db.execute(
                select(StudentResponse).where(StudentResponse.id == student_response_id)
            ).scalar_one_or_none()

            # Stream error to Redis
            ProgressTracker.set_student_progress(
                student_response_id=student_response_id,
                evaluation_id=evaluation_id,
                percentage=0.0,
                message=f"Evaluation failed: {str(e)}",
                status="failed",
            )

            # Mark as failed by leaving it with incomplete data
            print(f"Error in evaluate_student_responses_task: {str(e)}")
            import traceback

            traceback.print_exc()
            raise Exception(f"Failed to evaluate student responses: {str(e)}")
