from typing import Any, Dict, Generic, Optional, TypeVar

from pydantic import BaseModel

from libs.exceptions.errors import ErrorCode

T = TypeVar("T")


class ResponseBase(BaseModel, Generic[T]):
    data: Optional[T] = None
    error_code: Optional[int] = None
    error_message: Optional[str] = None


class ExceptionBase(Exception):
    def __init__(self, error: ErrorCode) -> None:
        self.code = error.code
        self.message = error.message
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"Error Code: {self.code}, Message: {self.message}"

    def to_dict(self) -> Dict[str, Any]:
        return {"error_code": self.code, "error_message": self.message}
