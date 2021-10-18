"""
    Módulo responsável por armazenar a primeira camada de acesso à aplicação

    Nos controllers são definidas as rotas e endpoints, além das especificações
    dos mesmos
"""

from server.configuration.exceptions import ApiBaseException
from server.configuration.db import AsyncSession
from server.configuration.custom_logging import get_main_logger
from functools import wraps


MAIN_LOGGER = get_main_logger()


def endpoint_exception_handler(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        MAIN_LOGGER.info("Início do endpoint")
        session: AsyncSession = kwargs.get('session', None)
        try:
            result = await func(*args, **kwargs)
            MAIN_LOGGER.info("Fim da rotina do endpoint. Commit da sessão do banco de dados acionado")
            if session:
                await session.commit()
            return result
        except ApiBaseException as ex:
            MAIN_LOGGER.warning(
                "Ocorreu um problema no endpoint. O problema foi detectado, mas não tratado. " 
                "Rollback da sessão atual do banco de dados acionado",
                exc_info=True
            )
            if session:
                await session.rollback()
            raise ex
        except Exception as ex:
            MAIN_LOGGER.error(
                "Ocorreu um erro inesperado no endpoint. "
                "Rollback da sessão atual do banco de dados acionado",
                exc_info=True
            )
            if session:
                await session.rollback()
            raise ex
        finally:
            MAIN_LOGGER.info(
                "Fim do endpoint e da sessão do banco de dados"
            )
            if session:
                await session.close()
    return wrapper

