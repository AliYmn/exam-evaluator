from contextlib import asynccontextmanager
from typing import AsyncGenerator

import anyio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from fastapi_limiter import FastAPILimiter
import redis.asyncio as redis

from tracker_service.api.v1.body_tracker.body_tracker_router import router as body_tracker_router
from tracker_service.api.v1.daily_tracker.daily_tracker_router import router as daily_tracker_router
from libs import ExceptionBase, settings


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
    title=settings.PROJECT_NAME.format(project_name="Tracker"),
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
    allow_methods=["GET", "POST"],
    allow_credentials=False,
)


@app.exception_handler(ExceptionBase)
async def http_exception_handler(_request, exc: ExceptionBase) -> ORJSONResponse:
    return ORJSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict(),
    )


app.include_router(body_tracker_router, prefix=settings.API_STR)
app.include_router(daily_tracker_router, prefix=settings.API_STR)
