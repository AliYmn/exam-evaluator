from typing import Optional
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import redis.asyncio as redis
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from libs.exceptions import ErrorCode
from libs.settings import settings


# Error message when rate limit is exceeded
RATE_LIMIT_EXCEEDED_MESSAGE = "Rate limit exceeded"


async def init_limiter(
    redis_host: str = None, redis_port: int = None, redis_db: int = 0, redis_password: Optional[str] = None
):
    """
    Initialize the FastAPI Limiter.

    Args:
        redis_host: Redis server address (defaults to settings.REDIS_HOST)
        redis_port: Redis port number (defaults to settings.REDIS_PORT)
        redis_db: Redis database number
        redis_password: Redis password (defaults to settings.REDIS_PASSWORD)
    """
    # Use values from settings if not provided
    redis_host = redis_host or settings.REDIS_HOST
    redis_port = redis_port or settings.REDIS_PORT
    redis_password = redis_password or settings.REDIS_PASSWORD

    # Build Redis URL
    redis_url = f"redis://{redis_host}:{redis_port}/{redis_db}"

    if redis_password:
        redis_url = f"redis://:{redis_password}@{redis_host}:{redis_port}/{redis_db}"

    redis_instance = redis.from_url(redis_url, encoding="utf-8", decode_responses=True)

    await FastAPILimiter.init(redis_instance)

    return redis_instance


def get_client_ip(request: Request) -> str:
    """
    Returns the IP address of the client making the request.

    Args:
        request: FastAPI request object

    Returns:
        Client IP address
    """
    x_forwarded_for = request.headers.get("X-Forwarded-For")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()

    client_host = request.client.host if request.client else None
    return client_host or "127.0.0.1"


async def rate_limit_callback(request: Request, response: Response, pexpire: int):
    """
    Handler called when rate limit is exceeded

    Args:
        request: FastAPI request object
        response: FastAPI response object
        pexpire: Time in seconds until the rate limit resets
    """
    return JSONResponse(
        status_code=429,
        content={
            "detail": RATE_LIMIT_EXCEEDED_MESSAGE,
            "code": ErrorCode.RATE_LIMIT_EXCEEDED.value,
            "retry_after": pexpire,
        },
    )


def ip_rate_limit(times: int = 10, seconds: int = 60):
    """
    Applies rate limiting based on IP address.

    Args:
        times: Maximum number of allowed requests
        seconds: Time period in seconds

    Returns:
        RateLimiter dependency
    """

    async def _get_ip_identifier(request: Request):
        return get_client_ip(request)

    return RateLimiter(times=times, seconds=seconds, identifier=_get_ip_identifier, callback=rate_limit_callback)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware that applies rate limiting to all requests.
    """

    def __init__(self, app, times: int = 100, seconds: int = 60, exclude_paths: list = None):
        super().__init__(app)
        self.times = times
        self.seconds = seconds
        self.exclude_paths = exclude_paths or []

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for excluded paths
        path = request.url.path
        if any(path.startswith(excluded) for excluded in self.exclude_paths):
            return await call_next(request)

        # Apply rate limit based on IP address
        client_ip = get_client_ip(request)

        # Rate limit check
        try:
            # Check with FastAPILimiter
            await FastAPILimiter.redis.incr(f"rate_limit:{client_ip}")
            current = await FastAPILimiter.redis.get(f"rate_limit:{client_ip}")

            # If first request, set expiration time
            if int(current) == 1:
                await FastAPILimiter.redis.expire(f"rate_limit:{client_ip}", self.seconds)

            # Check if limit exceeded
            if int(current) > self.times:
                return JSONResponse(
                    status_code=429,
                    content={"detail": RATE_LIMIT_EXCEEDED_MESSAGE, "code": ErrorCode.RATE_LIMIT_EXCEEDED.value},
                )

            # Continue with normal flow
            return await call_next(request)

        except Exception as e:
            # Skip rate limit check in case of Redis connection errors, etc.
            print(f"Rate limit error: {str(e)}")
            return await call_next(request)
