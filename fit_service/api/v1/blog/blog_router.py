from typing import Optional, Annotated
from fastapi import APIRouter, Depends, Query, status, Header

from fit_service.api.v1.blog.blog_schemas import (
    BlogCreate,
    BlogUpdate,
    BlogListResponse,
    BlogCategoryCreate,
    BlogCategoryUpdate,
    BlogCategoryListResponse,
    BlogTagCreate,
    BlogTagUpdate,
    BlogTagListResponse,
)
from fit_service.core.services.blog_service import BlogService
from libs.service.auth import AuthService
from sqlalchemy.ext.asyncio import AsyncSession
from libs.db import get_async_db

router = APIRouter(tags=["Blog"], prefix="/blog")


# Dependencies
def get_blog_service(db: AsyncSession = Depends(get_async_db)) -> BlogService:
    return BlogService(db)


def get_auth_service(db: AsyncSession = Depends(get_async_db)) -> AuthService:
    return AuthService(db)


# Blog Category endpoints
@router.post("/categories", status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: BlogCategoryCreate,
    authorization: Annotated[str | None, Header()] = None,
    blog_service: BlogService = Depends(get_blog_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Create a new blog category (admin only)"""
    user = await auth_service.get_user_from_token(authorization)
    await auth_service.verify_admin(user.id)
    return await blog_service.create_category(category_data)


@router.get("/categories/{category_id}")
async def get_category(
    category_id: int,
    blog_service: BlogService = Depends(get_blog_service),
):
    """Get a specific blog category by ID"""
    return await blog_service.get_category(category_id)


@router.get("/categories")
async def list_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    blog_service: BlogService = Depends(get_blog_service),
):
    """List all blog categories"""
    categories, total_count = await blog_service.list_categories(skip, limit)
    return BlogCategoryListResponse(
        items=categories,
        count=len(categories),
        total=total_count,
    )


@router.put("/categories/{category_id}")
async def update_category(
    category_id: int,
    category_data: BlogCategoryUpdate,
    authorization: Annotated[str | None, Header()] = None,
    blog_service: BlogService = Depends(get_blog_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Update an existing blog category (admin only)"""
    user = await auth_service.get_user_from_token(authorization)
    await auth_service.verify_admin(user.id)
    return await blog_service.update_category(category_id, category_data)


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    authorization: Annotated[str | None, Header()] = None,
    blog_service: BlogService = Depends(get_blog_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Delete a blog category (admin only)"""
    user = await auth_service.get_user_from_token(authorization)
    await auth_service.verify_admin(user.id)
    await blog_service.delete_category(category_id)


# Blog Tag endpoints
@router.post("/tags", status_code=status.HTTP_201_CREATED)
async def create_tag(
    tag_data: BlogTagCreate,
    authorization: Annotated[str | None, Header()] = None,
    blog_service: BlogService = Depends(get_blog_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Create a new blog tag (admin only)"""
    user = await auth_service.get_user_from_token(authorization)
    await auth_service.verify_admin(user.id)
    return await blog_service.create_tag(tag_data)


@router.get("/tags/{tag_id}")
async def get_tag(
    tag_id: int,
    blog_service: BlogService = Depends(get_blog_service),
):
    """Get a specific blog tag by ID"""
    return await blog_service.get_tag(tag_id)


@router.get("/tags")
async def list_tags(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    blog_service: BlogService = Depends(get_blog_service),
):
    """List all blog tags"""
    tags, total_count = await blog_service.list_tags(skip, limit)
    return BlogTagListResponse(
        items=tags,
        count=len(tags),
        total=total_count,
    )


@router.put("/tags/{tag_id}")
async def update_tag(
    tag_id: int,
    tag_data: BlogTagUpdate,
    authorization: Annotated[str | None, Header()] = None,
    blog_service: BlogService = Depends(get_blog_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Update an existing blog tag (admin only)"""
    user = await auth_service.get_user_from_token(authorization)
    await auth_service.verify_admin(user.id)
    return await blog_service.update_tag(tag_id, tag_data)


@router.delete("/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tag_id: int,
    authorization: Annotated[str | None, Header()] = None,
    blog_service: BlogService = Depends(get_blog_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Delete a blog tag (admin only)"""
    user = await auth_service.get_user_from_token(authorization)
    await auth_service.verify_admin(user.id)
    await blog_service.delete_tag(tag_id)


# Blog endpoints
@router.post("", status_code=status.HTTP_201_CREATED)
async def create_blog(
    blog_data: BlogCreate,
    authorization: Annotated[str | None, Header()] = None,
    blog_service: BlogService = Depends(get_blog_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Create a new blog post"""
    user = await auth_service.get_user_from_token(authorization)
    return await blog_service.create_blog(user.id, blog_data)


@router.get("/{blog_id}")
async def get_blog(
    blog_id: int,
    increment_view: bool = Query(False, description="Whether to increment the view count"),
    blog_service: BlogService = Depends(get_blog_service),
):
    """Get a specific blog by ID"""
    blog = await blog_service.get_blog(blog_id)

    if increment_view:
        await blog_service.increment_view_count(blog_id)

    return blog


@router.get("")
async def list_blogs(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    tag_id: Optional[int] = Query(None, description="Filter by tag ID"),
    blog_type: Optional[str] = Query(None, description="Filter by blog type (e.g., explore, recipe)"),
    is_published: Optional[bool] = Query(None, description="Filter by published status"),
    is_featured: Optional[bool] = Query(None, description="Filter by featured status"),
    search: Optional[str] = Query(None, description="Search term for title, content, or summary"),
    blog_service: BlogService = Depends(get_blog_service),
):
    """List blogs with various filters"""
    blogs, total_count = await blog_service.list_blogs(
        skip=skip,
        limit=limit,
        user_id=user_id,
        category_id=category_id,
        tag_id=tag_id,
        blog_type=blog_type,
        is_published=is_published,
        is_featured=is_featured,
        search_term=search,
    )

    return BlogListResponse(
        items=blogs,
        count=len(blogs),
        total=total_count,
    )


@router.put("/{blog_id}")
async def update_blog(
    blog_id: int,
    blog_data: BlogUpdate,
    authorization: Annotated[str | None, Header()] = None,
    blog_service: BlogService = Depends(get_blog_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Update an existing blog"""
    user = await auth_service.get_user_from_token(authorization)
    is_admin = await auth_service.is_admin(user.id)
    return await blog_service.update_blog(blog_id, user.id, blog_data, is_admin)


@router.delete("/{blog_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_blog(
    blog_id: int,
    authorization: Annotated[str | None, Header()] = None,
    blog_service: BlogService = Depends(get_blog_service),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Delete a blog"""
    user = await auth_service.get_user_from_token(authorization)
    is_admin = await auth_service.is_admin(user.id)
    await blog_service.delete_blog(blog_id, user.id, is_admin)
