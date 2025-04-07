from fastapi import APIRouter, Depends, Query, status, Header
from typing import Annotated

from auth_service.api.v1.diet.diet_schemas import DietCreate, DietUpdate, DietResponse, DietListResponse
from auth_service.core.services.diet_service import DietService
from libs.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from libs.db import get_async_db
from libs.service.auth import AuthService
from libs import ErrorCode, ExceptionBase

router = APIRouter(tags=["diet"], prefix="/diet")


async def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
    db: AsyncSession = Depends(get_async_db),
) -> User:
    """Validates the user's token and returns the current user"""
    if not authorization:
        raise ExceptionBase(ErrorCode.UNAUTHORIZED)

    auth_service = AuthService(db)
    try:
        _, user = await auth_service.validate_token(authorization)
        if not user:
            raise ExceptionBase(ErrorCode.UNAUTHORIZED)
        return user
    except Exception as e:
        raise ExceptionBase(ErrorCode.UNAUTHORIZED, str(e))


@router.post("", response_model=DietResponse, status_code=status.HTTP_201_CREATED)
async def create_diet(
    diet_data: DietCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    """Create a new diet record for the authenticated user"""
    diet_service = DietService(db)
    return await diet_service.create_diet(user.id, diet_data)


@router.get("/{diet_id}", response_model=DietResponse)
async def get_diet(
    diet_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    """Get a specific diet record by ID"""
    diet_service = DietService(db)
    return await diet_service.get_diet(diet_id, user.id)


@router.get("", response_model=DietListResponse)
async def list_diets(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    """List all diet records for the authenticated user"""
    diet_service = DietService(db)
    diets, total_count = await diet_service.list_diets(user.id, skip, limit)

    return DietListResponse(
        items=diets,
        count=len(diets),
        total=total_count,
    )


@router.put("/{diet_id}", response_model=DietResponse)
async def update_diet(
    diet_id: int,
    diet_data: DietUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    """Update a specific diet record"""
    diet_service = DietService(db)
    return await diet_service.update_diet(diet_id, user.id, diet_data)


@router.delete("/{diet_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_diet(
    diet_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
):
    """Delete a specific diet record"""
    diet_service = DietService(db)
    await diet_service.delete_diet(diet_id, user.id)
    return None
