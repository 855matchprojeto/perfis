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
from server.services.arquivo_service import ArquivoService
from server.services.file_uploader.uploader import FileUploaderService
from server.dependencies.get_s3_file_uploader_service import get_s3_file_uploader_service
from server.schemas.arquivo_schema import ArquivoInput, ArquivoOutput
from server.repository.arquivo_repository import ArquivoRepository


router = APIRouter()
arquivo_router = dict(
    router=router,
    prefix="/files",
    tags=["Arquivos"],
)


@router.post(
    "/upload",
    response_model=ArquivoOutput,
    summary='Retorna o arquivo criado no banco de dados junto com a URL do arquivo',
    response_description='Retorna o arquivo criado no banco de dados junto com a URL do arquivo',
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
async def upload_file(
    file_input: ArquivoInput,
    current_user: usuario_schema.CurrentUserToken = Security(get_current_user, scopes=[]),
    session: AsyncSession = Depends(get_session),
    environment: Environment = Depends(get_environment_cached),
    file_uploader_service: FileUploaderService = Depends(get_s3_file_uploader_service)
):

    """
        # Descrição

        Faz o upload de um arquivo codificado em BASE 64. É necessária enviar informaçoes como:

        - Nome do arquivo com extensão
        - Extensão do arquivo
        - Conteúdo codificado em BASE 64

        # Erros

        Segue a lista de erros, por (**error_id**, **status_code**), que podem ocorrer nesse endpoint:

        - **(INVALID_OR_EXPIRED_TOKEN, 401)**: Token de acesso inválido ou expirado.
        - **(REQUEST_VALIDATION_ERROR, 422)**: Validação padrão da requisição. O detalhamento é um JSON,
        no formato de string, contendo os erros de validação encontrados.
        - **(INTERNAL_SERVER_ERROR, 500)**: Erro interno no sistema
    """

    arquivo_service = ArquivoService(
        arquivo_repo=ArquivoRepository(session, environment),
        environment=environment,
        file_uploader_service=file_uploader_service
    )

    return await arquivo_service.upload_arquivo(file_input, current_user)
