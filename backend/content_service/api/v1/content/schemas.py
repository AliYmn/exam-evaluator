from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional


class EvaluationStatus(str, Enum):
    PENDING = "pending"
    PARSING = "parsing"
    COMPLETED = "completed"
    FAILED = "failed"


class AnswerKeyUploadRequest(BaseModel):
    """Request schema for uploading answer key"""

    exam_title: str = Field(..., min_length=3, max_length=255, description="Title of the exam")


class AnswerKeyUploadResponse(BaseModel):
    """Response after uploading answer key"""

    evaluation_id: str
    status: EvaluationStatus
    message: str
    total_questions: Optional[int] = None
    max_possible_score: Optional[float] = None


class ExamUploadResponse(BaseModel):
    evaluation_id: str
    status: EvaluationStatus
    message: str


class QuestionDetail(BaseModel):
    """Question detail schema"""

    number: int
    question_text: str
    expected_answer: str
    max_score: Optional[float] = 10
    keywords: Optional[list[str]] = []


class ExamDetailResponse(BaseModel):
    """Exam detail response with progress and questions"""

    evaluation_id: str
    exam_title: str
    status: EvaluationStatus
    progress_percentage: float
    current_message: str
    total_questions: Optional[int] = None
    max_possible_score: Optional[float] = None
    questions: Optional[list[QuestionDetail]] = None
    error_message: Optional[str] = None
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class ExamListItem(BaseModel):
    """Exam list item schema"""

    evaluation_id: str
    exam_title: str
    status: EvaluationStatus
    progress_percentage: float
    total_questions: Optional[int] = None
    created_at: str

    class Config:
        from_attributes = True


class ExamListResponse(BaseModel):
    """List of exams"""

    exams: list[ExamListItem]
    total: int


class StudentAnswerUploadResponse(BaseModel):
    """Response after uploading student answer sheet"""

    student_response_id: int
    evaluation_id: str
    student_name: str
    status: str
    message: str


class StudentListItem(BaseModel):
    """Student list item for exam detail page"""

    student_response_id: int
    student_id: str
    student_name: str
    total_score: float
    max_score: float
    percentage: float
    status: str  # "pending", "processing", "completed", "failed"
    created_at: str

    class Config:
        from_attributes = True


class QuestionResponseDetail(BaseModel):
    """Detailed response for a single question"""

    question_number: int
    question_text: Optional[str] = None
    expected_answer: str
    student_answer: str
    score: float
    max_score: float
    feedback: str
    is_correct: bool

    class Config:
        from_attributes = True


class StudentDetailResponse(BaseModel):
    """Full student evaluation details"""

    student_response_id: int
    student_id: str
    student_name: str
    total_score: float
    max_score: float
    percentage: float
    summary: Optional[str] = None
    strengths: Optional[list[str]] = None
    weaknesses: Optional[list[str]] = None
    topic_gaps: Optional[list[str]] = None
    questions: list[QuestionResponseDetail]
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class ChatMessage(BaseModel):
    """Chat message"""

    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    """Request for chat about student"""

    question: str
    chat_history: Optional[list[ChatMessage]] = []


class ChatResponse(BaseModel):
    """Response from chat"""

    answer: str
