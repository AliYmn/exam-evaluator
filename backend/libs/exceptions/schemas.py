from typing import Any, Dict, Generic, Optional, TypeVar

from pydantic import BaseModel

from libs.exceptions.errors import ErrorCode

T = TypeVar("T")


class ResponseBase(BaseModel, Generic[T]):
    data: Optional[T] = None
    error_code: Optional[int] = None
    error_message: Optional[str] = None
    status_code: Optional[int] = None


class ExceptionBase(Exception):
    def __init__(self, error: ErrorCode) -> None:
        self.code = error.code
        self.message = error.message
        self.status_code = error.status_code
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"Error Code: {self.code}, Message: {self.message}, Status Code: {self.status_code}"

    def to_dict(self) -> Dict[str, Any]:
        return {"error_code": self.code, "error_message": self.message, "status_code": self.status_code}
