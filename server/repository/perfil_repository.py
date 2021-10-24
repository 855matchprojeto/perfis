from server.configuration.db import AsyncSession
from server.models.permissao_model import Permissao
from server.models.vinculo_permissao_funcao_model import VinculoPermissaoFuncao
from sqlalchemy import select
from typing import List, Optional
from server.configuration.environment import Environment
from sqlalchemy.orm import selectinload
from sqlalchemy import and_
from server.models.perfil_model import Perfil
from server.models.vinculo_perfil_interesse_model import VinculoPerfilInteresse
from server.models.interesse_model import Interesse
from server.schemas.cursor_schema import Cursor
from jose import JWTError, jwt


class PerfilRepository:

    CURSOR_TYPE_HANDLER = {
        "int": int
    }

    def __init__(self, db_session: AsyncSession, environment: Optional[Environment] = None):
        self.db_session = db_session
        self.environment = environment

    def encode_cursor(self, cursor: dict):
        return jwt.encode(
            cursor,
            self.environment.CURSOR_TOKEN_SECRET_KEY,
            algorithm=self.environment.CURSOR_TOKEN_ALGORITHM
        )

    def handle_cursor_type(self, cursor: Cursor):
        cursor_type = cursor.sort_field_type
        cursor_value = cursor.value
        return PerfilRepository.CURSOR_TYPE_HANDLER[cursor_type](cursor_value)

    async def find_profiles_by_filters_paginated(self, limit, cursor: Cursor, filters) -> dict:

        # Offset a partir do cursor, geralmente é pelo ID
        # Limit + 1 para capturar o ultimo perfil. Esse último perfil será usado no cursor
        if cursor:
            cursor_value = self.handle_cursor_type(cursor)
            filters.append(getattr(Perfil, cursor.sort_field_key) >= cursor_value)

        stmt = (
            select(Perfil, VinculoPerfilInteresse).
            options(
                selectinload(Perfil.vinculos_perfil_curso),
                selectinload(Perfil.vinculos_perfil_interesse),
                selectinload(Perfil.entidade_phone),
                selectinload(Perfil.entidade_email),
                selectinload(VinculoPerfilInteresse.interesse)
            ).
            where(*filters).
            limit(limit + 1)
        )

        # Executando a query
        query = await self.db_session.execute(stmt)
        perfis = query.scalars().all()

        next_cursor = None
        if len(perfis) == (limit+1):
            last_profile = perfis[limit]
            next_cursor = {
                'sort_field_key': 'id',
                'sort_field_type': 'int',
                'value': last_profile.id
            }

        # Capturando o ultimo perfil
        return {
            "items": perfis[:limit],
            "next_cursor": self.encode_cursor(next_cursor) if next_cursor else None,
        }


