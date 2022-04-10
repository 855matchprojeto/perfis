from fastapi import Depends
from server.configuration.custom_logging import get_main_logger
from server.dependencies.get_environment_cached import get_environment_cached
from server.configuration.environment import Environment
from server.services.file_uploader.s3_uploader.s3_uploader_service import S3FileUploaderService


MAIN_LOGGER = get_main_logger()


async def get_s3_file_uploader_service(
    environment: Environment = Depends(get_environment_cached)
) -> S3FileUploaderService:

    return S3FileUploaderService(environment)

