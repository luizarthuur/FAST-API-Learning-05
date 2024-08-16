from typing import List

from fastapi import APIRouter, status, Depends, HTTPException, Response

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models.artigo_model import ArtigoModel
from models.usuario_model import usuario_model
from schemas.artigo_schema import artigoSchema
from core.deps import get_session, get_current_user

router = APIRouter()

#POST Artigo

@router.post('/', status_code=status.HTTP_201_CREATED, response_model=artigoSchema)
async def postartigo(artigo: artigoSchema, usuario_logado: usuario_model = Depends(get_current_user), db: AsyncSession = Depends(get_session)):
    novo_artigo: ArtigoModel = ArtigoModel(titulo=artigo.titulo, descricao=artigo.descricao, url_fonte=artigo.url_fonte, usuario_id=usuario_logado.id)

    db.add(novo_artigo)
    await db.commit()

    return novo_artigo

#GET Artigos

@router.get('/', response_model=List[artigoSchema])
async def getartigos(db: AsyncSession = Depends(get_session)):
    async with db as session:
        query= select(ArtigoModel)
        result = await session.execute(query)
        artigos: List[ArtigoModel] = result.scalars().unique().all()

        return artigos
    
#GET Artigo

@router.get('/{artigo_id}', response_model=artigoSchema, status_code=status.HTTP_200_OK)
async def getartigo(artigo_id :int , db: AsyncSession = Depends(get_session)):
    async with db as session:
        query = select(ArtigoModel).filter(ArtigoModel.id == artigo_id)
        result = await session.execute(query)
        artigo: ArtigoModel = result.scalars().unique().one_or_none()

        if artigo:
            return artigo
        else:
            raise HTTPException(detail='Artigo não encontrado', status_code=status.HTTP_404_NOT_FOUND)
        
#PUT Artigo
@router.put('/{artigo_id}', response_model=artigoSchema, status_code=status.HTTP_202_ACCEPTED)
async def putartigo(artigo_id: int, artigo: artigoSchema, db: AsyncSession = Depends(get_session), usuario_logado: usuario_model = Depends(get_current_user)):
    async with db as session:
        query = select(ArtigoModel).filter(ArtigoModel.id == artigo_id)
        result = await session.execute(query)
        artigo_up: ArtigoModel = result.scalars().unique().one_or_none()

        if artigo_up:
            if usuario_logado.id != artigo_up.usuario_id:
                raise HTTPException(detail='Você não tem permissão para atualizar este artigo', status_code=status.HTTP_403_FORBIDDEN)

            if artigo.titulo:
                artigo_up.titulo = artigo.titulo
            if artigo.descricao:
                artigo_up.descricao = artigo.descricao
            if artigo.url_fonte:
                artigo_up.url_fonte = artigo.url_fonte

            await session.commit()

            return artigo_up
        else:
            raise HTTPException(detail='Artigo não encontrado', status_code=status.HTTP_404_NOT_FOUND)

        
#DEL Artigo
@router.delete('/{artigo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delartigo(artigo_id: int, db: AsyncSession = Depends(get_session), usuario_logado: usuario_model = Depends(get_current_user)):
    async with db as session:
        query = select(ArtigoModel).filter(ArtigoModel.id == artigo_id).filter(ArtigoModel.usuario_id == usuario_logado.id)
        result = await session.execute(query)
        artigo_del: ArtigoModel = result.scalars().unique().one_or_none()

        if artigo_del:
            if usuario_logado.id != artigo_del.usuario_id:
                raise HTTPException(detail='Você não tem permissão para deletar este artigo', status_code=status.HTTP_403_FORBIDDEN)
            await session.delete(artigo_del)
            await session.commit()
            
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        else:
            raise HTTPException(detail='Artigo não encontrado', status_code=status.HTTP_404_NOT_FOUND)
        
