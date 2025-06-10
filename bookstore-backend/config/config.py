import os
from typing import ClassVar

from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from pathlib import Path


# Get the path to the .env file from the environment variable
env_file_path = os.getenv("ENV_FILE_PATH", "config/.env")

# Load the .env file from the specified path
load_dotenv(dotenv_path=Path(env_file_path))


class Settings(BaseSettings):
    SERVICE_NAME: str = "Online BookStore Service"
    PROJECT_VERSION: str = "0.0.1"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # Database settings
    DB_USER: str = os.getenv("USER_DB_USER", "user")
    DB_PASSWORD: str = os.getenv("USER_DB_PASSWORD", "password")
    DB_NAME: str = os.getenv("USER_DB_NAME", "bookstore")
    DB_HOST: str = os.getenv("USER_DB_HOST", "localhost")
    DB_PORT: str = os.getenv("USER_DB_PORT", "5432")

    # Construct the database URL
    DB_URL: str = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    # Service Base url
    BASE_URL: ClassVar[str] = os.getenv('BASE_URL', 'http://localhost:8000')

    # Security settings
    SECRET_KEY: str = os.getenv('SECRET_KEY', "defaultsecretkey")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', 200))
    ALGORITHM: str = os.getenv('ALGORITHM', "HS256")

    DEFAULT_USER_PROFILE: ClassVar[str] ="https://cdn-icons-png.flaticon.com/128/149/149071.png"

    class Config:
        # env_file = env_file_path
        extra = "allow"


settings = Settings()
