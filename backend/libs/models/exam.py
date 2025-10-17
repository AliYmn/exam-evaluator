from sqlalchemy import Column, String, Integer, Float, Text, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
import enum

from libs.models.base import BaseModel


class EvaluationStatus(str, enum.Enum):
    """Status of exam evaluation"""

    PENDING = "pending"
    PARSING = "parsing"
    EVALUATING = "evaluating"
    COMPLETED = "completed"
    FAILED = "failed"


class Evaluation(BaseModel):
    """
    Main evaluation record - represents one exam evaluation session.

    One evaluation can have:
    - 1 answer key PDF
    - Multiple student response PDFs
    """

    __tablename__ = "evaluations"

    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Unique identifier for this evaluation
    evaluation_id = Column(String(100), unique=True, nullable=False, index=True)

    # Exam Title
    exam_title = Column(String(255), nullable=True)

    # Status & Progress
    status = Column(SQLEnum(EvaluationStatus), default=EvaluationStatus.PENDING, nullable=False, index=True)
    progress_percentage = Column(Float, default=0.0)  # 0-100
    current_message = Column(String(255), nullable=True)  # "Parsing PDFs...", "Evaluating student 2/5"
    error_message = Column(Text, nullable=True)

    # File Information
    answer_key_filename = Column(String(255), nullable=False)
    answer_key_path = Column(String(500), nullable=False)  # Storage path

    # Parsed Answer Key Data (JSON)
    # Format: {"questions": [{"number": 1, "expected_answer": "...", "max_score": 10}, ...]}
    answer_key_data = Column(JSON, nullable=True)

    # Student Count
    total_students = Column(Integer, default=0)
    completed_students = Column(Integer, default=0)

    # Scores
    average_score = Column(Float, nullable=True)
    max_possible_score = Column(Float, nullable=True)

    # Relationships
    user = relationship("User", backref="evaluations")
    students = relationship("StudentResponse", back_populates="evaluation", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Evaluation(id={self.id}, evaluation_id={self.evaluation_id}, status={self.status}, students={self.total_students})>"


class StudentResponse(BaseModel):
    """
    Complete response and evaluation for one student.

    Contains:
    - Student info
    - Overall scores
    - Summary feedback
    - All question responses
    """

    __tablename__ = "student_responses"

    # Foreign Keys
    evaluation_id = Column(Integer, ForeignKey("evaluations.id"), nullable=False, index=True)

    # Student Identification
    student_id = Column(String(100), nullable=False, index=True)  # Unique per evaluation
    student_name = Column(String(255), nullable=True)  # Extracted from PDF or filename

    # File Information
    pdf_filename = Column(String(255), nullable=False)
    pdf_path = Column(String(500), nullable=False)

    # Scores
    total_score = Column(Float, default=0.0)
    max_score = Column(Float, nullable=False)
    percentage = Column(Float, default=0.0)  # Calculated: (total_score / max_score) * 100

    # AI-Generated Summary
    summary = Column(Text, nullable=True)  # Overall strengths, weaknesses, recommendations

    # Topic Gaps (JSON array)
    # Format: ["DNA structure", "Cell division", ...]
    topic_gaps = Column(JSON, nullable=True)

    # Relationships
    evaluation = relationship("Evaluation", back_populates="students")
    questions = relationship(
        "QuestionResponse",
        back_populates="student",
        cascade="all, delete-orphan",
        order_by="QuestionResponse.question_number",
    )

    def __repr__(self):
        return (
            f"<StudentResponse(id={self.id}, student_id={self.student_id}, score={self.total_score}/{self.max_score})>"
        )


class QuestionResponse(BaseModel):
    """
    Detailed evaluation for a single question.

    Contains:
    - Student's answer
    - Expected answer
    - Score and feedback
    - AI reasoning
    """

    __tablename__ = "question_responses"

    # Foreign Keys
    student_response_id = Column(Integer, ForeignKey("student_responses.id"), nullable=False, index=True)

    # Question Info
    question_number = Column(Integer, nullable=False)

    # Answers
    student_answer = Column(Text, nullable=False)
    expected_answer = Column(Text, nullable=False)

    # Scoring
    score = Column(Float, nullable=False)
    max_score = Column(Float, nullable=False)

    # AI-Generated Feedback
    feedback = Column(Text, nullable=False)  # Explanation for the score

    # Additional data (JSON)
    # Can store: keywords matched, concepts covered, etc.
    additional_data = Column(JSON, nullable=True)

    # Relationships
    student = relationship("StudentResponse", back_populates="questions")

    def __repr__(self):
        return f"<QuestionResponse(id={self.id}, q{self.question_number}, score={self.score}/{self.max_score})>"


class FollowUpQuestion(BaseModel):
    """
    Log of follow-up questions asked about evaluations.

    Used for:
    - Chat history
    - Analytics
    - Improving AI responses
    """

    __tablename__ = "followup_questions"

    # Foreign Keys
    evaluation_id = Column(Integer, ForeignKey("evaluations.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Optional: Question about specific student
    student_response_id = Column(Integer, ForeignKey("student_responses.id"), nullable=True, index=True)

    # Question & Answer
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)

    # Context used for answering (JSON)
    # Can include: relevant question data, scores, etc.
    context = Column(JSON, nullable=True)

    # Relationships
    evaluation = relationship("Evaluation", backref="followup_questions")
    user = relationship("User", backref="followup_questions")
    student = relationship("StudentResponse", backref="followup_questions")

    def __repr__(self):
        return f"<FollowUpQuestion(id={self.id}, evaluation_id={self.evaluation_id})>"
