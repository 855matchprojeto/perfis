import boto3
from server.configuration.environment import Environment
from server.schemas.arquivo_schema import FileUploaderInput


class FIleUploaderClient:

    def __init__(self, _environment: Environment = Environment):
        self._s3_client = boto3.client(
            "s3",
            aws_access_key_id=_environment.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=_environment.AWS_SECRET_KEY,
            region_name=_environment.AWS_REGION_NAME,
        )

    def upload(
        self, file_uploader_input: FileUploaderInput
    ):
        return self._s3_client.put_object(
            Bucket=file_uploader_input.target,
            Key=file_uploader_input.key,
            ContentType=file_uploader_input.type,
            Body=file_uploader_input.content,
            ACL=file_uploader_input.acl or 'public-read'
        )

