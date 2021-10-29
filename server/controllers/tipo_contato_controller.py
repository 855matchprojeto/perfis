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
from server.schemas.tipo_contato_schema import TipoContatoOutput
from server.services.tipo_contato_service import TipoContatoService
from server.repository.tipo_contato_repository import TipoContatoRepository


router = APIRouter()
tipo_contato_router = dict(
    router=router,
    prefix="/contacting-types",
    tags=["Tipos de Contato"],
)


@router.get(
    "",
    response_model=List[TipoContatoOutput],
    summary='Retorna todos os tipos de contato cadastrados no sistema',
    response_description='Retorna todos os tipos de contato cadastrados no sistema',
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
async def get_all_contacting_types(
    _: usuario_schema.CurrentUserToken = Security(get_current_user, scopes=[]),
    session: AsyncSession = Depends(get_session),
    environment: Environment = Depends(get_environment_cached),
):

    """
        # Descrição

        Retorna todos os tipos de contrato cadastrados no sistema.

        # Erros

        Segue a lista de erros, por (**error_id**, **status_code**), que podem ocorrer nesse endpoint:

        - **(INVALID_OR_EXPIRED_TOKEN, 401)**: Token de acesso inválido ou expirado.
        - **(REQUEST_VALIDATION_ERROR, 422)**: Validação padrão da requisição. O detalhamento é um JSON,
        no formato de string, contendo os erros de validação encontrados.
        - **(INTERNAL_SERVER_ERROR, 500)**: Erro interno no sistema

    """

    tipo_contato_service = TipoContatoService(
        tipo_contato_repo=TipoContatoRepository(
            db_session=session,
            environment=environment
        ),
        environment=environment
    )

    return await tipo_contato_service.get_all_tipos_contato()

