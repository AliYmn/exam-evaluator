from typing import Annotated
from fastapi import APIRouter, Depends, Header, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from content_service.api.v1.content.schemas import ExamUploadResponse
from content_service.core.services.service import ContentService
from libs.db.db import get_async_db
from libs.service.auth import AuthService

router = APIRouter(tags=["Exam Evaluation"], prefix="/exam")


def get_content_service(db: AsyncSession = Depends(get_async_db)) -> ContentService:
    return ContentService(db)


def get_auth_service(db: AsyncSession = Depends(get_async_db)) -> AuthService:
    return AuthService(db)


@router.post("/upload", response_model=ExamUploadResponse)
async def upload_answer_key(
    authorization: Annotated[str | None, Header()] = None,
    answer_key: UploadFile = File(...),
    content_service: ContentService = Depends(get_content_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization required")

    user = await auth_service.decode_token(authorization.replace("Bearer ", ""))
    return await content_service.upload_answer_key(answer_key, user.id)
