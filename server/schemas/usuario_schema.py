from pydantic import Field, BaseModel, EmailStr
from typing import List, Optional


class CurrentUserToken(BaseModel):

    name: str
    username: str
    guid: str
    email: EmailStr
    roles: List[int]
    permissions: Optional[List[str]]


class CurrentUserOutput(BaseModel):

    name: str = Field(example='Teste')
    username: str = Field(example='username')
    guid: str = Field(example='78628c23-aae3-4d58-84a9-0c8d7ea63672')
    email: EmailStr = Field(example="teste@unicamp.br")

