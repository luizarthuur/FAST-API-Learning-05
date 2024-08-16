from pytz import timezone

from typing import Optional, List
from datetime import datetime, timedelta

from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from jose import jwt

from models.usuario_model import usuario_model
from core.configs import settings
from core.security import verificar_senha
from pydantic import EmailStr

oauth2_schema = OAuth2PasswordBearer(
    tokenUrl = f'{settings.API_V1_STR}/usuarios/login'
)

async def autenticar(email: EmailStr, senha: str, db: AsyncSession) -> Optional[usuario_model]:
    async with db as session: 
        query = select(usuario_model).filter(usuario_model.email == email)
        result = await session.execute(query)
        usuario: usuario_model = result.scalars().unique().one_or_none()

        if not usuario:
            return None
        
        if not verificar_senha(senha, usuario.senha):
            return None
        
        else: return usuario

def criartoken(tipotoken:str, tempodevidatoken: timedelta, sub: str) -> str:
    #documentação do token JSON
    #https://datacracker.ietf.org/doc/html/rfc7519#section-4.1.3
    payload={}
    sp = timezone('America/Sao_Paulo')
    expira = datetime.now(tz=sp) + tempodevidatoken

    payload['type'] = tipotoken
    payload['exp'] = expira
    payload['iat'] = datetime.now(tz=sp)
    payload['sub'] = str(sub)

    return jwt.encode(payload,settings.JWT_SECRET, algorithm=settings.ALGORITHM)

def criar_token_acesso(sub: str) -> str:
    #https://jwt.io

    return criartoken(tipotoken='acess_token', tempodevidatoken=timedelta(minutes=settings.ACESS_TOKEN_EXPIRE_MINUTES), sub=sub)
