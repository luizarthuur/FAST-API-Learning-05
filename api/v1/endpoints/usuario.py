from typing import List, Optional, Any
from fastapi import APIRouter, status, Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models.usuario_model import usuario_model
from schemas.usuario_schema import UsuarioSchemaBase, UsuarioSchemaArtigos, UsuarioSchemaCreate, UsuarioSchemaUpdate
from core.deps import get_current_user, get_session
from core.security import gerar_hash_senha
from core.auth import autenticar, criar_token_acesso
from sqlalchemy.exc import IntegrityError

router = APIRouter()

#GET Logado
@router.get('/logado', response_model=UsuarioSchemaBase)
def getlogado(usuario_logado: usuario_model = Depends(get_current_user)):
    return usuario_logado

#POST / Signup
@router.post('/signup', response_model=UsuarioSchemaBase,status_code=status.HTTP_201_CREATED)
async def postusuario(usuario: UsuarioSchemaCreate, db: AsyncSession = Depends(get_session)):
    novo_usuario: usuario_model = usuario_model(nome = usuario.nome, sobrenome= usuario.sobrenome, email = usuario.email, senha=gerar_hash_senha(usuario.senha), e_admin = usuario.e_admin)
    async with db as session:
        try:
            session.add(novo_usuario)
            await session.commit()

            return novo_usuario
        except IntegrityError:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail='Já existe um usuário com este email cadastrado')
    
# GET Usuarios
@router.get('/',response_model=List[UsuarioSchemaBase],status_code=status.HTTP_200_OK)
async def getusuarios(db: AsyncSession = Depends(get_session)):
    async with db as session:
        query = select(usuario_model)
        result = await session.execute(query)
        usuarios: List[UsuarioSchemaBase] = result.scalars().unique().all()

        return usuarios
    
#GET Usuario
@router.get('/{usuario_id}', response_model=UsuarioSchemaArtigos, status_code=status.HTTP_200_OK)
async def getusuario(usuario_id: int, db: AsyncSession = Depends(get_session)):
    async with db as session:
        query = select(usuario_model).filter(usuario_model.id == usuario_id)
        result = await session.execute(query)

        usuario: UsuarioSchemaArtigos= result.scalars().unique().one_or_none()

        if usuario:
            return usuario
        else:
            raise HTTPException(detail='Usuário não encontrado', status_code=status.HTTP_404_NOT_FOUND)
        
#PUT Usuario
@router.put('/{usuario_id}', response_model=UsuarioSchemaBase, status_code=status.HTTP_202_ACCEPTED)
async def putusuario(usuario_id: int, usuario: UsuarioSchemaUpdate, db: AsyncSession = Depends(get_session)):
    async with db as session:
        query = select(usuario_model).filter(usuario_model.id == usuario_id)
        result = await session.execute(query)

        usuario_up: UsuarioSchemaBase= result.scalars().unique().one_or_none()

        if usuario_up:
            if usuario.nome:
                usuario_up.nome = usuario.nome
            if usuario.sobrenome:
                usuario_up.sobrenome = usuario.sobrenome
            if usuario.email:
                usuario_up.email = usuario.email
            if usuario.senha:
                usuario_up.nome = usuario.senha
            if usuario.e_admin:
                usuario_up.e_admin = usuario.e_admin
            if usuario.senha:
                usuario_up.senha = gerar_hash_senha(usuario.senha)

            await session.commit()

            return usuario_up
        else:
            raise HTTPException(detail='Usuário não encontrado', status_code=status.HTTP_404_NOT_FOUND)
        
 #DEL Usuario
@router.delete('/{usuario_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delusuario(usuario_id: int, db: AsyncSession = Depends(get_session)):
    async with db as session:
        query = select(usuario_model).filter(usuario_model.id == usuario_id)
        result = await session.execute(query)

        usuario_del: UsuarioSchemaArtigos= result.scalars().unique().one_or_none()

        if usuario_del:
            await session.delete(usuario_del)
            await session.commit()

            return Response(status_code=status.HTTP_204_NO_CONTENT)
        else:
            raise HTTPException(detail='Usuário não encontrado', status_code=status.HTTP_404_NOT_FOUND)

#POST Login
@router.post('/login') 
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_session)):
    
    usuario = await autenticar(email=form_data.username, senha=form_data.password, db=db)

    if not usuario:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Dados de acesso incorretos')
    
    else:
        return JSONResponse(content={'access_token': criar_token_acesso(sub=usuario.id), 'token_type': 'bearer'}, status_code=status.HTTP_200_OK)
    
