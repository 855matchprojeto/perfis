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
from server.repository.curso_repository import CursoRepository
from server.repository.interesse_repository import InteresseRepository
from server.schemas.perfil_schema import PaginatedPerfilOutput, PerfilOutput, PerfilPostInput, \
    PerfilUpdateInput, PerfilUpdateOutput
from fastapi import Request, status


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


@router.get(
    "/{guid_perfil}",
    response_model=PerfilOutput,
    summary='Retorna o perfil a partir de seu GUID',
    response_description='Retorna o perfil criado a partir do seu GUID',
    responses={
        401: {
            'model': error_schema.ErrorOutput401,
        },
        404: {
            'model': error_schema.ErrorOutput404,
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
async def get_profile_by_guid(
    guid_perfil: str,
    _: usuario_schema.CurrentUserToken = Security(get_current_user, scopes=[]),
    session: AsyncSession = Depends(get_session),
    environment: Environment = Depends(get_environment_cached),
):

    """
        # Descrição

        Retorna o perfil a partir do GUID no path.

        # Erros

        Segue a lista de erros, por (**error_id**, **status_code**), que podem ocorrer nesse endpoint:

        - **(INVALID_OR_EXPIRED_TOKEN, 401)**: Token de acesso inválido ou expirado.
        - **(PROFILE_NOT_FOUND, 404)**: Perfil não encontrado no sistema.
        - **(REQUEST_VALIDATION_ERROR, 422)**: Validação padrão da requisição. O detalhamento é um JSON,
        no formato de string, contendo os erros de validação encontrados.
        - **(INTERNAL_SERVER_ERROR, 500)**: Erro interno no sistema

    """

    perfil_service = PerfilService(
        perfil_repo=PerfilRepository(
            db_session=session,
            environment=environment
        ),
        environment=environment
    )

    return await perfil_service.get_profile_by_guid(guid_perfil)


@router.get(
    "/user/find-user-by-guid/{guid_usuario}",
    response_model=PerfilOutput,
    summary='Retorna o perfil a partir do GUID do usuário',
    response_description='Retorna o perfil a partir do GUID do usuário',
    responses={
        401: {
            'model': error_schema.ErrorOutput401,
        },
        404: {
            'model': error_schema.ErrorOutput404,
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
async def get_profile_by_guid_usuario(
    guid_usuario: str,
    _: usuario_schema.CurrentUserToken = Security(get_current_user, scopes=[]),
    session: AsyncSession = Depends(get_session),
    environment: Environment = Depends(get_environment_cached),
):

    """
        # Descrição

        Retorna o perfil a partir do GUID do usuário no path.

        # Erros

        Segue a lista de erros, por (**error_id**, **status_code**), que podem ocorrer nesse endpoint:

        - **(INVALID_OR_EXPIRED_TOKEN, 401)**: Token de acesso inválido ou expirado.
        - **(PROFILE_NOT_FOUND, 404)**: Perfil não encontrado no sistema.
        - **(REQUEST_VALIDATION_ERROR, 422)**: Validação padrão da requisição. O detalhamento é um JSON,
        no formato de string, contendo os erros de validação encontrados.
        - **(INTERNAL_SERVER_ERROR, 500)**: Erro interno no sistema

    """

    perfil_service = PerfilService(
        perfil_repo=PerfilRepository(
            db_session=session,
            environment=environment
        ),
        environment=environment
    )

    return await perfil_service.get_profile_by_guid_usuario(guid_usuario)


@router.get(
    "/user/me",
    response_model=PerfilOutput,
    summary='Busca o perfil do usuário atual',
    response_description='Retorna o perfil do usuário atual',
    responses={
        401: {
            'model': error_schema.ErrorOutput401,
        },
        404: {
            'model': error_schema.ErrorOutput404,
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
async def get_own_profile(
    current_user: usuario_schema.CurrentUserToken = Security(get_current_user, scopes=[]),
    session: AsyncSession = Depends(get_session),
    environment: Environment = Depends(get_environment_cached),
):

    """
        # Descrição

        Busca o perfil do usuário atual, além de todas as relações com as demais entidades
        vinculadas ao perfil

        # Erros

        Segue a lista de erros, por (**error_id**, **status_code**), que podem ocorrer nesse endpoint:

        - **(INVALID_OR_EXPIRED_TOKEN, 401)**: Token de acesso inválido ou expirado.
        - **(REQUEST_VALIDATION_ERROR, 422)**: Validação padrão da requisição. O detalhamento é um JSON,
        no formato de string, contendo os erros de validação encontrados.
        - **(INTERNAL_SERVER_ERROR, 500)**: Erro interno no sistema

    """

    perfil_service = PerfilService(
        perfil_repo=PerfilRepository(
            db_session=session,
            environment=environment
        ),
        environment=environment
    )

    guid_usuario = current_user.guid

    return await perfil_service.get_profile_by_guid_usuario(guid_usuario)


@router.post(
    "/user/me",
    response_model=PerfilOutput,
    summary='Cria um novo perfil para o usuário atual',
    response_description='Retorna o perfil criado para o usuário atual, incluindo o GUID do perfil na resposta',
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
async def post_own_profile(
    perfil_input: PerfilPostInput,
    current_user: usuario_schema.CurrentUserToken = Security(get_current_user, scopes=[]),
    session: AsyncSession = Depends(get_session),
    environment: Environment = Depends(get_environment_cached),
):

    """
        # Descrição

        Cria o perfil do usuário atual a partir dos campos definidos no corpo da requisição

        # Erros

        Segue a lista de erros, por (**error_id**, **status_code**), que podem ocorrer nesse endpoint:

        - **(INVALID_OR_EXPIRED_TOKEN, 401)**: Token de acesso inválido ou expirado.
        - **(REQUEST_VALIDATION_ERROR, 422)**: Validação padrão da requisição. O detalhamento é um JSON,
        no formato de string, contendo os erros de validação encontrados.
        - **(INTERNAL_SERVER_ERROR, 500)**: Erro interno no sistema

    """

    perfil_service = PerfilService(
        perfil_repo=PerfilRepository(
            db_session=session,
            environment=environment
        ),
        environment=environment
    )

    guid_usuario = current_user.guid

    return await perfil_service.create_profile_by_guid_usuario(guid_usuario, perfil_input)


@router.put(
    "/user/me",
    response_model=PerfilUpdateOutput,
    summary='Atualiza o perfil do usuário atual.',
    response_description='O perfil é atualizado e são retornadas as informações atualizadas. Note que algumas informações não são retornadas'
    ', como os vínculos com as demais entidades',
    responses={
        401: {
            'model': error_schema.ErrorOutput401,
        },
        404: {
            'model': error_schema.ErrorOutput404,
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
async def put_own_profile(
    perfil_input: PerfilUpdateInput,
    current_user: usuario_schema.CurrentUserToken = Security(get_current_user, scopes=[]),
    session: AsyncSession = Depends(get_session),
    environment: Environment = Depends(get_environment_cached),
):

    """
        # Descrição

        Atualiza o perfil do usuário atual a partir dos campos definidos no corpo da requisição.
        Note que a respostas é mais "enxuta" e não retorna os vínculos com as outras entidades.

        # Erros

        Segue a lista de erros, por (**error_id**, **status_code**), que podem ocorrer nesse endpoint:

        - **(INVALID_OR_EXPIRED_TOKEN, 401)**: Token de acesso inválido ou expirado.
        - **(PROFILE_NOT_FOUND, 404)**: Perfil não encontrado no sistema.
        - **(REQUEST_VALIDATION_ERROR, 422)**: Validação padrão da requisição. O detalhamento é um JSON,
        no formato de string, contendo os erros de validação encontrados.
        - **(INTERNAL_SERVER_ERROR, 500)**: Erro interno no sistema

    """

    perfil_service = PerfilService(
        perfil_repo=PerfilRepository(
            db_session=session,
            environment=environment
        ),
        environment=environment
    )

    guid_usuario = current_user.guid

    return await perfil_service.update_profile_by_guid_usuario(guid_usuario, perfil_input)


@router.delete(
    "/user/me",
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Deleta o perfil do usuário atual',
    responses={
        401: {
            'model': error_schema.ErrorOutput401,
        },
        404: {
            'model': error_schema.ErrorOutput404,
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
async def delete_profile(
    current_user: usuario_schema.CurrentUserToken = Security(get_current_user, scopes=[]),
    session: AsyncSession = Depends(get_session),
    environment: Environment = Depends(get_environment_cached),
):

    """
        # Descrição

        Atualiza o perfil do usuário a partir dos campos definidos no corpo da requisição.
        Note que a respostas é mais "enxuta" e não retorna os vínculos com as outras entidades.

        # Erros

        Segue a lista de erros, por (**error_id**, **status_code**), que podem ocorrer nesse endpoint:

        - **(INVALID_OR_EXPIRED_TOKEN, 401)**: Token de acesso inválido ou expirado.
        - **(PROFILE_NOT_FOUND, 404)**: Perfil não encontrado no sistema.
        - **(REQUEST_VALIDATION_ERROR, 422)**: Validação padrão da requisição. O detalhamento é um JSON,
        no formato de string, contendo os erros de validação encontrados.
        - **(INTERNAL_SERVER_ERROR, 500)**: Erro interno no sistema

    """

    perfil_service = PerfilService(
        perfil_repo=PerfilRepository(
            db_session=session,
            environment=environment
        ),
        environment=environment
    )

    guid_usuario = current_user.guid

    await perfil_service.delete_profile_by_guid_usuario(guid_usuario)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


"""
    VinculoPerfilCurso
"""


@router.post(
    "/user/me/link-course/{nome_referencia_curso}",
    tags=["VinculoCursoPerfil"],
    status_code=status.HTTP_201_CREATED,
    summary='Vincula um curso para o perfil do usuário atual',
    responses={
        401: {
            'model': error_schema.ErrorOutput401,
        },
        404: {
            'model': error_schema.ErrorOutput404,
        },
        409: {
            'model': error_schema.ErrorOutput409,
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
async def link_course_to_own_profile(
    nome_referencia_curso: str,
    current_user: usuario_schema.CurrentUserToken = Security(get_current_user, scopes=[]),
    session: AsyncSession = Depends(get_session),
    environment: Environment = Depends(get_environment_cached),
):

    """
        # Descrição

        Vincula um curso para o perfil do usuário atual.
        O curso é referenciado pelo campo nome_referencia

        # Erros

        Segue a lista de erros, por (**error_id**, **status_code**), que podem ocorrer nesse endpoint:

        - **(INVALID_OR_EXPIRED_TOKEN, 401)**: Token de acesso inválido ou expirado.
        - **(PROFILE_NOT_FOUND, 404)**: Perfil não encontrado no sistema.
        - **(COURSE_LINK_ALREADY_EXISTS, 409)**: Já existe um vínculo do curso com o perfil do usuário
        - **(REQUEST_VALIDATION_ERROR, 422)**: Validação padrão da requisição. O detalhamento é um JSON,
        no formato de string, contendo os erros de validação encontrados.
        - **(INTERNAL_SERVER_ERROR, 500)**: Erro interno no sistema

    """

    perfil_service = PerfilService(
        perfil_repo=PerfilRepository(
            db_session=session,
            environment=environment
        ),
        curso_repo=CursoRepository(
            db_session=session,
            environment=environment
        ),
        environment=environment
    )

    guid_usuario = current_user.guid

    await perfil_service.link_course_to_profile(guid_usuario, nome_referencia_curso)
    return Response(status_code=status.HTTP_201_CREATED)


@router.delete(
    "/user/me/link-course/{nome_referencia_curso}",
    tags=["VinculoCursoPerfil"],
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Deleta um vínculo de um curso com o perfil do usuário atual',
    responses={
        401: {
            'model': error_schema.ErrorOutput401,
        },
        404: {
            'model': error_schema.ErrorOutput404,
        },
        409: {
            'model': error_schema.ErrorOutput409,
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
async def delete_link_course_to_own_profile(
    nome_referencia_curso: str,
    current_user: usuario_schema.CurrentUserToken = Security(get_current_user, scopes=[]),
    session: AsyncSession = Depends(get_session),
    environment: Environment = Depends(get_environment_cached),
):

    """
        # Descrição

        Deleta um vincula do curso com o perfil do usuário atual.
        O curso é referenciado pelo campo nome_referencia

        # Erros

        Segue a lista de erros, por (**error_id**, **status_code**), que podem ocorrer nesse endpoint:

        - **(INVALID_OR_EXPIRED_TOKEN, 401)**: Token de acesso inválido ou expirado.
        - **(PROFILE_NOT_FOUND, 404)**: Perfil não encontrado no sistema.
        - **(COURSE_LINK_NOT_FOUND, 404)**: Não foi encontrado o vínculo do curso com o usuário
        - **(REQUEST_VALIDATION_ERROR, 422)**: Validação padrão da requisição. O detalhamento é um JSON,
        no formato de string, contendo os erros de validação encontrados.
        - **(INTERNAL_SERVER_ERROR, 500)**: Erro interno no sistema

    """

    perfil_service = PerfilService(
        perfil_repo=PerfilRepository(
            db_session=session,
            environment=environment
        ),
        curso_repo=CursoRepository(
            db_session=session,
            environment=environment
        ),
        environment=environment
    )

    guid_usuario = current_user.guid

    await perfil_service.delete_profile_course_link(guid_usuario, nome_referencia_curso)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


"""
    VinculoPerfilInteresse
"""


@router.post(
    "/user/me/link-interest/{nome_referencia_interesse}",
    tags=["VinculoInteressePerfil"],
    status_code=status.HTTP_201_CREATED,
    summary='Vincula um interesse para o perfil do usuário atual',
    responses={
        401: {
            'model': error_schema.ErrorOutput401,
        },
        404: {
            'model': error_schema.ErrorOutput404,
        },
        409: {
            'model': error_schema.ErrorOutput409,
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
async def link_interest_to_own_profile(
    nome_referencia_interesse: str,
    current_user: usuario_schema.CurrentUserToken = Security(get_current_user, scopes=[]),
    session: AsyncSession = Depends(get_session),
    environment: Environment = Depends(get_environment_cached),
):

    """
        # Descrição

        Vincula um interesse para o perfil do usuário atual.
        O interesse é referenciado pelo campo nome_referencia

        # Erros

        Segue a lista de erros, por (**error_id**, **status_code**), que podem ocorrer nesse endpoint:

        - **(INVALID_OR_EXPIRED_TOKEN, 401)**: Token de acesso inválido ou expirado.
        - **(PROFILE_NOT_FOUND, 404)**: Perfil não encontrado no sistema.
        - **(INTEREST_LINK_ALREADY_EXISTS, 409)**: Já existe um vínculo do interesse com o perfil do usuário
        - **(REQUEST_VALIDATION_ERROR, 422)**: Validação padrão da requisição. O detalhamento é um JSON,
        no formato de string, contendo os erros de validação encontrados.
        - **(INTERNAL_SERVER_ERROR, 500)**: Erro interno no sistema

    """

    perfil_service = PerfilService(
        perfil_repo=PerfilRepository(
            db_session=session,
            environment=environment
        ),
        interesse_repo=InteresseRepository(
            db_session=session,
            environment=environment
        ),
        environment=environment
    )

    guid_usuario = current_user.guid

    await perfil_service.link_interest_to_profile(guid_usuario, nome_referencia_interesse)
    return Response(status_code=status.HTTP_201_CREATED)


@router.delete(
    "/user/me/link-interest/{nome_referencia_interesse}",
    tags=["VinculoInteressePerfil"],
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Deleta um vínculo de um interesse com o perfil do usuário atual',
    responses={
        401: {
            'model': error_schema.ErrorOutput401,
        },
        404: {
            'model': error_schema.ErrorOutput404,
        },
        409: {
            'model': error_schema.ErrorOutput409,
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
async def delete_link_course_to_own_profile(
    nome_referencia_interesse: str,
    current_user: usuario_schema.CurrentUserToken = Security(get_current_user, scopes=[]),
    session: AsyncSession = Depends(get_session),
    environment: Environment = Depends(get_environment_cached),
):

    """
        # Descrição

        Deleta um vincula do interesse com o perfil do usuário atual.
        O interesse é referenciado pelo campo nome_referencia

        # Erros

        Segue a lista de erros, por (**error_id**, **status_code**), que podem ocorrer nesse endpoint:

        - **(INVALID_OR_EXPIRED_TOKEN, 401)**: Token de acesso inválido ou expirado.
        - **(PROFILE_NOT_FOUND, 404)**: Perfil não encontrado no sistema.
        - **(INTEREST_LINK_NOT_FOUND, 404)**: Não foi encontrado o vínculo do interesse com o usuário
        - **(REQUEST_VALIDATION_ERROR, 422)**: Validação padrão da requisição. O detalhamento é um JSON,
        no formato de string, contendo os erros de validação encontrados.
        - **(INTERNAL_SERVER_ERROR, 500)**: Erro interno no sistema

    """

    perfil_service = PerfilService(
        perfil_repo=PerfilRepository(
            db_session=session,
            environment=environment
        ),
        interesse_repo=InteresseRepository(
            db_session=session,
            environment=environment
        ),
        environment=environment
    )

    guid_usuario = current_user.guid

    await perfil_service.delete_profile_interest_link(guid_usuario, nome_referencia_interesse)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

