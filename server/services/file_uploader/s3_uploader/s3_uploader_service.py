from server.services.file_uploader.uploader import FileUploaderService
from server.services.file_uploader.s3_uploader.client import FIleUploaderClient
from server.configuration.environment import Environment
from server.schemas.arquivo_schema import FileUploaderOutput, FileUploaderInput


class S3FileUploaderService(FileUploaderService):

    def __init__(self, _environment: Environment = Environment, _client: FIleUploaderClient = None):
        self._client = _client if _client else FIleUploaderClient(_environment)

    def upload(
        self, file_input: FileUploaderInput
    ) -> FileUploaderOutput:
        uploaded_file_data = self._client.upload(file_input)

        url = f'https://{file_input.target}.s3.{file_input.region}.amazonaws.com/{file_input.key}'

        return FileUploaderOutput(
            url=url, additional_data=uploaded_file_data
        )

