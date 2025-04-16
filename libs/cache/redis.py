from typing import Any, Optional, Union

from cryptography.fernet import Fernet
from redis.asyncio import ConnectionPool, Redis

from libs.settings import settings


class CacheService:
    _pool: Optional[ConnectionPool] = None
    _instance: Optional["CacheService"] = None

    def __new__(cls) -> "CacheService":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if not hasattr(self, "client"):
            if self._pool is None:
                self._pool = ConnectionPool(
                    host=settings.REDIS_HOST,
                    port=settings.REDIS_PORT,
                    password=settings.REDIS_PASSWORD,
                    db=0,
                    max_connections=20,
                    decode_responses=True,
                )
            self.client = Redis(connection_pool=self._pool)
            self.fernet = Fernet(settings.FERNET_KEY)
            self.prefix = settings.REDIS_PREFIX

    async def set_cache(self, key: str, value: Union[str, dict, list], expiration: Optional[int] = None) -> None:
        key = f"{self.prefix}{key}"
        value_str = str(value) if isinstance(value, (dict, list)) else value
        encrypted_value = self.fernet.encrypt(value_str.encode())
        await self.client.setex(key, expiration, encrypted_value)

    async def get_cache(self, key: str) -> Optional[Any]:
        key = f"{self.prefix}{key}"
        encrypted_value = await self.client.get(key)
        if encrypted_value:
            decrypted_value = self.fernet.decrypt(encrypted_value).decode()
            return decrypted_value
        return None

    async def delete_cache(self, key: str) -> None:
        key = f"{self.prefix}{key}"
        await self.client.delete(key)

    async def clear_all_cache(self) -> None:
        await self.client.flushdb()
