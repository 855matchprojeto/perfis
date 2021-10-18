from server.schemas import AuthenticatorModelInput, AuthenticatorModelOutput
from pydantic import Field, BaseModel, EmailStr
from datetime import datetime
from typing import List


class ErrorOutput401(AuthenticatorModelOutput):
    status_code: int = Field(example=401)
    error_id: str = Field(example='ID único do tipo do erro no serviço')
    message: str = Field(example='Mensagem do erro')
    detail: str = Field(None, example='Detalhamento do erro')

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class ErrorOutput403(AuthenticatorModelOutput):
    status_code: int = Field(example=403)
    error_id: str = Field(example='ID único do tipo do erro no serviço')
    message: str = Field(example='Mensagem do erro')
    detail: str = Field(None, example='Detalhamento do erro')

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class ErrorOutput404(AuthenticatorModelOutput):
    status_code: int = Field(example=404)
    error_id: str = Field(example='ID único do tipo do erro no serviço')
    message: str = Field(example='Mensagem do erro')
    detail: str = Field(None, example='Detalhamento do erro')

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class ErrorOutput409(AuthenticatorModelOutput):
    status_code: int = Field(example=409)
    error_id: str = Field(example='ID único do tipo do erro no serviço')
    message: str = Field(example='Mensagem do erro')
    detail: str = Field(None, example='Detalhamento do erro')

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class ErrorOutput422(AuthenticatorModelOutput):

    status_code: int = Field(example=422)
    error_id: str = Field(example='ID único do tipo do erro no serviço')
    message: str = Field(example='Mensagem do erro')
    detail: str = Field(None, example='Detalhamento do erro')

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class ErrorOutput500(AuthenticatorModelOutput):

    status_code: int = Field(example=500)
    error_id: str = Field(example='ID único do tipo do erro no serviço')
    message: str = Field(example='Mensagem do erro')
    detail: str = Field(None, example='Detalhamento do erro')

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

