"""
DigitalOcean Space service for image upload and management.
This module provides functionality to interact with DigitalOcean Spaces
for storing and retrieving images and other files.
"""

import os
import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime
import boto3
from botocore.exceptions import ClientError
from fastapi import UploadFile
from libs import settings


class SpaceService:
    """Service for interacting with DigitalOcean Spaces."""

    def __init__(self):
        """Initialize the SpaceService with DigitalOcean credentials."""
        self.session = boto3.session.Session()
        self.client = self.session.client(
            "s3",
            region_name=settings.DIGITALOCEAN_REGION,
            endpoint_url=settings.DIGITALOCEAN_ENDPOINT_URL,
            aws_access_key_id=settings.DIGITALOCEAN_ACCESS_KEY,
            aws_secret_access_key=settings.DIGITALOCEAN_SECRET_KEY,
        )
        self.bucket_name = settings.DIGITALOCEAN_BUCKET_NAME
        self.cdn_url = settings.DIGITALOCEAN_CDN_URL

    async def upload_image(self, file: UploadFile, folder: str = "images", public: bool = True) -> Dict[str, Any]:
        """
        Upload an image to DigitalOcean Space.

        Args:
            file: The image file to upload
            folder: The folder path within the bucket (default: 'images')
            public: Whether the file should be publicly accessible (default: True)

        Returns:
            Dict containing the uploaded file information
        """
        # Generate a unique filename to avoid collisions
        file_extension = os.path.splitext(file.filename)[1].lower()
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        new_filename = f"{timestamp}_{unique_id}{file_extension}"

        # Create the full path for the file
        file_path = f"{folder}/{new_filename}" if folder else new_filename

        # Set the appropriate ACL (Access Control List)
        acl = "public-read" if public else "private"

        try:
            # Read file content
            contents = await file.read()

            # Upload to DigitalOcean Space
            self.client.put_object(
                Bucket=self.bucket_name, Key=file_path, Body=contents, ACL=acl, ContentType=file.content_type
            )

            # Reset file cursor for potential future use
            await file.seek(0)

            # Generate the URL for the uploaded file
            file_url = f"{self.cdn_url}/{file_path}" if public else None

            return {
                "filename": new_filename,
                "original_filename": file.filename,
                "content_type": file.content_type,
                "size": len(contents),
                "path": file_path,
                "url": file_url,
                "public": public,
                "uploaded_at": datetime.now().isoformat(),
            }

        except ClientError as e:
            # Log the error and re-raise
            print(f"Error uploading to DigitalOcean Space: {str(e)}")
            raise

    async def delete_image(self, file_path: str) -> bool:
        """
        Delete an image from DigitalOcean Space.

        Args:
            file_path: The path of the file to delete

        Returns:
            bool: True if deletion was successful, False otherwise
        """
        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=file_path)
            return True
        except ClientError as e:
            print(f"Error deleting from DigitalOcean Space: {str(e)}")
            return False

    async def list_images(self, folder: str = "images") -> List[Dict[str, Any]]:
        """
        List all images in a specific folder.

        Args:
            folder: The folder path to list images from

        Returns:
            List of dictionaries containing file information
        """
        try:
            response = self.client.list_objects_v2(Bucket=self.bucket_name, Prefix=folder)

            if "Contents" not in response:
                return []

            files = []
            for item in response["Contents"]:
                file_path = item["Key"]
                file_name = os.path.basename(file_path)

                files.append(
                    {
                        "filename": file_name,
                        "path": file_path,
                        "url": f"{self.cdn_url}/{file_path}",
                        "size": item["Size"],
                        "last_modified": item["LastModified"].isoformat(),
                    }
                )

            return files

        except ClientError as e:
            print(f"Error listing images from DigitalOcean Space: {str(e)}")
            return []

    async def get_image_url(self, file_path: str) -> Optional[str]:
        """
        Get the URL for an image.

        Args:
            file_path: The path of the file

        Returns:
            str: The URL of the file or None if file doesn't exist
        """
        try:
            # Check if file exists
            self.client.head_object(Bucket=self.bucket_name, Key=file_path)

            # Return the URL
            return f"{self.cdn_url}/{file_path}"

        except ClientError:
            # File doesn't exist
            return None

    async def get_presigned_url(self, file_path: str, expiration: int = 3600) -> Optional[str]:
        """
        Generate a presigned URL for a file.

        Args:
            file_path: The path of the file
            expiration: The expiration time in seconds (default: 1 hour)

        Returns:
            str: The presigned URL or None if generation fails
        """
        try:
            url = self.client.generate_presigned_url(
                "get_object", Params={"Bucket": self.bucket_name, "Key": file_path}, ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            print(f"Error generating presigned URL: {str(e)}")
            return None

    async def upload_multiple_images(
        self, files: List[UploadFile], folder: str = "images", public: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Upload multiple images to DigitalOcean Space.

        Args:
            files: List of files to upload
            folder: The folder path within the bucket (default: 'images')
            public: Whether the files should be publicly accessible (default: True)

        Returns:
            List of dictionaries containing uploaded file information
        """
        results = []
        for file in files:
            result = await self.upload_image(file, folder, public)
            results.append(result)
        return results
