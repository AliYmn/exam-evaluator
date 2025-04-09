from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


# Blog Category schemas
class BlogCategoryBase(BaseModel):
    """Base model for Blog Category"""

    name: str = Field(..., description="Category name")
    description: Optional[str] = Field(None, description="Category description")


class BlogCategoryCreate(BlogCategoryBase):
    """Request model for creating a Blog Category"""


class BlogCategoryUpdate(BaseModel):
    """Request model for updating a Blog Category"""

    name: Optional[str] = Field(None, description="Category name")
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


# Blog Tag schemas
class BlogTagBase(BaseModel):
    """Base model for Blog Tag"""

    name: str = Field(..., description="Tag name")


class BlogTagCreate(BlogTagBase):
    """Request model for creating a Blog Tag"""


class BlogTagUpdate(BaseModel):
    """Request model for updating a Blog Tag"""

    name: Optional[str] = Field(None, description="Tag name")


class BlogTagResponse(BlogTagBase):
    """Response model for Blog Tag"""

    id: int
    created_date: datetime
    updated_date: datetime

    class Config:
        from_attributes = True


class BlogTagListResponse(BaseModel):
    """Response model for a list of Blog Tags"""

    items: List[BlogTagResponse]
    count: int
    total: int


# Blog schemas
class BlogBase(BaseModel):
    """Base model for Blog"""

    category_id: Optional[int] = Field(None, description="Category ID")
    title: str = Field(..., description="Blog title")
    content: str = Field(..., description="Blog content")
    summary: Optional[str] = Field(None, description="Blog summary")
    image_url: Optional[str] = Field(None, description="URL to blog image")
    is_published: bool = Field(False, description="Whether the blog is published")
    is_featured: bool = Field(False, description="Whether the blog is featured")
    blog_type: Optional[str] = Field(None, description="Blog type for UI placement (e.g., explore, recipe)")
    tag_ids: Optional[List[int]] = Field(None, description="List of tag IDs to associate with the blog")


class BlogCreate(BlogBase):
    """Request model for creating a Blog"""


class BlogUpdate(BaseModel):
    """Request model for updating a Blog"""

    category_id: Optional[int] = Field(None, description="Category ID")
    title: Optional[str] = Field(None, description="Blog title")
    content: Optional[str] = Field(None, description="Blog content")
    summary: Optional[str] = Field(None, description="Blog summary")
    image_url: Optional[str] = Field(None, description="URL to blog image")
    is_published: Optional[bool] = Field(None, description="Whether the blog is published")
    is_featured: Optional[bool] = Field(None, description="Whether the blog is featured")
    blog_type: Optional[str] = Field(None, description="Blog type for UI placement (e.g., explore, recipe)")
    tag_ids: Optional[List[int]] = Field(None, description="List of tag IDs to associate with the blog")


class BlogTagInfo(BaseModel):
    """Embedded Tag information for Blog responses"""

    id: int
    name: str


class BlogCategoryInfo(BaseModel):
    """Embedded Category information for Blog responses"""

    id: int
    name: str
    description: Optional[str] = None


class BlogResponse(BaseModel):
    """Response model for Blog"""

    id: int
    user_id: int
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
