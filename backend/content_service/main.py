from contextlib import asynccontextmanager
from typing import AsyncGenerator

import anyio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from fastapi_limiter import FastAPILimiter
import redis.asyncio as redis
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration

from content_service.api.v1.content.router import router as content_router
from libs import ExceptionBase, settings


# Initialize Sentry if enabled and in production environment
if settings.SENTRY_ENABLED and settings.ENV_NAME == "PRODUCTION":
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.SENTRY_ENVIRONMENT,
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
        integrations=[
            StarletteIntegration(transaction_style="endpoint"),
            FastApiIntegration(transaction_style="endpoint"),
        ],
    )


# App Lifespan
@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    # Thread limiter setting
    limiter = anyio.to_thread.current_default_thread_limiter()
    limiter.total_tokens = 100

    # Initialize rate limiter with Redis connection
    redis_url = f"redis://:{settings.REDIS_PASSWORD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/0"
    redis_instance = redis.from_url(redis_url, encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(redis_instance)

    yield

    # Close Redis connection on shutdown
    await redis_instance.close()


# APP Configuration
app = FastAPI(
    title=settings.PROJECT_NAME.format(project_name="Content"),
    version=settings.PROJECT_VERSION,
    openapi_url=f"{settings.API_STR}/openapi.json",
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
    lifespan=lifespan,
)

# Middleware settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_headers=["*"],
    allow_methods=["*"],
    allow_credentials=True,
)


@app.exception_handler(ExceptionBase)
async def http_exception_handler(_request, exc: ExceptionBase) -> ORJSONResponse:
    return ORJSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict(),
    )


@app.exception_handler(Exception)
async def general_exception_handler(_request, exc: Exception) -> ORJSONResponse:
    import traceback

    print(f"UNHANDLED EXCEPTION: {exc}")
    print(traceback.format_exc())
    return ORJSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"},
    )


# Health check endpoint for Fly.io
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "content-service"}


app.include_router(content_router, prefix=settings.API_STR)
