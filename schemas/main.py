import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from fastapi import FastAPI

from core.configs import settings
from api.v1.api import api_router

app = FastAPI(title='Curso API - Segurança')

app.include_router(api_router, prefix=settings.API_V1_STR)

if __name__ == '__main__':
    import uvicorn

    uvicorn.run('main:app', host = '0.0.0.0', port=8000, log_level='info')


#TOKEN: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0eXBlIjoiYWNlc3NfdG9rZW4iLCJleHAiOjE3MjQ0MjE2ODEsImlhdCI6MTcyMzgxNjg4MSwic3ViIjoiNyJ9.aYrVoT26HiF_NHUG7U4GxhAuzZJptvXQ9xtFUHP8N1k
#TIPO: bearer