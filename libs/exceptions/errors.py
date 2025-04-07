from enum import IntEnum


class ErrorCode(IntEnum):
    def __new__(cls, code, message, status_code) -> "ErrorCode":
        obj = int.__new__(cls, code)
        obj._value_ = code
        obj.code = code
        obj.message = message.upper()
        obj.status_code = status_code
        return obj

    # General errors
    UNKNOWN_ERROR = (1000, "Unknown error", 500)
    VALIDATION_ERROR = (1001, "Validation failed", 400)
    UNAUTHORIZED = (1002, "Unauthorized access", 401)
    FORBIDDEN = (1003, "Forbidden", 403)
    NOT_FOUND = (1004, "Resource not found", 404)
    METHOD_NOT_ALLOWED = (1005, "Method not allowed", 405)
    CONFLICT = (1006, "Conflict", 409)
    UNSUPPORTED_MEDIA_TYPE = (1007, "Unsupported media type", 415)
    RATE_LIMIT_EXCEEDED = (1008, "Rate limit exceeded", 429)
    PAYLOAD_TOO_LARGE = (1009, "Payload too large", 413)

    # Server errors
    INTERNAL_SERVER_ERROR = (2000, "Internal server error", 500)
    SERVICE_UNAVAILABLE = (2001, "Service temporarily unavailable", 503)
    TIMEOUT = (2002, "Request timeout", 504)
    BAD_GATEWAY = (2003, "Bad gateway", 502)

    # Authentication errors
    DUPLICATE_ENTRY = (3000, "Duplicate entry", 400)
    DEPENDENCY_FAILURE = (3001, "Dependency failure", 424)
    AUTHENTICATION_FAILED = (3002, "Authentication failed", 401)
    INVALID_TOKEN = (3003, "Invalid token", 401)
    EXPIRED_TOKEN = (3004, "Expired token", 401)

    def __str__(self) -> str:
        return f"Error Code: {self.code}, Message: {self.message}, Status Code: {self.status_code}"
