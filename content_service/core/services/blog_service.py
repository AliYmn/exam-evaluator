from typing import List, Optional, Tuple

from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from libs.models.blog import Blog, BlogCategory, blog_tag_association
from content_service.api.v1.blog.blog_schemas import (
    BlogResponse,
    BlogCategoryResponse,
)
from libs import ErrorCode, ExceptionBase


class BlogService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # Blog Category Methods
    async def list_categories(self, skip: int = 0, limit: int = 100) -> Tuple[List[BlogCategoryResponse], int]:
        """List all blog categories"""
        # Get total count
        count_query = select(func.count()).select_from(BlogCategory).where(BlogCategory.deleted_date.is_(None))
        total_count = await self.db.execute(count_query)
        total = total_count.scalar()

        # Get categories with pagination
        query = (
            select(BlogCategory)
            .where(BlogCategory.deleted_date.is_(None))
            .order_by(BlogCategory.name)
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        categories = result.scalars().all()

        return [BlogCategoryResponse.model_validate(category) for category in categories], total

    # Blog Methods
    async def get_blog(self, blog_id: int) -> BlogResponse:
        """Get a specific blog by ID"""
        query = (
            select(Blog)
            .options(joinedload(Blog.category), joinedload(Blog.tags))
            .where(and_(Blog.id == blog_id, Blog.deleted_date.is_(None)))
        )
        result = await self.db.execute(query)
        blog = result.scalars().first()

        if not blog:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        return BlogResponse.model_validate(blog)

    async def list_blogs(
        self,
        skip: int = 0,
        limit: int = 10,
        category_id: Optional[int] = None,
        tag_id: Optional[int] = None,
        blog_type: Optional[str] = None,
        is_published: Optional[bool] = None,
        is_featured: Optional[bool] = None,
        search_term: Optional[str] = None,
        language: Optional[str] = "en",
    ) -> Tuple[List[BlogResponse], int]:
        """List blogs with various filters"""
        # Build base query
        base_query = select(Blog).where(Blog.deleted_date.is_(None))

        # Apply filters
        if category_id is not None:
            base_query = base_query.where(Blog.category_id == category_id)

        if tag_id is not None:
            base_query = base_query.join(blog_tag_association).where(blog_tag_association.c.tag_id == tag_id)

        if blog_type is not None:
            base_query = base_query.where(Blog.blog_type == blog_type)

        if is_published is not None:
            base_query = base_query.where(Blog.is_published == is_published)

        if is_featured is not None:
            base_query = base_query.where(Blog.is_featured == is_featured)

        if search_term:
            search_filter = or_(
                Blog.title.ilike(f"%{search_term}%"),
                Blog.content.ilike(f"%{search_term}%"),
                Blog.summary.ilike(f"%{search_term}%"),
            )
            base_query = base_query.where(search_filter)

        if language is not None:
            base_query = base_query.where(Blog.language == language)

        # Get total count
        count_query = select(func.count()).select_from(base_query.subquery())
        total_count = await self.db.execute(count_query)
        total = total_count.scalar()

        # Get blogs with pagination
        query = (
            base_query.options(joinedload(Blog.category), joinedload(Blog.tags))
            .order_by(Blog.created_date.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        blogs = result.scalars().all()

        return [BlogResponse.model_validate(blog) for blog in blogs], total

    async def increment_view_count(self, blog_id: int) -> None:
        """Increment the view count of a blog"""
        query = select(Blog).where(and_(Blog.id == blog_id, Blog.deleted_date.is_(None)))
        result = await self.db.execute(query)
        blog = result.scalars().first()

        if not blog:
            raise ExceptionBase(ErrorCode.NOT_FOUND)

        blog.view_count += 1
        await self.db.commit()
