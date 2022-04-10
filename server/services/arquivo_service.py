from typing import Optional
from server.configuration.environment import Environment
from server.repository.arquivo_repository import ArquivoRepository
from server.services.file_uploader.uploader import FileUploaderService, FileUploaderInput
from server.schemas.usuario_schema import CurrentUserToken
from server import utils
from server.schemas.arquivo_schema import ArquivoInput
import uuid
from server.models.arquivo_model import Arquivo


class ArquivoService:

    def __init__(
        self, file_uploader_service: FileUploaderService = None, arquivo_repo: Optional[ArquivoRepository] = None,
        environment: Optional[Environment] = None,
    ):
        self.file_uploader_service = file_uploader_service

        self.environment = environment

        self.arquivo_repo = arquivo_repo

    async def upload_arquivo(
        self, file_input: ArquivoInput  , current_user: CurrentUserToken
    ) -> Arquivo:
        """
        Faz o upload do arquivo e o armazena na tabela de 'Arquivo'
        """

        uploaded_file_output = self.file_uploader_service.upload(
            FileUploaderInput(
                target=self.environment.AWS_S3_BUCKET,
                region=self.environment.AWS_REGION_NAME,
                key=f'u/{str(current_user.guid)}/profile/{str(uuid.uuid4())}/{file_input.file_name}',
                type=file_input.file_type,
                content=utils.decode_b64_str(file_input.b64_content)
            )
        )

        return await self.arquivo_repo.insere_arquivo(
            {
                'url': uploaded_file_output.url,
                'file_type': file_input.file_type,
                'file_name': file_input.file_name
            }
        )

