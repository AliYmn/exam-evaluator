from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


# Blog Category schemas
class BlogCategoryBase(BaseModel):
    """Base model for Blog Category"""

    name: str = Field(..., description="Category name")
    description: Optional[str] = Field(None, description="Category description")


class BlogCategoryResponse(BlogCategoryBase):
    """Response model for Blog Category"""

    id: int
    created_date: datetime
    updated_date: datetime
    deleted_date: Optional[datetime] = None

    class Config:
        from_attributes = True


class BlogCategoryListResponse(BaseModel):
    """Response model for a list of Blog Categories"""

    items: List[BlogCategoryResponse]
    count: int
    total: int


# Embedded models for Blog responses
class BlogCategoryInfo(BaseModel):
    """Embedded Category information for Blog responses"""

    id: int
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class BlogTagInfo(BaseModel):
    """Embedded Tag information for Blog responses"""

    id: int
    name: str

    class Config:
        from_attributes = True


# Blog schemas
class BlogResponse(BaseModel):
    """Response model for Blog"""

    id: int
    title: str
    content: str
    summary: Optional[str] = None
    image_url: Optional[str] = None
    view_count: int
    is_published: bool
    is_featured: bool
    blog_type: Optional[str] = None
    created_date: datetime
    updated_date: datetime
    deleted_date: Optional[datetime] = None
    category: Optional[BlogCategoryInfo] = None
    tags: List[BlogTagInfo] = []

    class Config:
        from_attributes = True


class BlogListResponse(BaseModel):
    """Response model for a list of Blogs"""

    items: List[BlogResponse]
    count: int
    total: int
