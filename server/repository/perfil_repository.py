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
from server.models.vinculo_perfil_curso_model import VinculoPerfilCurso
from server.models.interesse_model import Interesse
from server.schemas.cursor_schema import Cursor
from jose import JWTError, jwt
from server.models.perfil_phone_model import PerfilPhone
from server.models.curso_model import Curso
from server import utils
from sqlalchemy.sql import operators


class PerfilRepository:

    @staticmethod
    def get_operator_dictionary():
        return {
            'ge': operators.ge,
            'gt': operators.gt,
            'le': operators.le,
            'lt': operators.lt
        }

    @staticmethod
    def get_name_ilike_filter(nome_exibicao: str):
        return [
            Perfil.nome_exibicao_normalized.ilike(
               utils.normalize_string(f'%{nome_exibicao}%')
            )
        ]

    @staticmethod
    def get_default_cursor_filter(sort_field_key, cursor_value, _operator):
        return _operator(getattr(Perfil, sort_field_key), cursor_value)

    @staticmethod
    def get_int_cursor_filter(sort_field_key, cursor_value, _operator):
        return _operator(getattr(Perfil, sort_field_key), int(cursor_value))

    @staticmethod
    def get_cursor_filter_factory():
        return {
            "int": PerfilRepository.get_int_cursor_filter,
            "str": PerfilRepository.get_default_cursor_filter
        }

    @staticmethod
    def build_cursor_filter(cursor: Cursor):
        # Factory e builder descrevem como construir o filtro
        cursor_field_factory = PerfilRepository.get_cursor_filter_factory()
        cursor_operator_factory = PerfilRepository.get_operator_dictionary()
        cursor_field_type = cursor.sort_field_type
        cursor_field_builder = cursor_field_factory[cursor_field_type]
        # Retornando o resultado usando o builder com os argumentos
        cursor_field_key = cursor.sort_field_key
        cursor_value = cursor.value
        cursor_operator = cursor_operator_factory[cursor.operator]
        return cursor_field_builder(cursor_field_key, cursor_value, cursor_operator)

    def __init__(self, db_session: AsyncSession, environment: Optional[Environment] = None):
        self.db_session = db_session
        self.environment = environment

    def encode_cursor(self, cursor: dict):
        return jwt.encode(
            cursor,
            self.environment.CURSOR_TOKEN_SECRET_KEY,
            algorithm=self.environment.CURSOR_TOKEN_ALGORITHM
        )

    async def find_profiles_by_filters_paginated(self, limit, cursor: Cursor, filters) -> dict:

        # Offset a partir do cursor, geralmente é pelo ID
        # Limit + 1 para capturar o ultimo perfil. Esse último perfil será usado no cursor
        if cursor:
            filters.append(PerfilRepository.build_cursor_filter(cursor))

        stmt = (
            select(Perfil, VinculoPerfilCurso, VinculoPerfilInteresse, PerfilPhone).
            outerjoin(
                VinculoPerfilCurso,
                VinculoPerfilCurso.id_perfil == Perfil.id,
            ).
            outerjoin(
                Curso,
                VinculoPerfilCurso.id_curso == Curso.id,
            ).
            outerjoin(
                VinculoPerfilInteresse,
                VinculoPerfilInteresse.id_perfil == Perfil.id,
            ).
            outerjoin(
                Interesse,
                VinculoPerfilInteresse.id_interesse == Interesse.id,
            ).
            options(
                selectinload(Perfil.vinculos_perfil_curso),
                selectinload(Perfil.vinculos_perfil_interesse),
                selectinload(Perfil.phones),
                selectinload(PerfilPhone.tipo_contato),
                selectinload(Perfil.emails),
                selectinload(VinculoPerfilInteresse.interesse),
                selectinload(VinculoPerfilCurso.curso)
            ).
            where(*filters).
            limit(limit + 1).
            order_by(Perfil.nome_exibicao.asc())
        )

        # Executando a query
        query = await self.db_session.execute(stmt)
        perfis = query.scalars().unique().all()

        # Capturando o ultimo perfil e setando o next_cursor
        next_cursor = None
        if len(perfis) == (limit+1):
            last_profile = perfis[limit]
            next_cursor = {
                'sort_field_key': cursor.sort_field_key if cursor else 'nome_exibicao',
                'sort_field_type': cursor.sort_field_type if cursor else 'str',
                'operator': 'ge',
                'value': last_profile.nome_exibicao
            }

        return {
            "items": perfis[:limit],
            "next_cursor": self.encode_cursor(next_cursor) if next_cursor else None,
        }

