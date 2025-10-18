from typing import Any, Optional

import redis
from cryptography.fernet import Fernet

from libs.settings import settings


class CacheService:
    client = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
        db=0,
    )
    fernet = Fernet(settings.FERNET_KEY)

    @staticmethod
    def set_cache(key: str, value: str, expiration: Optional[int] = None) -> None:
        key = f"{settings.REDIS_PREFIX}{key}"
        encrypted_value = CacheService.fernet.encrypt(str(value).encode())
        CacheService.client.setex(key, expiration, encrypted_value)

    @staticmethod
    def get_cache(key: str) -> Optional[Any]:
        key = f"{settings.REDIS_PREFIX}{key}"
        encrypted_value = CacheService.client.get(key)
        if encrypted_value:
            decrypted_value = CacheService.fernet.decrypt(encrypted_value).decode()
            return decrypted_value
        return None

    @staticmethod
    def delete_cache(key: str) -> None:
        key = f"{settings.REDIS_PREFIX}{key}"
        CacheService.client.delete(key)

    @staticmethod
    def clear_all_cache() -> None:
        CacheService.client.flushdb()
