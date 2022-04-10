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
from server.schemas.perfil_schema import (
    PaginatedPerfilOutput, PerfilOutput, PerfilPostInput, PerfilPatchInput
)
from fastapi import Request, status
from uuid import UUID as GUID
from server.models.perfil_email_model import PerfilEmail
from server.schemas.perfil_email_schema import PerfilEmailPatchInput, PerfilEmailOutput, PerfilEmailPostInput
from server.schemas.perfil_phone_schema import PerfilPhoneOutput, PerfilPhonePatchInput, PerfilPhonePostInput
from server.repository.tipo_contato_repository import TipoContatoRepository
from server.services.file_uploader.uploader import FileUploaderService
from server.dependencies.get_s3_file_uploader_service import get_s3_file_uploader_service
from server.repository.arquivo_repository import ArquivoRepository
from server.services.arquivo_service import ArquivoService


async def all_profiles_query_params(
    interests_in: Optional[List[int]] = perfil_schema.InterestQuery,
    courses_in: Optional[List[int]] = perfil_schema.CourseQuery,
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
    guid_perfil: GUID,
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

    return await perfil_service.get_profile_by_guid(str(guid_perfil))


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
    guid_usuario: GUID,
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

    return await perfil_service.get_profile_by_guid_usuario(str(guid_usuario))


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
async def post_own_profile(
    perfil_input: PerfilPostInput,
    current_user: usuario_schema.CurrentUserToken = Security(get_current_user, scopes=[]),
    session: AsyncSession = Depends(get_session),
    environment: Environment = Depends(get_environment_cached),
    file_uploader_service: FileUploaderService = Depends(get_s3_file_uploader_service)
):

    """
        # Descrição

        Cria o perfil do usuário atual a partir dos campos definidos no corpo da requisição

        É possível fazer upload de imagem de perfil nesse endpoint, a partir do campo
        'imagem_perfil'

        # Erros

        Segue a lista de erros, por (**error_id**, **status_code**), que podem ocorrer nesse endpoint:

        - **(INVALID_OR_EXPIRED_TOKEN, 401)**: Token de acesso inválido ou expirado.
        - **(PROFILE_ALREADY_EXISTS, 409)**: Já existe um perfil para o usuário atual.
        - **(REQUEST_VALIDATION_ERROR, 422)**: Validação padrão da requisição. O detalhamento é um JSON,
        no formato de string, contendo os erros de validação encontrados.
        - **(INTERNAL_SERVER_ERROR, 500)**: Erro interno no sistema

    """

    arquivo_service = ArquivoService(
        arquivo_repo=ArquivoRepository(session, environment),
        environment=environment,
        file_uploader_service=file_uploader_service
    )

    perfil_service = PerfilService(
        perfil_repo=PerfilRepository(
            db_session=session,
            environment=environment
        ),
        environment=environment,
        arquivo_service=arquivo_service
    )

    return await perfil_service.create_profile_by_guid_usuario(current_user, perfil_input)


@router.patch(
    "/user/me",
    response_model=PerfilOutput,
    summary='Atualiza o perfil do usuário atual.',
    response_description='O perfil é atualizado e são retornadas as informações atualizadas',
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
async def patch_own_profile(
    perfil_input: PerfilPatchInput,
    current_user: usuario_schema.CurrentUserToken = Security(get_current_user, scopes=[]),
    session: AsyncSession = Depends(get_session),
    environment: Environment = Depends(get_environment_cached),
    file_uploader_service: FileUploaderService = Depends(get_s3_file_uploader_service)
):

    """
        # Descrição

        Atualiza o perfil do usuário atual a partir dos campos definidos no corpo da requisição.

        Apenas os campos enviados no corpo da requisição são atualizados.

        É possível fazer upload de imagem de perfil nesse endpoint, a partir do campo
        'imagem_perfil'

        # Erros

        Segue a lista de erros, por (**error_id**, **status_code**), que podem ocorrer nesse endpoint:

        - **(INVALID_OR_EXPIRED_TOKEN, 401)**: Token de acesso inválido ou expirado.
        - **(PROFILE_NOT_FOUND, 404)**: Perfil não encontrado no sistema.
        - **(REQUEST_VALIDATION_ERROR, 422)**: Validação padrão da requisição. O detalhamento é um JSON,
        no formato de string, contendo os erros de validação encontrados.
        - **(INTERNAL_SERVER_ERROR, 500)**: Erro interno no sistema

    """

    arquivo_service = ArquivoService(
        arquivo_repo=ArquivoRepository(session, environment),
        environment=environment,
        file_uploader_service=file_uploader_service
    )

    perfil_service = PerfilService(
        perfil_repo=PerfilRepository(
            db_session=session,
            environment=environment
        ),
        environment=environment,
        arquivo_service=arquivo_service
    )

    return await perfil_service.patch_profile_by_guid_usuario(current_user, perfil_input)


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

        Deleta o perfil do usuario

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
    "/user/me/link-course/{id_curso}",
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
    id_curso: int,
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

    await perfil_service.link_course_to_profile(guid_usuario, id_curso)
    return Response(status_code=status.HTTP_201_CREATED)


@router.delete(
    "/user/me/link-course/{id_curso}",
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
    id_curso: int,
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

    await perfil_service.delete_profile_course_link(guid_usuario, id_curso)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


"""
    VinculoPerfilInteresse
"""


@router.post(
    "/user/me/link-interest/{id_interesse}",
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
    id_interesse: int,
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

    await perfil_service.link_interest_to_profile(guid_usuario, id_interesse)
    return Response(status_code=status.HTTP_201_CREATED)


@router.delete(
    "/user/me/link-interest/{id_interesse}",
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
    id_interesse: int,
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

    await perfil_service.delete_profile_interest_link(guid_usuario, id_interesse)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


"""
    PerfilEmail
"""


@router.post(
    "/user/me/perfil-email",
    tags=["PerfilEmail"],
    response_model=PerfilEmailOutput,
    summary='Insere uma entidade de e-mail para o perfil do usuário atual',
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
async def insert_email_to_own_profile(
    perfil_email_input: PerfilEmailPostInput,
    current_user: usuario_schema.CurrentUserToken = Security(get_current_user, scopes=[]),
    session: AsyncSession = Depends(get_session),
    environment: Environment = Depends(get_environment_cached),
):

    """
        # Descrição

        Insere uma entidade de email para o perfil do usuário atual.

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

    return await perfil_service.insert_email_profile_by_guid_usuario(
        guid_usuario,
        perfil_email_input
    )


@router.patch(
    "/user/me/perfil-email/{guid_perfil_email}",
    tags=["PerfilEmail"],
    response_model=PerfilEmailOutput,
    summary='Atualiza uma entidade de email para o perfil do usuário atual',
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
async def patch_email_to_own_profile(
    guid_perfil_email: GUID,
    perfil_email_input: PerfilEmailPatchInput,
    _: usuario_schema.CurrentUserToken = Security(get_current_user, scopes=[]),
    session: AsyncSession = Depends(get_session),
    environment: Environment = Depends(get_environment_cached),
):

    """
        # Descrição

        Atualiza uma entidade de email para o perfil do usuário atual.
        Apenas os campos enviados no corpo da requisição são atualizados.

        # Erros

        Segue a lista de erros, por (**error_id**, **status_code**), que podem ocorrer nesse endpoint:

        - **(INVALID_OR_EXPIRED_TOKEN, 401)**: Token de acesso inválido ou expirado.
        - **(PROFILE_EMAIL_NOT_FOUND, 404)**: Entidade de email vinculada ao perfil não encontrado no sistema.
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

    return await perfil_service.patch_email_profile_by_guid(
        str(guid_perfil_email),
        perfil_email_input
    )


@router.delete(
    "/user/me/perfil-email/{guid_perfil_email}",
    tags=["PerfilEmail"],
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Deleta uma entidade de email do perfil do usuário atual',
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
async def delete_email_to_own_profile(
    guid_perfil_email: GUID,
    _: usuario_schema.CurrentUserToken = Security(get_current_user, scopes=[]),
    session: AsyncSession = Depends(get_session),
    environment: Environment = Depends(get_environment_cached),
):

    """
        # Descrição

        Deleta uma entidade de email do perfil do usuário atual.

        # Erros

        Segue a lista de erros, por (**error_id**, **status_code**), que podem ocorrer nesse endpoint:

        - **(INVALID_OR_EXPIRED_TOKEN, 401)**: Token de acesso inválido ou expirado.
        - **(PROFILE_EMAIL_NOT_FOUND, 404)**: Entidade de email vinculada ao perfil não encontrado no sistema.
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

    await perfil_service.delete_email_profile_by_guid(
        str(guid_perfil_email)
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


"""
    PerfilPhone
"""


@router.post(
    "/user/me/perfil-phone",
    tags=["PerfilPhone"],
    response_model=PerfilPhoneOutput,
    summary='Insere uma entidade de contato (Phone) para o perfil do usuário atual',
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
async def insert_phone_to_own_profile(
    perfil_phone_input: PerfilPhonePostInput,
    current_user: usuario_schema.CurrentUserToken = Security(get_current_user, scopes=[]),
    session: AsyncSession = Depends(get_session),
    environment: Environment = Depends(get_environment_cached),
):

    """
        # Descrição

        Insere uma entidade de phone para o perfil do usuário atual.

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
        tipo_contato_repo=TipoContatoRepository(
            db_session=session,
            environment=environment
        ),
        environment=environment
    )

    guid_usuario = current_user.guid

    return await perfil_service.insert_phone_profile_by_guid_usuario(
        guid_usuario,
        perfil_phone_input
    )


@router.patch(
    "/user/me/perfil-phone/{guid_perfil_phone}",
    tags=["PerfilPhone"],
    response_model=PerfilPhoneOutput,
    summary='Atualiza uma entidade de contato (Phone) para o perfil do usuário atual',
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
async def update_phone_own_profile(
    guid_perfil_phone: GUID,
    perfil_email_input: PerfilPhonePatchInput,
    _: usuario_schema.CurrentUserToken = Security(get_current_user, scopes=[]),
    session: AsyncSession = Depends(get_session),
    environment: Environment = Depends(get_environment_cached),
):

    """
        # Descrição

        Atualiza uma entidade de email para o perfil do usuário atual.
        Apenas os campos enviados no corpo da requisição são atualizados.

        # Erros

        Segue a lista de erros, por (**error_id**, **status_code**), que podem ocorrer nesse endpoint:

        - **(INVALID_OR_EXPIRED_TOKEN, 401)**: Token de acesso inválido ou expirado.
        - **(PROFILE_PHONE_NOT_FOUND, 404)**: Entidade de contato (Phone) vinculada ao perfil não encontrado no sistema.
        - **(REQUEST_VALIDATION_ERROR, 422)**: Validação padrão da requisição. O detalhamento é um JSON,
        no formato de string, contendo os erros de validação encontrados.
        - **(INTERNAL_SERVER_ERROR, 500)**: Erro interno no sistema

    """

    perfil_service = PerfilService(
        perfil_repo=PerfilRepository(
            db_session=session,
            environment=environment
        ),
        tipo_contato_repo=TipoContatoRepository(
            db_session=session,
            environment=environment
        ),
        environment=environment
    )

    return await perfil_service.patch_phone_profile_by_guid(
        str(guid_perfil_phone),
        perfil_email_input
    )


@router.delete(
    "/user/me/perfil-phone/{guid_perfil_phone}",
    tags=["PerfilPhone"],
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Deleta uma entidade de contato (Phone) do perfil do usuário atual',
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
async def delete_phone_own_profile(
    guid_perfil_phone: GUID,
    _: usuario_schema.CurrentUserToken = Security(get_current_user, scopes=[]),
    session: AsyncSession = Depends(get_session),
    environment: Environment = Depends(get_environment_cached),
):

    """
        # Descrição

        Deleta uma entidade de contato (Phone) do perfil do usuário atual.

        # Erros

        Segue a lista de erros, por (**error_id**, **status_code**), que podem ocorrer nesse endpoint:

        - **(INVALID_OR_EXPIRED_TOKEN, 401)**: Token de acesso inválido ou expirado.
        - **(PROFILE_PHONE_NOT_FOUND, 404)**: Entidade de contato (Phone) vinculada ao perfil não encontrado no sistema.
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

    await perfil_service.delete_phone_profile_by_guid(
        str(guid_perfil_phone)
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)

