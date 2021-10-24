from server.schemas import usuario_schema, token_shema
from fastapi import APIRouter, Request, Response
from server.services.usuario_service import UsuarioService
from server.dependencies.session import get_session
from server.dependencies.get_environment_cached import get_environment_cached
from server.configuration.db import AsyncSession
from fastapi import Depends, Security, Query
from server.controllers import endpoint_exception_handler
from fastapi.security import OAuth2PasswordRequestForm
from typing import List, Optional
from server.dependencies.get_current_user import get_current_user
from server.schemas import error_schema
from server.schemas import perfil_schema
from server.controllers import pagination_parameters
from server.services.perfil_service import PerfilService
from server.configuration.environment import Environment
from server.repository.perfil_repository import PerfilRepository
from server.schemas.perfil_schema import PaginatedPerfilOutput
from fastapi import Request


async def all_profiles_query_params(
    interests_in: Optional[List[str]] = perfil_schema.InterestQuery,
    courses_in: Optional[List[str]] = perfil_schema.CourseQuery,
    display_name_ilike: Optional[str] = perfil_schema.DisplayNameIlikeQuery
):
    return {
        "interests_in": interests_in,
        "courses_in": courses_in,
        "display_name_ilike": display_name_ilike
    }


router = APIRouter()
perfil_router = dict(
    router=router,
    prefix="/profiles",
    tags=["Perfis"],
)


@router.get(
    "",
    response_model=PaginatedPerfilOutput,
    summary='Retorna todos os perfis a partir de filtros contidos na query string',
    response_description='Retorna todos os perfis a partir de filtros contidos na query string',
    responses={
        401: {
            'model': error_schema.ErrorOutput401,
        },
        422: {
            'model': error_schema.ErrorOutput422,
        },
        500: {
            'model': error_schema.ErrorOutput500
        }
    }
)
@endpoint_exception_handler
async def get_all_profiles(
    request: Request,
    _: usuario_schema.CurrentUserToken = Security(get_current_user, scopes=[]),
    profiles_query_params: dict = Depends(all_profiles_query_params),
    pagination_params: dict = Depends(pagination_parameters),
    session: AsyncSession = Depends(get_session),
    environment: Environment = Depends(get_environment_cached),
):

    """
        # Descrição

        Retorna todos os perfis encontrados a partir dos filtros definidos na query string.

        Note que há uma paginação nesse endpoint. O tamanho de cada página é definido pelo
        parâmetro 'page_size'. Caso existam mais resultados disponíveis, é enviado um valor
        não-nulo no campo 'next_cursor' na resposta da requisição. Esse valor deverá ser
        preenchido na query string na próxima requisição. Para facilitar, o formato da nova
        URL de busca também é preenchida na resposta, no campo 'next_url'.

        # Erros

        Segue a lista de erros, por (**error_id**, **status_code**), que podem ocorrer nesse endpoint:

        - **(INVALID_OR_EXPIRED_TOKEN, 401)**: Token de acesso inválido ou expirado.
        - **(REQUEST_VALIDATION_ERROR, 422)**: Validação padrão da requisição. O detalhamento é um JSON,
        no formato de string, contendo os erros de validação encontrados.
        - **(INTERNAL_SERVER_ERROR, 500)**: Erro interno no sistema

    """

    filter_params_dict = profiles_query_params
    limit = pagination_params['limit']
    offset = pagination_params['cursor']

    perfil_service = PerfilService(
        perfil_repo=PerfilRepository(
            db_session=session,
            environment=environment
        ),
        environment=environment
    )

    return await perfil_service.get_all_profiles_paginated(
        filter_params_dict, request, limit, offset
    )

