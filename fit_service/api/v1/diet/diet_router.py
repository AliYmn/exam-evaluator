from fastapi import APIRouter, Depends, Query, status, Header
from typing import Annotated

from fit_service.api.v1.diet.diet_schemas import DietCreate, DietUpdate, DietListResponse, DietTrackerListResponse
from fit_service.core.services.diet_service import DietService
from sqlalchemy.ext.asyncio import AsyncSession
from libs.db import get_async_db
from libs.service.auth import AuthService
from libs import ErrorCode, ExceptionBase

router = APIRouter(tags=["Diet"], prefix="/diet")


def get_diet_service(db: AsyncSession = Depends(get_async_db)) -> DietService:
    return DietService(db)


def get_fit_service(db: AsyncSession = Depends(get_async_db)) -> AuthService:
    return AuthService(db)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_diet(
    diet_data: DietCreate,
    authorization: Annotated[str | None, Header()] = None,
    diet_service: DietService = Depends(get_diet_service),
    fit_service: AuthService = Depends(get_fit_service),
):
    """Create a new diet record for the authenticated user"""
    try:
        user = await fit_service.get_user_from_token(authorization)
        return await diet_service.create_diet(user.id, diet_data)
    except Exception:
        raise ExceptionBase(ErrorCode.UNAUTHORIZED)


@router.get("/{diet_id}")
async def get_diet(
    diet_id: int,
    authorization: Annotated[str | None, Header()] = None,
    diet_service: DietService = Depends(get_diet_service),
    fit_service: AuthService = Depends(get_fit_service),
):
    """Get a specific diet record by ID"""
    user = await fit_service.get_user_from_token(authorization)
    return await diet_service.get_diet(diet_id, user.id)


@router.get("")
async def list_diets(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    authorization: Annotated[str | None, Header()] = None,
    diet_service: DietService = Depends(get_diet_service),
    fit_service: AuthService = Depends(get_fit_service),
):
    """List all diet records for the authenticated user"""
    user = await fit_service.get_user_from_token(authorization)
    diets, total_count = await diet_service.list_diets(user.id, skip, limit)

    return DietListResponse(
        items=diets,
        count=len(diets),
        total=total_count,
    )


@router.put("/{diet_id}")
async def update_diet(
    diet_id: int,
    diet_data: DietUpdate,
    authorization: Annotated[str | None, Header()] = None,
    diet_service: DietService = Depends(get_diet_service),
    fit_service: AuthService = Depends(get_fit_service),
):
    """Update a specific diet record"""
    try:
        user = await fit_service.get_user_from_token(authorization)
        return await diet_service.update_diet(diet_id, user.id, diet_data)
    except Exception:
        raise ExceptionBase(ErrorCode.UNAUTHORIZED)


@router.delete("/{diet_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_diet(
    diet_id: int,
    authorization: Annotated[str | None, Header()] = None,
    diet_service: DietService = Depends(get_diet_service),
    fit_service: AuthService = Depends(get_fit_service),
):
    """Delete a specific diet record"""
    try:
        user = await fit_service.get_user_from_token(authorization)
        await diet_service.delete_diet(diet_id, user.id)
    except Exception:
        raise ExceptionBase(ErrorCode.UNAUTHORIZED)


@router.get("/{diet_id}/trackers")
async def list_diet_trackers(
    diet_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    authorization: Annotated[str | None, Header()] = None,
    diet_service: DietService = Depends(get_diet_service),
    fit_service: AuthService = Depends(get_fit_service),
):
    """List all diet tracker records for a specific diet"""
    user = await fit_service.get_user_from_token(authorization)
    trackers, total_count = await diet_service.list_diet_trackers_by_diet_id(diet_id, user.id, skip, limit)

    return DietTrackerListResponse(
        items=trackers,
        count=len(trackers),
        total=total_count,
    )


@router.get("/trackers")
async def list_all_diet_trackers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    authorization: Annotated[str | None, Header()] = None,
    diet_service: DietService = Depends(get_diet_service),
    fit_service: AuthService = Depends(get_fit_service),
):
    """List all diet tracker records for the authenticated user"""
    user = await fit_service.get_user_from_token(authorization)
    trackers, total_count = await diet_service.list_diet_trackers_by_user_id(user.id, skip, limit)

    return DietTrackerListResponse(
        items=trackers,
        count=len(trackers),
        total=total_count,
    )
