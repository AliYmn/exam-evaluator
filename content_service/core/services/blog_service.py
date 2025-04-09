from typing import List, Optional, Tuple
from datetime import datetime

from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from libs.models.blog import Blog, BlogCategory, BlogTag, blog_tag_association
from content_service.api.v1.blog.blog_schemas import (
    BlogCreate,
    BlogUpdate,
    BlogResponse,
    BlogCategoryCreate,
    BlogCategoryUpdate,
    BlogCategoryResponse,
    BlogTagCreate,
    BlogTagUpdate,
    BlogTagResponse,
)
from libs import ErrorCode, ExceptionBase


class BlogService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # Blog Category Methods
    async def create_category(self, category_data: BlogCategoryCreate) -> BlogCategoryResponse:
        """Create a new blog category"""
        # Check if category with same name already exists
        result = await self.db.execute(
            select(BlogCategory).where(
                and_(BlogCategory.name == category_data.name, BlogCategory.deleted_date.is_(None))
            )
        )
        existing_category = result.scalars().first()
        if existing_category:
            raise ExceptionBase(ErrorCode.ALREADY_EXISTS, "Category with this name already exists")

        new_category = BlogCategory(
            name=category_data.name,
            description=category_data.description,
        )

        self.db.add(new_category)
        await self.db.commit()
        await self.db.refresh(new_category)

        return BlogCategoryResponse.model_validate(new_category)

    async def get_category(self, category_id: int) -> BlogCategoryResponse:
        """Get a specific blog category by ID"""
        result = await self.db.execute(
            select(BlogCategory).where(and_(BlogCategory.id == category_id, BlogCategory.deleted_date.is_(None)))
        )
        category = result.scalars().first()

        if not category:
            raise ExceptionBase(ErrorCode.NOT_FOUND, f"Category with ID {category_id} not found")

        return BlogCategoryResponse.model_validate(category)

    async def list_categories(self, skip: int = 0, limit: int = 100) -> Tuple[List[BlogCategoryResponse], int]:
        """List all blog categories"""
        # Get total count
        count_result = await self.db.execute(
            select(func.count()).select_from(BlogCategory).where(BlogCategory.deleted_date.is_(None))
        )
        total_count = count_result.scalar_one()

        # Get categories with pagination
        result = await self.db.execute(
            select(BlogCategory)
            .where(BlogCategory.deleted_date.is_(None))
            .order_by(BlogCategory.name)
            .offset(skip)
            .limit(limit)
        )
        categories = result.scalars().all()

        return [BlogCategoryResponse.model_validate(category) for category in categories], total_count

    async def update_category(self, category_id: int, category_data: BlogCategoryUpdate) -> BlogCategoryResponse:
        """Update an existing blog category"""
        result = await self.db.execute(
            select(BlogCategory).where(and_(BlogCategory.id == category_id, BlogCategory.deleted_date.is_(None)))
        )
        category = result.scalars().first()

        if not category:
            raise ExceptionBase(ErrorCode.NOT_FOUND, f"Category with ID {category_id} not found")

        # Check if new name conflicts with existing category
        if category_data.name and category_data.name != category.name:
            name_check = await self.db.execute(
                select(BlogCategory).where(
                    and_(
                        BlogCategory.name == category_data.name,
                        BlogCategory.id != category_id,
                        BlogCategory.deleted_date.is_(None),
                    )
                )
            )
            if name_check.scalars().first():
                raise ExceptionBase(ErrorCode.ALREADY_EXISTS, "Category with this name already exists")

        # Update fields if provided
        if category_data.name is not None:
            category.name = category_data.name
        if category_data.description is not None:
            category.description = category_data.description

        await self.db.commit()
        await self.db.refresh(category)

        return BlogCategoryResponse.model_validate(category)

    async def delete_category(self, category_id: int) -> None:
        """Soft delete a blog category"""
        result = await self.db.execute(
            select(BlogCategory).where(and_(BlogCategory.id == category_id, BlogCategory.deleted_date.is_(None)))
        )
        category = result.scalars().first()

        if not category:
            raise ExceptionBase(ErrorCode.NOT_FOUND, f"Category with ID {category_id} not found")

        # Check if category is used by any blogs
        blog_check = await self.db.execute(
            select(Blog).where(and_(Blog.category_id == category_id, Blog.deleted_date.is_(None)))
        )
        if blog_check.scalars().first():
            raise ExceptionBase(ErrorCode.OPERATION_NOT_ALLOWED, "Cannot delete category that is used by blogs")

        # Soft delete by setting deleted_date
        category.deleted_date = datetime.now()
        await self.db.commit()

    # Blog Tag Methods
    async def create_tag(self, tag_data: BlogTagCreate) -> BlogTagResponse:
        """Create a new blog tag"""
        # Check if tag with same name already exists
        result = await self.db.execute(select(BlogTag).where(BlogTag.name == tag_data.name))
        existing_tag = result.scalars().first()
        if existing_tag:
            raise ExceptionBase(ErrorCode.ALREADY_EXISTS, "Tag with this name already exists")

        new_tag = BlogTag(
            name=tag_data.name,
        )

        self.db.add(new_tag)
        await self.db.commit()
        await self.db.refresh(new_tag)

        return BlogTagResponse.model_validate(new_tag)

    async def get_tag(self, tag_id: int) -> BlogTagResponse:
        """Get a specific blog tag by ID"""
        result = await self.db.execute(select(BlogTag).where(BlogTag.id == tag_id))
        tag = result.scalars().first()

        if not tag:
            raise ExceptionBase(ErrorCode.NOT_FOUND, f"Tag with ID {tag_id} not found")

        return BlogTagResponse.model_validate(tag)

    async def list_tags(self, skip: int = 0, limit: int = 100) -> Tuple[List[BlogTagResponse], int]:
        """List all blog tags"""
        # Get total count
        count_result = await self.db.execute(select(func.count()).select_from(BlogTag))
        total_count = count_result.scalar_one()

        # Get tags with pagination
        result = await self.db.execute(select(BlogTag).order_by(BlogTag.name).offset(skip).limit(limit))
        tags = result.scalars().all()

        return [BlogTagResponse.model_validate(tag) for tag in tags], total_count

    async def update_tag(self, tag_id: int, tag_data: BlogTagUpdate) -> BlogTagResponse:
        """Update an existing blog tag"""
        result = await self.db.execute(select(BlogTag).where(BlogTag.id == tag_id))
        tag = result.scalars().first()

        if not tag:
            raise ExceptionBase(ErrorCode.NOT_FOUND, f"Tag with ID {tag_id} not found")

        # Check if new name conflicts with existing tag
        if tag_data.name and tag_data.name != tag.name:
            name_check = await self.db.execute(
                select(BlogTag).where(and_(BlogTag.name == tag_data.name, BlogTag.id != tag_id))
            )
            if name_check.scalars().first():
                raise ExceptionBase(ErrorCode.ALREADY_EXISTS, "Tag with this name already exists")

        # Update fields if provided
        if tag_data.name is not None:
            tag.name = tag_data.name

        await self.db.commit()
        await self.db.refresh(tag)

        return BlogTagResponse.model_validate(tag)

    async def delete_tag(self, tag_id: int) -> None:
        """Delete a blog tag"""
        result = await self.db.execute(select(BlogTag).where(BlogTag.id == tag_id))
        tag = result.scalars().first()

        if not tag:
            raise ExceptionBase(ErrorCode.NOT_FOUND, f"Tag with ID {tag_id} not found")

        # Remove tag from all blogs
        await self.db.execute(blog_tag_association.delete().where(blog_tag_association.c.tag_id == tag_id))

        # Delete the tag
        await self.db.delete(tag)
        await self.db.commit()

    # Blog Methods
    async def create_blog(self, blog_data: BlogCreate) -> BlogResponse:
        """Create a new blog post"""
        # Create new blog
        new_blog = Blog(
            category_id=blog_data.category_id,
            title=blog_data.title,
            content=blog_data.content,
            summary=blog_data.summary,
            image_url=blog_data.image_url,
            is_published=blog_data.is_published,
            is_featured=blog_data.is_featured,
            blog_type=blog_data.blog_type,
        )

        self.db.add(new_blog)
        await self.db.commit()
        await self.db.refresh(new_blog)

        # Add tags if provided
        if blog_data.tag_ids:
            await self._update_blog_tags(new_blog.id, blog_data.tag_ids)

        # Fetch the blog with relationships for response
        return await self._get_blog_with_relationships(new_blog.id)

    async def get_blog(self, blog_id: int) -> BlogResponse:
        """Get a specific blog by ID"""
        return await self._get_blog_with_relationships(blog_id)

    async def _get_blog_with_relationships(self, blog_id: int) -> BlogResponse:
        """Helper method to get a blog with its relationships"""
        result = await self.db.execute(
            select(Blog)
            .options(joinedload(Blog.category), joinedload(Blog.tags))
            .where(and_(Blog.id == blog_id, Blog.deleted_date.is_(None)))
        )
        blog = result.unique().scalars().first()

        if not blog:
            raise ExceptionBase(ErrorCode.NOT_FOUND, f"Blog with ID {blog_id} not found")

        return BlogResponse.model_validate(blog)

    async def list_blogs(
        self,
        skip: int = 0,
        limit: int = 100,
        category_id: Optional[int] = None,
        tag_id: Optional[int] = None,
        blog_type: Optional[str] = None,
        is_published: Optional[bool] = None,
        is_featured: Optional[bool] = None,
        search_term: Optional[str] = None,
    ) -> Tuple[List[BlogResponse], int]:
        """List blogs with various filters"""
        # Build the query with filters
        query = (
            select(Blog).options(joinedload(Blog.category), joinedload(Blog.tags)).where(Blog.deleted_date.is_(None))
        )

        # Apply filters
        if category_id is not None:
            query = query.where(Blog.category_id == category_id)
        if tag_id is not None:
            query = query.join(Blog.tags).where(BlogTag.id == tag_id)
        if blog_type is not None:
            query = query.where(Blog.blog_type == blog_type)
        if is_published is not None:
            query = query.where(Blog.is_published == is_published)
        if is_featured is not None:
            query = query.where(Blog.is_featured == is_featured)
        if search_term is not None:
            search_filter = or_(
                Blog.title.ilike(f"%{search_term}%"),
                Blog.content.ilike(f"%{search_term}%"),
                Blog.summary.ilike(f"%{search_term}%"),
            )
            query = query.where(search_filter)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await self.db.execute(count_query)
        total_count = count_result.scalar_one()

        # Get blogs with pagination
        query = query.order_by(Blog.created_date.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        blogs = result.unique().scalars().all()

        return [BlogResponse.model_validate(blog) for blog in blogs], total_count

    async def update_blog(self, blog_id: int, blog_data: BlogUpdate, is_admin: bool = False) -> BlogResponse:
        """Update an existing blog"""
        query = select(Blog).where(and_(Blog.id == blog_id, Blog.deleted_date.is_(None)))

        # If not admin, only allow updates to published status
        if not is_admin:
            # Only allow updating specific fields for non-admins
            if any(
                field is not None
                for field in [
                    blog_data.category_id,
                    blog_data.title,
                    blog_data.content,
                    blog_data.summary,
                    blog_data.image_url,
                    blog_data.blog_type,
                ]
            ):
                raise ExceptionBase(ErrorCode.PERMISSION_DENIED, "Only admins can update blog content")

        result = await self.db.execute(query)
        blog = result.scalars().first()

        if not blog:
            raise ExceptionBase(ErrorCode.NOT_FOUND, f"Blog with ID {blog_id} not found")

        # Update fields if provided
        if blog_data.category_id is not None:
            blog.category_id = blog_data.category_id
        if blog_data.title is not None:
            blog.title = blog_data.title
        if blog_data.content is not None:
            blog.content = blog_data.content
        if blog_data.summary is not None:
            blog.summary = blog_data.summary
        if blog_data.image_url is not None:
            blog.image_url = blog_data.image_url
        if blog_data.is_published is not None:
            blog.is_published = blog_data.is_published
        if blog_data.is_featured is not None:
            blog.is_featured = blog_data.is_featured
        if blog_data.blog_type is not None:
            blog.blog_type = blog_data.blog_type

        await self.db.commit()
        await self.db.refresh(blog)

        # Update tags if provided
        if blog_data.tag_ids is not None:
            await self._update_blog_tags(blog_id, blog_data.tag_ids)

        # Fetch the blog with relationships for response
        return await self._get_blog_with_relationships(blog_id)

    async def delete_blog(self, blog_id: int, is_admin: bool = False) -> None:
        """Soft delete a blog"""
        query = select(Blog).where(and_(Blog.id == blog_id, Blog.deleted_date.is_(None)))

        # If not admin, don't allow deletion
        if not is_admin:
            raise ExceptionBase(ErrorCode.PERMISSION_DENIED, "Only admins can delete blogs")

        result = await self.db.execute(query)
        blog = result.scalars().first()

        if not blog:
            raise ExceptionBase(ErrorCode.NOT_FOUND, f"Blog with ID {blog_id} not found")

        # Soft delete by setting deleted_date
        blog.deleted_date = datetime.now()
        await self.db.commit()

    async def increment_view_count(self, blog_id: int) -> None:
        """Increment the view count for a blog"""
        result = await self.db.execute(select(Blog).where(and_(Blog.id == blog_id, Blog.deleted_date.is_(None))))
        blog = result.scalars().first()

        if not blog:
            raise ExceptionBase(ErrorCode.NOT_FOUND, f"Blog with ID {blog_id} not found")

        blog.view_count += 1
        await self.db.commit()

    async def _update_blog_tags(self, blog_id: int, tag_ids: List[int]) -> None:
        """Helper method to update the tags for a blog"""
        # First remove all existing tags
        await self.db.execute(blog_tag_association.delete().where(blog_tag_association.c.blog_id == blog_id))

        # Then add the new tags
        for tag_id in tag_ids:
            # Verify tag exists
            tag_check = await self.db.execute(select(BlogTag).where(BlogTag.id == tag_id))
            if not tag_check.scalars().first():
                raise ExceptionBase(ErrorCode.NOT_FOUND, f"Tag with ID {tag_id} not found")

            # Add association
            await self.db.execute(blog_tag_association.insert().values(blog_id=blog_id, tag_id=tag_id))

        await self.db.commit()
