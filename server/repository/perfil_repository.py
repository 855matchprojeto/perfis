from server.configuration.db import AsyncSession
from server.models.permissao_model import Permissao
from server.models.vinculo_permissao_funcao_model import VinculoPermissaoFuncao
from sqlalchemy import select, update, insert, delete, literal_column
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
from server.models.perfil_email_model import PerfilEmail
from server.models.curso_model import Curso
from server import utils
from sqlalchemy.sql import operators
from server.configuration.exceptions import ProfileNotFoundException
from server.models.tipo_contato_model import TipoContato


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

    @staticmethod
    def get_all_entities_select_statement():
        stmt = (
            select(Perfil)
            .distinct()
            .outerjoin(
                VinculoPerfilCurso,
                VinculoPerfilCurso.id_perfil == Perfil.id,
            ).outerjoin(
                Curso,
                VinculoPerfilCurso.id_curso == Curso.id,
            ).outerjoin(
                VinculoPerfilInteresse,
                VinculoPerfilInteresse.id_perfil == Perfil.id,
            ).outerjoin(
                Interesse,
                VinculoPerfilInteresse.id_interesse == Interesse.id
            ).options(
                (
                    selectinload(Perfil.vinculos_perfil_curso).
                    selectinload(VinculoPerfilCurso.curso)
                ),
                (
                    selectinload(Perfil.vinculos_perfil_interesse).
                    selectinload(VinculoPerfilInteresse.interesse)
                ),
                (
                    selectinload(Perfil.phones).
                    selectinload(PerfilPhone.tipo_contato)
                ),
                selectinload(Perfil.emails),
                selectinload(Perfil.imagem_perfil)
            )
        )
        return stmt

    @staticmethod
    def get_default_select_statement():
        stmt = select(Perfil)
        return stmt

    def __init__(self, db_session: AsyncSession, environment: Optional[Environment] = None):
        self.db_session = db_session
        self.environment = environment

    def encode_cursor(self, cursor: dict):
        return jwt.encode(
            cursor,
            self.environment.CURSOR_TOKEN_SECRET_KEY,
            algorithm=self.environment.CURSOR_TOKEN_ALGORITHM
        )

    async def find_profile_by_guid(self, guid_perfil: str, load_all_entities=True) -> Perfil:
        stmt = (
            PerfilRepository.get_all_entities_select_statement()
            if load_all_entities
            else PerfilRepository.get_default_select_statement()
        ).where(
            Perfil.guid == guid_perfil
        )
        query = await self.db_session.execute(stmt)

        perfil = query.scalars().unique().first()
        if not perfil:
            raise ProfileNotFoundException(
                detail=f"O perfil de GUID={guid_perfil} n??o foi encontrado."
            )
        return perfil

    async def find_profile_by_guid_usuario(self, guid_usuario: str, load_all_entities=True) -> Perfil:

        stmt = (
            PerfilRepository.get_all_entities_select_statement()
            if load_all_entities
            else PerfilRepository.get_default_select_statement()
        ).where(
            Perfil.guid_usuario == guid_usuario
        )
        query = await self.db_session.execute(stmt)

        perfil = query.scalars().unique().first()
        return perfil

    async def find_profiles_by_filters_paginated(
        self, limit, encoded_cursor: str, cursor: Cursor, filters
    ) -> dict:

        # Offset a partir do cursor, geralmente ?? pelo ID
        # Limit + 1 para capturar o ultimo perfil. Esse ??ltimo perfil ser?? usado no cursor
        if cursor:
            filters.append(PerfilRepository.build_cursor_filter(cursor))
            filters.append(Perfil.id != cursor.id)

        stmt = (
            PerfilRepository.get_all_entities_select_statement()
        ).where(*filters).limit(limit+1).order_by(
            Perfil.nome_exibicao.asc()
        )

        # Executando a query
        query = await self.db_session.execute(stmt)
        perfis = query.scalars().unique().all()

        # Capturando o ultimo perfil e setando o next_cursor
        next_cursor = None
        if len(perfis) == (limit+1):
            last_profile: Perfil = perfis[limit]
            next_cursor = {
                'previous_encoded_cursor': encoded_cursor,
                'sort_field_key': cursor.sort_field_key if cursor else 'nome_exibicao',
                'sort_field_type': cursor.sort_field_type if cursor else 'str',
                'operator': 'ge',
                'value': last_profile.nome_exibicao,
                'id': last_profile.id
            }

        return {
            "items": perfis[:limit],
            "current_cursor": encoded_cursor,
            "next_cursor": self.encode_cursor(next_cursor) if next_cursor else None,
            "count": len(perfis[:limit])
        }

    async def insere_perfil(self, perfil_dict: dict) -> Perfil:
        stmt = (
            insert(Perfil).
            returning(literal_column('*')).
            values(**perfil_dict)
        )
        query = await self.db_session.execute(stmt)
        row_to_dict = dict(query.fetchone())
        return Perfil(**row_to_dict)

    async def atualiza_perfil_by_guid(self, guid_perfil, perfil_update_dict: dict) -> Perfil:
        stmt = (
            update(Perfil).
            returning(literal_column('*')).
            where(Perfil.guid == guid_perfil).
            values(**perfil_update_dict)
        )
        query = await self.db_session.execute(stmt)

        if query.rowcount == 0:
            raise ProfileNotFoundException(
                detail=f"O perfil de GUID={guid_perfil} n??o foi encontrado."
            )

        row_to_dict = dict(query.fetchone())
        perfil = Perfil(**row_to_dict)
        return perfil

    async def atualiza_perfil_by_guid_usuario(self, guid_usuario, perfil_update_dict: dict) -> Perfil:
        stmt = (
            update(Perfil).
            returning(literal_column('*')).
            where(Perfil.guid_usuario == guid_usuario).
            values(**perfil_update_dict)
        )
        query = await self.db_session.execute(stmt)

        if query.rowcount == 0:
            raise ProfileNotFoundException(
                detail=f"O perfil do usu??rio de GUID={guid_usuario} n??o foi encontrado."
            )

        row_to_dict = dict(query.fetchone())
        perfil = Perfil(**row_to_dict)
        return perfil

    async def delete_vinculos_curso_perfil(self, id_perfil: str):
        stmt = (
            delete(VinculoPerfilCurso).
            where(VinculoPerfilCurso.id_perfil == id_perfil)
        )
        await self.db_session.execute(stmt)

    async def delete_vinculos_interesse_perfil(self, id_perfil: str):
        stmt = (
            delete(VinculoPerfilInteresse).
            where(VinculoPerfilInteresse.id_perfil == id_perfil)
        )
        await self.db_session.execute(stmt)

    async def delete_phones_perfil(self, id_perfil: str):
        stmt = (
            delete(PerfilPhone).
            where(PerfilPhone.id_perfil == id_perfil)
        )
        await self.db_session.execute(stmt)

    async def delete_emails_perfil(self, id_perfil: str):
        stmt = (
            delete(PerfilEmail).
            where(PerfilEmail.id_perfil == id_perfil)
        )
        await self.db_session.execute(stmt)

    async def delete_perfil_by_id(self, id_perfil) -> None:
        stmt = (
            delete(Perfil).
            where(Perfil.id == id_perfil)
        )
        await self.db_session.execute(stmt)

    async def delete_perfil_by_guid(self, guid_perfil) -> None:

        # Capturando o ID do perfil
        perfil = await self.find_profile_by_guid(guid_perfil, load_all_entities=False)
        id_perfil = perfil.id

        # Deletando as entidades relacionadas
        await self.delete_vinculos_interesse_perfil(id_perfil)
        await self.delete_vinculos_curso_perfil(id_perfil)
        await self.delete_phones_perfil(id_perfil)
        await self.delete_emails_perfil(id_perfil)

        # Deleta a entidade principal
        await self.delete_perfil_by_id(id_perfil)

    async def delete_perfil(self, id_perfil) -> None:
        # Deletando as entidades relacionadas
        await self.delete_vinculos_interesse_perfil(id_perfil)
        await self.delete_vinculos_curso_perfil(id_perfil)
        await self.delete_phones_perfil(id_perfil)
        await self.delete_emails_perfil(id_perfil)

        # Deleta a entidade principal
        await self.delete_perfil_by_id(id_perfil)

    async def find_vinculo_perfil_curso(self, id_curso, id_perfil):
        stmt = (
            select(VinculoPerfilCurso).
            where(
                VinculoPerfilCurso.id_perfil == id_perfil,
                VinculoPerfilCurso.id_curso == id_curso
            )
        )

        # Executando a query
        query = await self.db_session.execute(stmt)
        return query.scalars().unique().first()

    async def insert_vinculo_perfil_curso(self, id_curso, id_perfil):
        stmt = (
            insert(VinculoPerfilCurso).
            values(
                id_curso=id_curso,
                id_perfil=id_perfil
            )
        )

        # Executando a query
        await self.db_session.execute(stmt)

    async def delete_vinculo_perfil_curso(self, id_curso, id_perfil):
        stmt = (
            delete(VinculoPerfilCurso).
            where(
                VinculoPerfilCurso.id_perfil == id_perfil,
                VinculoPerfilCurso.id_curso == id_curso
            )
        )

        # Executando a query
        await self.db_session.execute(stmt)

    async def find_vinculo_perfil_interesse(self, id_interesse, id_perfil):
        stmt = (
            select(VinculoPerfilInteresse).
            where(
                VinculoPerfilInteresse.id_perfil == id_perfil,
                VinculoPerfilInteresse.id_interesse == id_interesse
            )
        )

        # Executando a query
        query = await self.db_session.execute(stmt)
        return query.scalars().unique().first()

    async def insert_vinculo_perfil_interesse(self, id_interesse, id_perfil):
        stmt = (
            insert(VinculoPerfilInteresse).
            values(
                id_interesse=id_interesse,
                id_perfil=id_perfil
            )
        )

        # Executando a query
        await self.db_session.execute(stmt)

    async def delete_vinculo_perfil_interesse(self, id_interesse, id_perfil):
        stmt = (
            delete(VinculoPerfilInteresse).
            where(
                VinculoPerfilInteresse.id_perfil == id_perfil,
                VinculoPerfilInteresse.id_interesse == id_interesse
            )
        )

        # Executando a query
        await self.db_session.execute(stmt)

    async def insert_email_profile(self, perfil_email_dict):
        stmt = (
            insert(PerfilEmail).
            returning(literal_column('*')).
            values(**perfil_email_dict)
        )
        query = await self.db_session.execute(stmt)
        row_to_dict = dict(query.fetchone())
        return PerfilEmail(**row_to_dict)

    async def atualiza_email_profile(self, guid_perfil_email: str, perfil_email_update_dict: dict):
        stmt = (
            update(PerfilEmail).
            returning(literal_column('*')).
            where(PerfilEmail.guid == guid_perfil_email).
            values(**perfil_email_update_dict)
        )
        query = await self.db_session.execute(stmt)
        row_to_dict = dict(query.fetchone())
        return PerfilEmail(**row_to_dict)

    async def delete_email_profile(self, guid_perfil_email: str):
        stmt = (
            delete(PerfilEmail).
            where(PerfilEmail.guid == guid_perfil_email)
        )
        await self.db_session.execute(stmt)

    async def find_perfil_email_by_guid(self, perfil_email_guid: str):
        stmt = (
            select(PerfilEmail).
            where(
                PerfilEmail.guid == perfil_email_guid
            )
        )

        # Executando a query
        query = await self.db_session.execute(stmt)
        return query.scalars().unique().first()

    async def insert_phone_profile(self, perfil_phone_dict):
        stmt = (
            insert(PerfilPhone).
            returning(literal_column('*')).
            values(**perfil_phone_dict)
        )
        query = await self.db_session.execute(stmt)
        row_to_dict = dict(query.fetchone())
        return PerfilPhone(**row_to_dict)

    async def atualiza_phone_profile(self, guid_perfil_phone: str, perfil_phone_update_dict: dict):
        stmt = (
            update(PerfilPhone).
            returning(literal_column('*')).
            where(PerfilPhone.guid == guid_perfil_phone).
            values(**perfil_phone_update_dict)
        )
        query = await self.db_session.execute(stmt)
        row_to_dict = dict(query.fetchone())
        return PerfilPhone(**row_to_dict)

    async def delete_phone_profile(self, guid_perfil_phone: str):
        stmt = (
            delete(PerfilPhone).
            where(PerfilPhone.guid == guid_perfil_phone)
        )
        await self.db_session.execute(stmt)

    async def find_perfil_phone_by_guid(self, perfil_phone_guid: str):
        stmt = (
            select(PerfilPhone).
            outerjoin(
                TipoContato,
                TipoContato.id == PerfilPhone.id_tipo_contato
            ).
            options(
                selectinload(PerfilPhone.tipo_contato)
            ).
            where(
                PerfilPhone.guid == perfil_phone_guid
            )
        )

        # Executando a query
        query = await self.db_session.execute(stmt)
        return query.scalars().unique().first()

