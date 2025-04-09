from contextlib import asynccontextmanager
from typing import AsyncGenerator

import anyio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from content_service.api.v1.blog.blog_router import router as blog_router
from libs import ExceptionBase, settings


# App Lifespan
@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    limiter = anyio.to_thread.current_default_thread_limiter()
    limiter.total_tokens = 100
    yield


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
    allow_methods=["GET", "POST"],
    allow_credentials=False,
)


@app.exception_handler(ExceptionBase)
async def http_exception_handler(_request, exc: ExceptionBase) -> ORJSONResponse:
    return ORJSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict(),
    )


app.include_router(blog_router, prefix=settings.API_STR)
