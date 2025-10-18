from pydantic_settings import BaseSettings


class Config(BaseSettings):
    # API Settings
    DEBUG: bool
    API_STR: str = "/api/v1"
    PROJECT_NAME: str = "{project_name} Service API"
    PROJECT_VERSION: str = "v1"

    # JWT Settings
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # POSTGRES
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PORT: int

    # RabbitMQ (Optional - falls back to Redis if not provided)
    RABBITMQ_PASS: str = ""
    RABBITMQ_USER: str = ""
    RABBITMQ_HOST: str = ""
    RABBITMQ_PORT: int = 5672

    # REDIS
    REDIS_PORT: int
    REDIS_HOST: str
    REDIS_PASSWORD: str
    REDIS_TTL: int
    REDIS_PREFIX: str
    FERNET_KEY: str

    # Celery Worker (Optional - uses defaults if not provided)
    CONTENT_QUEUE_NAME: str = "content_queue"
    CONTENT_WORKER_NAME: str = "content_worker"

    # GEMINI (Google)
    GEMINI_API_KEY: str

    # Sentry (Optional)
    SENTRY_DSN: str = ""
    SENTRY_ENVIRONMENT: str = "development"
    SENTRY_ENABLED: bool = False
    ENV_NAME: str = "development"

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra env vars


settings = Config()
