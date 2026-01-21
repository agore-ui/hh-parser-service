from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    APP_NAME: str = "HH Parser Service"
    APP_ENV: str = "development"
    DEBUG: bool = True
    
    DATABASE_URL: str
    REDIS_URL: str
    
    SECRET_KEY: str = "change-me-in-production"
    
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    HH_API_BASE_URL: str = "https://api.hh.ru"
    HH_API_TIMEOUT: int = 30
    
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
