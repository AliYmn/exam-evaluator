import json
from datetime import datetime
import requests
from typing import List

from sqlalchemy import select
from sqlalchemy.orm import Session
import openai

from libs.models.blog import Blog, BlogCategory, BlogTag
from libs.settings import settings
from libs.helper.space import SpaceService
from .prompts import (
    get_blog_prompt_en,
    get_blog_prompt_tr,
    get_recipe_prompt_en,
    get_recipe_prompt_tr,
    get_blog_system_content_en,
    get_blog_system_content_tr,
    get_recipe_system_content_en,
    get_recipe_system_content_tr,
    get_image_prompt,
)


class ContentScheduleService:
    def __init__(self, db: Session):
        self.db = db
        self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.space_service = SpaceService()

    def generate_general_blog(self, language: str = "en") -> int:
        blog_data = self._generate_complete_blog_content(language)
        if self._blog_title_exists(blog_data["title"]):
            return 0
        image_url = self._generate_and_upload_image(blog_data["title"], "blog")
        category = self._get_or_create_category(blog_data["category"], language)
        tags = self._get_or_create_tags(blog_data["tags"])
        blog = Blog(
            title=blog_data["title"],
            content=blog_data["content"],
            summary=blog_data["summary"],
            image_url=image_url,
            category_id=category.id,
            blog_type="explore",
            language=language,
            is_published=False,
        )
        self.db.add(blog)
        self.db.flush()
        for tag in tags:
            blog.tags.append(tag)
        self.db.commit()
        self.publish_blog(blog.id)
        return blog.id

    def generate_recipe_blog(self, language: str = "en") -> int:
        recipe_data = self._generate_complete_recipe_content(language)
        if self._blog_title_exists(recipe_data["title"]):
            return 0
        image_url = self._generate_and_upload_image(recipe_data["title"], "recipe")
        category = self._get_or_create_category(recipe_data["category"], language)
        tags = self._get_or_create_tags(recipe_data["tags"])
        blog = Blog(
            title=recipe_data["title"],
            content=recipe_data["content"],
            summary=recipe_data["summary"],
            image_url=image_url,
            category_id=category.id,
            blog_type="recipe",
            language=language,
            is_published=False,
        )
        self.db.add(blog)
        self.db.flush()
        for tag in tags:
            blog.tags.append(tag)
        self.db.commit()
        self.publish_blog(blog.id)
        return blog.id

    def get_blog_by_id(self, blog_id: int) -> Blog:
        result = self.db.execute(select(Blog).where(Blog.id == blog_id, Blog.deleted_date.is_(None)))
        return result.scalars().first()

    def publish_blog(self, blog_id: int) -> bool:
        blog = self.get_blog_by_id(blog_id)
        if not blog:
            return False
        blog.is_published = True
        blog.updated_date = datetime.now()
        self.db.commit()
        return True

    def _blog_title_exists(self, title: str) -> bool:
        result = self.db.execute(select(Blog).where(Blog.title == title, Blog.deleted_date.is_(None)))
        return result.scalars().first() is not None

    def _generate_complete_content(self, language: str, prompt_fn, system_fn) -> dict:
        prompt = prompt_fn()
        system_content = system_fn()
        response = self.openai_client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "system", "content": system_content}, {"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.9,
            max_tokens=3500,
        )
        response_message = response.choices[0].message
        return json.loads(response_message.content)

    def _generate_complete_blog_content(self, language: str) -> dict:
        recent_titles = []
        result = self.db.execute(
            select(Blog.title)
            .where(Blog.deleted_date.is_(None), Blog.language == language)
            .order_by(Blog.created_date.desc())
            .limit(10)
        )
        for row in result:
            recent_titles.append(row[0])
        lang_key = language.upper()

        def prompt_fn():
            if lang_key == "EN":
                return get_blog_prompt_en(recent_titles)
            elif lang_key == "TR":
                return get_blog_prompt_tr(recent_titles)

        def system_fn():
            if lang_key == "EN":
                return get_blog_system_content_en()
            elif lang_key == "TR":
                return get_blog_system_content_tr()

        return self._generate_complete_content(language, prompt_fn, system_fn)

    def _generate_complete_recipe_content(self, language: str) -> dict:
        recent_titles = []
        result = self.db.execute(
            select(Blog.title)
            .join(BlogCategory, Blog.category_id == BlogCategory.id)
            .where(Blog.deleted_date.is_(None), Blog.language == language, BlogCategory.name == "Recipes")
            .order_by(Blog.created_date.desc())
            .limit(10)
        )
        for row in result:
            recent_titles.append(row[0])
        lang_key = language.upper()

        def prompt_fn():
            if lang_key == "EN":
                return get_recipe_prompt_en(recent_titles)
            elif lang_key == "TR":
                return get_recipe_prompt_tr(recent_titles)

        def system_fn():
            if lang_key == "EN":
                return get_recipe_system_content_en()
            elif lang_key == "TR":
                return get_recipe_system_content_tr()

        return self._generate_complete_content(language, prompt_fn, system_fn)

    def _get_or_create_category(self, category_name: str, language: str) -> BlogCategory:
        result = self.db.execute(
            select(BlogCategory).where(BlogCategory.name == category_name, BlogCategory.deleted_date.is_(None))
        )
        category = result.scalars().first()
        if not category:
            language.upper()
            description = f"{category_name} category"
            category = BlogCategory(name=category_name, description=description)
            self.db.add(category)
            self.db.commit()
        return category

    def _get_or_create_tags(self, tag_names: list) -> List[BlogTag]:
        tag_objects = []
        for tag_name in tag_names:
            result = self.db.execute(select(BlogTag).where(BlogTag.name == tag_name, BlogTag.deleted_date.is_(None)))
            tag = result.scalars().first()
            if not tag:
                tag = BlogTag(name=tag_name)
                self.db.add(tag)
                self.db.commit()
            tag_objects.append(tag)
        return tag_objects

    def _generate_and_upload_image(self, title: str, image_type: str) -> str:
        prompt = get_image_prompt(title, image_type)
        dalle_response = self.openai_client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024",
            response_format="url",
        )
        image_url = dalle_response.data[0].url
        image_response = requests.get(image_url)
        folder = f"content/{image_type}"
        file_name = f"{title.replace(' ', '_')}.png"
        object_key = f"{folder}/{file_name}"
        self.space_service.client.put_object(
            Bucket=self.space_service.bucket_name,
            Key=object_key,
            Body=image_response.content,
            ACL="public-read",
            ContentType="image/png",
        )
        file_url = f"{self.space_service.cdn_url}/{object_key}"
        return file_url
