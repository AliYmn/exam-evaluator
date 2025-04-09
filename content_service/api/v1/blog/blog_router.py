from typing import Optional
from fastapi import APIRouter, Depends, Query

from content_service.api.v1.blog.blog_schemas import (
    BlogListResponse,
    BlogCategoryListResponse,
)
from content_service.core.services.blog_service import BlogService
from sqlalchemy.ext.asyncio import AsyncSession
from libs.db import get_async_db

router = APIRouter(tags=["Blog"], prefix="/blog")


# Dependencies
def get_blog_service(db: AsyncSession = Depends(get_async_db)) -> BlogService:
    return BlogService(db)


# Blog Category endpoints
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


# Blog endpoints
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
