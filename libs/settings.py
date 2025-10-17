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

    # REDIS
    REDIS_PORT: int
    REDIS_HOST: str
    REDIS_PASSWORD: str
    REDIS_TTL: int
    REDIS_PREFIX: str
    FERNET_KEY: str

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
