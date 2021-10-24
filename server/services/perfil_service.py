from server.configuration.db import AsyncSession
import re
from server.configuration import exceptions
from sqlalchemy import or_, and_
from passlib.context import CryptContext
from jose import JWTError, jwt
from server.schemas.token_shema import DecodedMailToken
from datetime import timedelta
from datetime import datetime
from typing import List, Optional
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Request
from pydantic import ValidationError, EmailStr
from server.templates import jinja2_templates
from server.configuration.environment import Environment
from server.schemas.usuario_schema import CurrentUserOutput
from functools import lru_cache
from server.services import insert_filter, get_filters_base
from server.repository.perfil_repository import PerfilRepository
from server.repository.interesse_repository import InteresseRepository
from server.repository.curso_repository import CursoRepository
from server.schemas.cursor_schema import Cursor
from server.models.perfil_model import Perfil
from server import utils


class PerfilService:

    @staticmethod
    def get_filter_factory():
        return {
            "interests_in": InteresseRepository.get_interests_in_filter,
            "courses_in": CursoRepository.get_courses_in_filter,
            "display_name_ilike": PerfilRepository.get_name_ilike_filter
        }

    @staticmethod
    def get_filters_by_params(params_dict: dict):
        filters = []
        filter_factory = PerfilService.get_filter_factory()
        for key in params_dict:
            param = params_dict[key]
            if param:
                filters.extend(filter_factory[key](param))
        return filters

    @staticmethod
    def get_previous_url(request: Request):
        return str(request.url)

    @staticmethod
    def get_next_url(request: Request, path: str, next_encoded_cursor: str):
        if not next_encoded_cursor:
            return None

        query_params_dict = dict(request.query_params)
        query_string_builder = '?'

        for query_param_key in [key for key in query_params_dict.keys() if key != 'cursor']:
            query_param_value = query_params_dict[query_param_key]
            query_string_builder += f'{query_param_key}={query_param_value}&'

        query_string_builder += f'cursor={next_encoded_cursor}'

        return f"{request.base_url}{path}{query_string_builder}"

    @staticmethod
    def handle_profile_body(perfil: Perfil):
        perfil.interesses = [
            x.interesse for x in perfil.vinculos_perfil_interesse
        ]
        perfil.cursos = [
            x.curso for x in perfil.vinculos_perfil_curso
        ]
        return perfil

    @staticmethod
    def handle_profile_body_list(perfil_list: List[Perfil]):
        for perfil in perfil_list:
            PerfilService.handle_profile_body(perfil)
        return perfil_list

    @staticmethod
    def handle_profile_pagination(
        paginated_profile_dict: dict, previous_encoded_cursor: str, request: Request
    ):
        next_encoded_cursor = paginated_profile_dict['next_cursor']
        paginated_profile_dict['items'] = PerfilService.handle_profile_body_list(paginated_profile_dict['items'])
        paginated_profile_dict['previous_cursor'] = previous_encoded_cursor
        paginated_profile_dict['previous_url'] = PerfilService.get_previous_url(request)
        paginated_profile_dict['next_url'] = PerfilService.get_next_url(request, request.url.path, next_encoded_cursor)
        return paginated_profile_dict

    def __init__(self, perfil_repo: Optional[PerfilRepository] = None, environment: Optional[Environment] = None):
        self.perfil_repo = perfil_repo
        self.environment = environment

    def decode_cursor_info(self, encoded_cursor: str):
        decoded_cursor_dict = jwt.decode(
            encoded_cursor,
            self.environment.CURSOR_TOKEN_SECRET_KEY,
            algorithms=[self.environment.CURSOR_TOKEN_ALGORITHM]
        )
        return Cursor(**decoded_cursor_dict)

    async def get_all_profiles_paginated(
        self, filter_params_dict: dict,
        request: Request, limit: int, cursor: str
    ):
        filters = PerfilService.get_filters_by_params(filter_params_dict)
        decoded_cursor = self.decode_cursor_info(cursor) if cursor else None

        paginated_profile_dict = await self.perfil_repo.\
            find_profiles_by_filters_paginated(limit, decoded_cursor, filters)

        paginated_profile_dict = PerfilService.handle_profile_pagination(
            paginated_profile_dict, cursor, request
        )

        return paginated_profile_dict

