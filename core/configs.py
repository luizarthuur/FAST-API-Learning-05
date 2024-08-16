from typing import List

from pydantic import BaseSettings
from sqlalchemy.ext.declarative import declarative_base

class Settings(BaseSettings):
    API_V1_STR: str = '/api/v1'
    DB_URL: str = 'postgresql+asyncpg://postgres:vistatech3011@localhost:5432/vista-tech-bd'
    DBBaseModel = declarative_base()

    JWT_SECRET: str = 'PCYHjmFR-MH_3cNTEJnGLudhWkkq0pp7baLSA7soq9o'
    ALGORITHM: str = 'HS256'

    """
    import secrets

    token: str = secrets.token_urlsafe(32)
    """

    #60 minutos * 24 horas * 7 dias => 1 semana em minutos

    ACESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    class Config:
        case_sensitive = True
    
settings: Settings = Settings()