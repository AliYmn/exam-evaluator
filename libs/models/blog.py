from sqlalchemy import Column, Integer, String, Text, ForeignKey, Table, Boolean
from sqlalchemy.orm import relationship

from libs.models.base import BaseModel


# Association table for blog tags
blog_tag_association = Table(
    "blog_tag_association",
    BaseModel.metadata,
    Column("blog_id", Integer, ForeignKey("blogs.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("blog_tags.id"), primary_key=True),
)


class BlogCategory(BaseModel):
    """
    Model for blog categories
    Used to categorize blog posts (e.g., Recipes, Workouts, Nutrition)
    """

    __tablename__ = "blog_categories"

    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)

    # Relationships
    blogs = relationship("Blog", back_populates="category")

    def __repr__(self):
        return f"<BlogCategory(id={self.id}, name={self.name})>"


class BlogTag(BaseModel):
    """
    Model for blog tags
    Used to tag and filter blog posts
    """

    __tablename__ = "blog_tags"

    name = Column(String(50), nullable=False, unique=True)

    # Relationships
    blogs = relationship("Blog", secondary=blog_tag_association, back_populates="tags")

    def __repr__(self):
        return f"<BlogTag(id={self.id}, name={self.name})>"


class Blog(BaseModel):
    """
    Model for blog posts
    Stores blog content, images, and metadata
    """

    __tablename__ = "blogs"

    # Relationships
    category_id = Column(Integer, ForeignKey("blog_categories.id"), nullable=True)

    # Blog content
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(String(500), nullable=True)
    image_url = Column(String(255), nullable=True)

    # Blog metadata
    view_count = Column(Integer, default=0)
    is_published = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)

    # Blog type for UI placement
    blog_type = Column(String(50), nullable=True)  # e.g., "explore", "recipe", "workout"

    # Relationships
    category = relationship("BlogCategory", back_populates="blogs")
    tags = relationship("BlogTag", secondary=blog_tag_association, back_populates="blogs")

    def __repr__(self):
        return f"<Blog(id={self.id}, title={self.title})>"
