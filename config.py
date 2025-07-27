# 환경변수 전담 설정

from pydantic.v1 import BaseSettings, Field
from functools import lru_cache

class Settings(BaseSettings):
    mongodb_uri: str = Field(..., env="MONGODB_URI")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()

# 애플리케이션 전역에서 재사용할 설정 인스턴스
settings = get_settings()