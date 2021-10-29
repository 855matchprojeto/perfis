from server.schemas import usuario_schema
from fastapi import APIRouter
from server.dependencies.session import get_session
from server.dependencies.get_environment_cached import get_environment_cached
from server.configuration.db import AsyncSession
from fastapi import Depends, Security, Query
from server.controllers import endpoint_exception_handler
from typing import List, Optional
from server.dependencies.get_current_user import get_current_user
from server.schemas import error_schema
from server.configuration.environment import Environment
from server.schemas.interesse_schema import InteresseOutput
from server.services.interesse_service import InteresseService
from server.repository.interesse_repository import InteresseRepository


router = APIRouter()
interesse_router = dict(
    router=router,
    prefix="/interests",
    tags=["Interesses"],
)


@router.get(
    "",
    response_model=List[InteresseOutput],
    summary='Retorna todos os interesses cadastrados no sistema',
    response_description='Retorna todos os interesses cadastrados no sistema',
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
async def get_all_interests(
    _: usuario_schema.CurrentUserToken = Security(get_current_user, scopes=[]),
    session: AsyncSession = Depends(get_session),
    environment: Environment = Depends(get_environment_cached),
):

    """
        # Descrição

        Retorna todos os interesses cadastrados no sistema.

        # Erros

        Segue a lista de erros, por (**error_id**, **status_code**), que podem ocorrer nesse endpoint:

        - **(INVALID_OR_EXPIRED_TOKEN, 401)**: Token de acesso inválido ou expirado.
        - **(REQUEST_VALIDATION_ERROR, 422)**: Validação padrão da requisição. O detalhamento é um JSON,
        no formato de string, contendo os erros de validação encontrados.
        - **(INTERNAL_SERVER_ERROR, 500)**: Erro interno no sistema

    """

    interesse_service = InteresseService(
        interesse_repo=InteresseRepository(
            db_session=session,
            environment=environment
        ),
        environment=environment
    )

    return await interesse_service.get_all_interests()

