from datetime import datetime
import requests
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session
import openai

from libs.models.blog import Blog, BlogCategory, BlogTag
from libs.settings import settings
from libs.helper.space import SpaceService


class ContentScheduleService:
    def __init__(self, db: Session):
        self.db = db
        self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
        self.space_service = SpaceService()

    def generate_general_blog(self, topic: Optional[str] = None, language: str = "en") -> int:
        """
        Generate a general blog post about intermittent fasting, healthy eating, or diet

        Args:
            topic: Optional specific topic to generate content for
            language: Language for the blog post (en or tr)

        Returns:
            int: ID of the created blog post
        """
        # Generate complete blog content including title, content, summary, category and tags
        blog_data = self._generate_complete_blog_content(topic, language)

        # Check if a blog with this title already exists
        if self._blog_title_exists(blog_data["title"]):
            return 0

        # Generate and upload an image for the blog
        image_url = self._generate_and_upload_image(blog_data["title"], "blog")

        # Get or create the category
        category = self._get_or_create_category(blog_data["category"], language)

        # Get or create tags
        tags = self._get_or_create_tags(blog_data["tags"])

        # Create the blog post
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

        # Add tags to the blog post
        for tag in tags:
            blog.tags.append(tag)

        self.db.commit()

        # Publish the blog
        self.publish_blog(blog.id)

        return blog.id

    def generate_recipe_blog(self, cuisine_type: Optional[str] = None, language: str = "en") -> int:
        """
        Generate a recipe blog post related to intermittent fasting, healthy eating, or diet

        Args:
            cuisine_type: Optional specific cuisine type to generate recipe for
            language: Language for the blog post (en or tr)

        Returns:
            int: ID of the created blog post
        """
        # Generate complete recipe content including title, content, summary, category and tags
        recipe_data = self._generate_complete_recipe_content(cuisine_type, language)

        # Check if a blog with this title already exists
        if self._blog_title_exists(recipe_data["title"]):
            return 0

        # Generate and upload an image for the recipe
        image_url = self._generate_and_upload_image(recipe_data["title"], "recipe")

        # Get or create the category
        category = self._get_or_create_category(recipe_data["category"], language)

        # Get or create tags
        tags = self._get_or_create_tags(recipe_data["tags"])

        # Create the blog post
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

        # Add tags to the blog post
        for tag in tags:
            blog.tags.append(tag)

        self.db.commit()

        # Publish the blog
        self.publish_blog(blog.id)

        return blog.id

    def get_blog_by_id(self, blog_id: int) -> Blog:
        """
        Get a blog post by ID
        """
        result = self.db.execute(select(Blog).where(Blog.id == blog_id, Blog.deleted_date.is_(None)))
        return result.scalars().first()

    def publish_blog(self, blog_id: int) -> bool:
        """
        Publish a blog post
        Returns True if successful, False otherwise
        """
        blog = self.get_blog_by_id(blog_id)
        if not blog:
            return False

        blog.is_published = True
        blog.updated_date = datetime.now()
        self.db.commit()
        return True

    def _blog_title_exists(self, title: str) -> bool:
        """
        Check if a blog with the given title already exists

        Args:
            title: Blog title to check

        Returns:
            bool: True if a blog with this title exists, False otherwise
        """
        result = self.db.execute(select(Blog).where(Blog.title == title, Blog.deleted_date.is_(None)))
        return result.scalars().first() is not None

    def _generate_complete_blog_content(self, topic: Optional[str], language: str) -> dict:
        """
        Generate complete blog content including title, content, summary, category and tags using OpenAI

        Args:
            topic: Optional topic for the blog post
            language: Language for the content (en or tr)

        Returns:
            dict: Complete blog data including title, content, summary, category and tags
        """
        if language == "tr":
            if topic:
                prompt = f"""
                "{topic}" hakkında kapsamlı bir blog yazısı oluştur.
                """
            else:
                prompt = """
                Aralıklı oruç, sağlıklı beslenme veya diyet ile ilgili ilgi çekici bir konu seç ve bu konu hakkında kapsamlı bir blog yazısı oluştur.
                """

            prompt += """
            Yanıtını aşağıdaki JSON formatında ver:
            {
                "title": "Blog yazısı için SEO dostu, çekici bir başlık",
                "content": "Markdown formatında tam blog içeriği (1000-1500 kelime). Giriş, ana bölümler ve sonuç içermeli.",
                "summary": "Blog yazısının kısa bir özeti (maksimum 150 kelime)",
                "category": "Blog için en uygun kategori (Genel Sağlık, Beslenme, Aralıklı Oruç, Egzersizler, vb.)",
                "tags": ["etiket1", "etiket2", "etiket3", "etiket4", "etiket5"]
            }

            Etiketler, blog içeriğiyle alakalı olmalı ve en fazla 5 tane olmalı.
            """
            system_content = "Sen aralıklı oruç, beslenme ve sağlık konularında uzmanlaşmış bir içerik üreticisisin."
        else:
            if topic:
                prompt = f"""
                Create a comprehensive blog post about "{topic}".
                """
            else:
                prompt = """
                Choose an interesting topic related to intermittent fasting, healthy eating, or diet, and create a comprehensive blog post about this topic.
                """

            prompt += """
            Provide your response in the following JSON format:
            {
                "title": "SEO-friendly, engaging title for the blog post",
                "content": "Full blog content in Markdown format (1000-1500 words). Should include introduction, main sections, and conclusion.",
                "summary": "Brief summary of the blog post (maximum 150 words)",
                "category": "Most appropriate category for the blog (General Health, Nutrition, Intermittent Fasting, Workouts, etc.)",
                "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"]
            }

            Tags should be relevant to the blog content and maximum 5 tags.
            """
            system_content = "You are a health and fitness content creator specializing in intermittent fasting, nutrition, and wellness."

        response = self.openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": system_content}, {"role": "user", "content": prompt}],
            max_tokens=3000,
            temperature=0.7,
            response_format={"type": "json_object"},
        )

        try:
            import json

            blog_data = json.loads(response.choices[0].message.content)
            return blog_data
        except Exception as e:
            raise Exception(f"Failed to parse AI response as JSON: {str(e)}")

    def _generate_complete_recipe_content(self, cuisine_type: Optional[str], language: str) -> dict:
        """
        Generate complete recipe content including title, content, summary, category and tags using OpenAI

        Args:
            cuisine_type: Optional type of cuisine for the recipe
            language: Language for the content (en or tr)

        Returns:
            dict: Complete recipe data including title, content, summary, category and tags
        """
        if language == "tr":
            if cuisine_type:
                prompt = f"""
                Aralıklı oruç veya sağlıklı beslenme için uygun bir {cuisine_type} tarifi oluştur.
                """
            else:
                prompt = """
                Aralıklı oruç veya sağlıklı beslenme için uygun bir tarif oluştur. Önce bir mutfak türü seç (örn. Akdeniz, Asya, Türk, ketojenik, düşük karbonhidratlı vb.) ve bu mutfak türüne uygun bir tarif oluştur.
                """

            prompt += """
            Yanıtını aşağıdaki JSON formatında ver:
            {
                "title": "Tarif için iştah açıcı, çekici bir başlık",
                "content": "Markdown formatında tam tarif içeriği. Giriş, malzemeler, hazırlama adımları, besin değerleri ve ipuçları içermeli.",
                "summary": "Tarifin kısa bir özeti (maksimum 150 kelime)",
                "category": "Tarif için en uygun kategori (genellikle 'Tarifler' olacaktır)",
                "tags": ["etiket1", "etiket2", "etiket3", "etiket4", "etiket5"]
            }

            Etiketler, tarif içeriğiyle alakalı olmalı ve en fazla 5 tane olmalı.
            """
            system_content = "Sen aralıklı oruç ve beslenme odaklı diyetler için sağlıklı tarifler konusunda uzmanlaşmış bir mutfak uzmanısın."
        else:
            if cuisine_type:
                prompt = f"""
                Create a recipe suitable for intermittent fasting or healthy eating in {cuisine_type} cuisine.
                """
            else:
                prompt = """
                Create a recipe suitable for intermittent fasting or healthy eating. First choose a cuisine type (e.g., Mediterranean, Asian, Turkish, ketogenic, low-carb, etc.) and then create a recipe appropriate for that cuisine.
                """

            prompt += """
            Provide your response in the following JSON format:
            {
                "title": "Appetizing, engaging title for the recipe",
                "content": "Full recipe content in Markdown format. Should include introduction, ingredients, preparation steps, nutritional information, and tips.",
                "summary": "Brief summary of the recipe (maximum 150 words)",
                "category": "Most appropriate category for the recipe (usually will be 'Recipes')",
                "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"]
            }

            Tags should be relevant to the recipe content and maximum 5 tags.
            """
            system_content = "You are a culinary expert specializing in healthy recipes for intermittent fasting and nutrition-focused diets."

        response = self.openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": system_content}, {"role": "user", "content": prompt}],
            max_tokens=3000,
            temperature=0.7,
            response_format={"type": "json_object"},
        )

        try:
            import json

            recipe_data = json.loads(response.choices[0].message.content)
            return recipe_data
        except Exception as e:
            raise Exception(f"Failed to parse AI response as JSON: {str(e)}")

    def _get_or_create_category(self, category_name: str, language: str) -> BlogCategory:
        """
        Get an existing category or create a new one

        Args:
            category_name: Name of the category
            language: Language for the category description

        Returns:
            BlogCategory: Category object
        """
        # Check if the category exists
        result = self.db.execute(
            select(BlogCategory).where(BlogCategory.name == category_name, BlogCategory.deleted_date.is_(None))
        )
        category = result.scalars().first()

        # If the category doesn't exist, create it
        if not category:
            if language == "tr":
                description = f"{category_name.lower()} ile ilgili makaleler"
            else:
                description = f"Articles related to {category_name.lower()}"

            category = BlogCategory(name=category_name, description=description)
            self.db.add(category)
            self.db.commit()

        return category

    def _get_or_create_tags(self, tag_names: list) -> List[BlogTag]:
        """
        Get existing tags or create new ones

        Args:
            tag_names: List of tag names

        Returns:
            List[BlogTag]: List of tag objects
        """
        tag_objects = []
        for tag_name in tag_names:
            # Check if the tag exists
            result = self.db.execute(select(BlogTag).where(BlogTag.name == tag_name, BlogTag.deleted_date.is_(None)))
            tag = result.scalars().first()

            # If the tag doesn't exist, create it
            if not tag:
                tag = BlogTag(name=tag_name)
                self.db.add(tag)
                self.db.commit()

            tag_objects.append(tag)

        return tag_objects

    def _generate_and_upload_image(self, title: str, image_type: str) -> str:
        """
        Generate an image using DALL-E and upload it to DigitalOcean Space

        Args:
            title: Blog post title to generate image for
            image_type: Type of image to generate (blog or recipe)

        Returns:
            str: URL of the uploaded image

        Raises:
            Exception: If image generation or upload fails
        """
        try:
            # Generate image prompt based on title and type
            if image_type == "recipe":
                prompt = f"A professional food photography style image of {title}. The dish should look appetizing, healthy, and well-presented."
            else:
                prompt = f"A conceptual image representing {title}. The image should be related to health, fitness, or nutrition."

            # Generate image using DALL-E
            response = self.openai_client.images.generate(
                model="dall-e-3", prompt=prompt, size="1024x1024", quality="standard", n=1
            )

            image_url = response.data[0].url

            # Download the image
            image_response = requests.get(image_url)
            if image_response.status_code != 200:
                raise Exception(f"Failed to download image from URL: {image_url}")

            # Determine the folder based on image type
            folder = "blog" if image_type == "blog" else "blog/recipes"

            # Create a unique filename based on the title
            file_name = f"{title.lower().replace(' ', '_')}.png"

            # Upload directly to DigitalOcean Space using boto3
            object_key = f"{folder}/{file_name}"
            self.space_service.client.put_object(
                Bucket=self.space_service.bucket_name,
                Key=object_key,
                Body=image_response.content,
                ACL="public-read",
                ContentType="image/png",
            )

            # Generate the URL for the uploaded file
            file_url = f"{self.space_service.cdn_url}/{object_key}"

            return file_url

        except Exception as e:
            # Raise the exception with a clear message
            raise Exception(f"Failed to generate or upload image: {str(e)}")
