import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    PROJECT_NAME: str = "ProShooter BACKEND"
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    VERSION: str = "1.0.0"

    class Config:
        env_file = ".env"




settings = Settings()
