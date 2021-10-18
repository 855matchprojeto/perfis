import json
from fastapi import HTTPException, status
from starlette.requests import Request
from starlette.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


class ApiBaseException(HTTPException):

    def __init__(
        self,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_id='INTERNAL_SERVER_ERROR',
        message='Ocorreu um erro interno no servidor',
        detail=''
    ) -> None:
        self.status_code = status_code
        self.error_id = error_id
        self.message = message
        self.detail = detail


class RequestValidationException(ApiBaseException):
    def __init__(
            self,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_id='REQUEST_VALIDATION_ERROR',
            message='Ocorreu um problema ao validar a requisição',
            detail=''
    ) -> None:
        super().__init__(status_code, error_id, message, detail)


class UnprocessableEntityException(ApiBaseException):
    def __init__(
        self,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        error_id='UNPROCESSABLE_ENTITY',
        message='Ocorreu um problema ao processar a entidade',
        detail=''
    ) -> None:
        super().__init__(status_code, error_id, message, detail)


class EmailAlreadyConfirmedException(ApiBaseException):
    def __init__(
        self,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        error_id='EMAIL_ALREADY_CONFIRMED',
        message='Email já verificado pelo sistema',
        detail=''
    ) -> None:
        super().__init__(status_code, error_id, message, detail)


class InvalidEmailException(ApiBaseException):
    def __init__(
        self,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        error_id='INVALID_EMAIL',
        message='Email inválido',
        detail=''
    ) -> None:
        super().__init__(status_code, error_id, message, detail)


class EmailNotConfirmedException(ApiBaseException):
    def __init__(
        self,
        status_code=status.HTTP_401_UNAUTHORIZED,
        error_id='EMAIL_NOT_CONFIRMED',
        message='Email não verificado',
        detail=''
    ) -> None:
        super().__init__(status_code, error_id, message, detail)


class UsernameConflictException(ApiBaseException):
    def __init__(
        self,
        status_code=status.HTTP_409_CONFLICT,
        error_id='USERNAME_ALREADY_EXISTS',
        message='O nome de usuário já existe no sistema',
        detail=''
    ) -> None:
        super().__init__(status_code, error_id, message, detail)


class EmailConflictException(ApiBaseException):
    def __init__(
        self,
        status_code=status.HTTP_409_CONFLICT,
        error_id='EMAIL_ALREADY_EXISTS',
        message='O e-mail já existe no sistema',
        detail=''
    ) -> None:
        super().__init__(status_code, error_id, message, detail)


class UserNotFoundException(ApiBaseException):
    def __init__(
        self,
        status_code=status.HTTP_404_NOT_FOUND,
        error_id='USER_NOT_FOUND',
        message='O usuário não foi encontrado no sistema',
        detail=''
    ) -> None:
        super().__init__(status_code, error_id, message, detail)


class InvalidUsernamePasswordException(ApiBaseException):
    def __init__(
        self,
        status_code=status.HTTP_403_FORBIDDEN,
        error_id='INVALID_USERNAME_OR_PASSWORD',
        message='Usuário ou senha inválidos',
        detail=''
    ) -> None:
        super().__init__(status_code, error_id, message, detail)


class InvalidExpiredTokenException(ApiBaseException):
    def __init__(
        self,
        status_code=status.HTTP_401_UNAUTHORIZED,
        error_id='INVALID_OR_EXPIRED_TOKEN',
        message='Token de acesso inválido ou expirado',
        detail=''
    ) -> None:
        super().__init__(status_code, error_id, message, detail)


class NotEnoughPermissionsException(ApiBaseException):
    def __init__(
        self,
        status_code=status.HTTP_401_UNAUTHORIZED,
        error_id='NOT_ENOUGH_PERMISSION',
        message='Permissões não suficientes para o acesso desse recurso',
        detail=''
    ) -> None:
        super().__init__(status_code, error_id, message, detail)


def generic_exception_handler(_: Request, exception: Exception):
    return api_base_exception_handler(_, ApiBaseException())


def request_validation_error_handler(_: Request, exception: RequestValidationError):
    api_base_exception = RequestValidationException(
        detail=json.dumps(exception.errors())
    )
    return api_base_exception_handler(_, api_base_exception)


def api_base_exception_handler(_: Request, exception: ApiBaseException):
    return JSONResponse(
        status_code=exception.status_code,
        content={
            'status_code': exception.status_code,
            'error_id': exception.error_id,
            'message': exception.message,
            'detail': exception.detail,
        }
    )

