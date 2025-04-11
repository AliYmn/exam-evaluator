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
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int

    # POSTGRES
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PORT: int

    # RabbitMQ
    RABBITMQ_PASS: str
    RABBITMQ_USER: str
    RABBITMQ_HOST: str
    RABBITMQ_PORT: int

    # REDIS
    REDIS_PORT: int
    REDIS_HOST: str
    REDIS_PASSWORD: str
    REDIS_TTL: int
    REDIS_PREFIX: str
    FERNET_KEY: str

    # Celery Worker
    AUTH_QUEUE_NAME: str
    AUTH_WORKER_NAME: str
    FIT_QUEUE_NAME: str
    FIT_WORKER_NAME: str
    TRACKER_QUEUE_NAME: str
    TRACKER_WORKER_NAME: str
    CONTENT_QUEUE_NAME: str
    CONTENT_WORKER_NAME: str

    # Email Settings
    MAIL_HOST: str = "smtp.gmail.com"
    MAIL_PORT: int = 587
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str

    # DigitalOcean Space
    DIGITALOCEAN_SECRET_KEY: str
    DIGITALOCEAN_CDN_URL: str
    DIGITALOCEAN_ACCESS_KEY: str
    DIGITALOCEAN_BUCKET_NAME: str
    DIGITALOCEAN_REGION: str = "nyc3"
    DIGITALOCEAN_ENDPOINT_URL: str = "https://nyc3.digitaloceanspaces.com"

    # GROQ
    GROQ_API_KEY: str
    GROQ_BASE_URL: str

    # OPENAI
    OPENAI_API_KEY: str
    OPENAI_BASE_URL: str

    # Sentry
    SENTRY_DSN: str
    SENTRY_ENVIRONMENT: str = "development"
    SENTRY_ENABLED: bool = False
    ENV_NAME: str = "development"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Config()
