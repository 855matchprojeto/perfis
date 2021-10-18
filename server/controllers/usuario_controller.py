from server.schemas import usuario_schema, token_shema
from fastapi import APIRouter, Request, Response
from server.services.usuario_service import UsuarioService
from server.dependencies.session import get_session
from server.dependencies.get_environment_cached import get_environment_cached
from server.configuration.db import AsyncSession
from fastapi import Depends, Security
from server.controllers import endpoint_exception_handler
from fastapi.security import OAuth2PasswordRequestForm
from typing import List
from server.dependencies.get_current_user import get_current_user
from server.constants.permission import RoleBasedPermission
from server.configuration.environment import Environment
from server.schemas import error_schema


router = APIRouter()
usuario_router = dict(
    router=router,
    prefix="/users",
    tags=["Usuários"],
)


@router.get(
    "/me",
    response_model=usuario_schema.CurrentUserOutput,
    summary='Retorna as informações contidas no token do usuário',
    response_description='Informações contidas no token do usuário',
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
async def get_current_user(
    current_user: usuario_schema.CurrentUserToken = Security(get_current_user, scopes=[]),
):

    """
        # Descrição

        Retorna as informações do usuário atual vinculadas ao token.

        # Erros

        Segue a lista de erros, por (**error_id**, **status_code**), que podem ocorrer nesse endpoint:

        - **(INVALID_OR_EXPIRED_TOKEN, 401)**: Token de acesso inválido ou expirado.
        - **(REQUEST_VALIDATION_ERROR, 422)**: Validação padrão da requisição. O detalhamento é um JSON,
        no formato de string, contendo os erros de validação encontrados.
        - **(INTERNAL_SERVER_ERROR, 500)**: Erro interno no sistema

    """

    return UsuarioService.current_user_output(current_user)

