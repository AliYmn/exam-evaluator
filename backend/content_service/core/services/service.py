from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import UploadFile


class ContentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def upload_answer_key(self, answer_key: UploadFile, user_id: int) -> None:
        pass
