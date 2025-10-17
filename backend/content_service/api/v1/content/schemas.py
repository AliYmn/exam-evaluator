from pydantic import BaseModel
from enum import Enum


class EvaluationStatus(str, Enum):
    PENDING = "pending"
    PARSING = "parsing"
    COMPLETED = "completed"
    FAILED = "failed"


class ExamUploadResponse(BaseModel):
    evaluation_id: str
    status: EvaluationStatus
    message: str
