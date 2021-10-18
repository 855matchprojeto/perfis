import logging
import sys
from starlette_context import context
from server.schemas.usuario_schema import CurrentUserToken
from typing import List
from starlette.requests import HTTPConnection


class CurrentUserFilter(logging.Filter):
    def filter(self, record: logging.LogRecord):
        if context.exists():
            current_user: CurrentUserToken = context.data.get('current_user', None)
            record.username = current_user.username if current_user else ""
            record.user_email = current_user.email if current_user else ""
            record.user_guid = current_user.guid if current_user else ""
            return True
        return False


class RequestFilter(logging.Filter):
    def filter(self, record: logging.LogRecord):
        if context.exists():
            request_dict = context.data.get('request', None)
            request: HTTPConnection = request_dict['request'] if request_dict else None
            record.request_method = request.scope['method'] if request else None
            record.request_path = request.scope['path'] if request else None

            request_id = context.data.get('X-Request-ID', None)
            record.request_id = request_id
            return True
        return False


class Logger:

    @staticmethod
    def get_logger_by_name(logger_name: str):
        return logging.getLogger(logger_name)

    def __init__(self, logger_name: str, formatter: logging.Formatter, logger_filters: List[logging.Filter]):
        self.logger_name = logger_name
        self.formatter = formatter
        self.logger_filters = logger_filters
        self.logger = logging.getLogger(logger_name)
        for logger_filter in logger_filters:
            self.logger.addFilter(logger_filter)
        self.build_stdout_logger()
        self.logger.setLevel(logging.DEBUG)

    def build_stdout_logger(self):
        handler = logging.StreamHandler(stream=sys.stdout)
        handler.setFormatter(self.formatter)
        handler.setLevel(logging.DEBUG)
        self.logger.addHandler(handler)

    def get_logger(self):
        return logging.getLogger(self.logger_name)


MICROSERVICE_LOGGER_NAME = "AUTHENTICATOR_LOGGER"
MICROSERVICE_LOGGER_KWARGS = {
    "logger_name": MICROSERVICE_LOGGER_NAME,
    "formatter": logging.Formatter("{\n"
        f'\t"levelname": "%(levelname)s",\n'
        f'\t"asctime": "%(asctime)s",\n'
        f'\t"request_id": "%(request_id)s",\n'
        f'\t"request_method": "%(request_method)s",\n'                     
        f'\t"request_path": "%(request_path)s",\n'
        f'\t"funcName": "%(funcName)s",\n'
        f'\t"module": "%(module)s",\n'
        f'\t"message": "%(message)s",\n'
        f'\t"username": "%(username)s",\n'
        f'\t"user_email": "%(user_email)s",\n'
        f'\t"user_guid": "%(user_guid)s",\n'
        '}'
    ),
    "logger_filters": [
        RequestFilter(),
        CurrentUserFilter()
    ]
}


def get_main_logger():
    return Logger.get_logger_by_name(MICROSERVICE_LOGGER_NAME)

