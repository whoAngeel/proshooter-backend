from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    # Base de datos
    DATABASE_URL: str
    POSTGRES_USER: str = "angel"
    POSTGRES_PASSWORD: str = "angel"
    POSTGRES_DB: str = "proshooter_db_dev"
    DB_PORT: int = 5432

    # Aplicación
    SECRET_KEY: str
    PROJECT_NAME: str = "ProShooter API"
    VERSION: str = "1.0.0"
    API_IMAGE: str = "subkey/proshooter-api:dev"
    BUILD_TARGET: str = "development"
    VOLUME_MOUNT: str = "./:/app"
    START_COMMAND: str = (
        "alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload"
    )

    # Servidor
    HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # Para compatibilidad con código existente
    @property
    def PORT(self) -> int:
        return self.API_PORT

    # Seguridad
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 720  # 12 horas

    # CORS
    CORS_ORIGINS: list = ["*"]

    # Entorno
    ENV: str = "dev"
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"

    class Config:
        env_file = ".env.dev"
        case_sensitive = True
        extra = "forbid"


settings = Settings()
