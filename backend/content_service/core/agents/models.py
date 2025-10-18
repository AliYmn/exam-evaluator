"""
Pydantic models for structured agent outputs
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class AnswerKeyQuestion(BaseModel):
    """Structured model for answer key questions"""

    number: int = Field(description="Question number")
    question_text: str = Field(description="The question text exactly as it appears")
    expected_answer: str = Field(description="The expected answer exactly as it appears")
    max_score: float = Field(default=10, description="Maximum score for this question")
    keywords: List[str] = Field(default_factory=list, description="Key concepts/terms")


class AnswerKeyOutput(BaseModel):
    """Complete answer key structure"""

    questions: List[AnswerKeyQuestion] = Field(description="List of questions")
    total_questions: int = Field(description="Total number of questions")
    max_possible_score: float = Field(description="Sum of all max_scores")


class StudentAnswer(BaseModel):
    """Student's answer for a question"""

    number: int = Field(description="Question number")
    student_answer: str = Field(description="Student's written answer")


class StudentAnswersOutput(BaseModel):
    """Student answers list"""

    answers: List[StudentAnswer] = Field(description="List of student answers")


class EvaluationResult(BaseModel):
    """Evaluation result for a single answer with confidence"""

    score: float = Field(description="Score awarded (0 to max_score)")
    feedback: str = Field(description="Detailed Turkish feedback explaining the score")
    is_correct: bool = Field(description="True if score >= 70% of max_score")
    confidence: float = Field(
        default=0.8, ge=0.0, le=1.0, description="Confidence score (0-1) indicating how certain the evaluation is"
    )
    reasoning: Optional[str] = Field(
        default=None, description="Brief reasoning for the score (optional, for transparency)"
    )


class PerformanceAnalysis(BaseModel):
    """Student performance analysis"""

    strengths: List[str] = Field(description="2-4 strengths in Turkish (max 15 words each)")
    weaknesses: List[str] = Field(description="2-4 weaknesses in Turkish (max 15 words each)")
    confidence: float = Field(default=0.8, ge=0.0, le=1.0, description="Confidence in the analysis")


class QualityCheckResult(BaseModel):
    """Result of quality check / self-correction"""

    is_acceptable: bool = Field(description="True if the evaluation quality is acceptable")
    issues: List[str] = Field(default_factory=list, description="List of quality issues found (if any)")
    suggested_corrections: Optional[dict] = Field(
        default=None, description="Suggested corrections if quality is not acceptable"
    )
    confidence: float = Field(default=0.9, description="Confidence in the quality assessment")
