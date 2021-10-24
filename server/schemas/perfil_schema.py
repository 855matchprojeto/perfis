from server.schemas import PerfilModelOutput, PerfilModelInput
from pydantic import Field, BaseModel, EmailStr
from datetime import datetime
from typing import List
from pydantic import BaseModel
from fastapi import Query
from uuid import UUID as GUID
from server.schemas.interesse_schema import InteresseOutput
from server.schemas.curso_schema import CursoOutput
from server.schemas.perfil_phone_schema import PerfilPhoneOutput
from server.schemas.perfil_email_schema import PerfilEmailOutput
from typing import Any, Optional, Literal


InterestQuery = Query(
    None,
    title="Query string para filtrar perfis a partir dos nomes de referência dos interesses listados no perfil do usuário",
    description="Query string para filtrar perfis a partir dos nomes de referência dos interesses listados no perfil do usuário",
)

CourseQuery = Query(
    None,
    title="Query string para filtrar perfis a partir dos nomes de referência dos cursos listados no perfil do usuário",
    description="Query string para filtrar perfis a partir dos nomes de referência dos cursos listados no perfil do usuário",
)

DisplayNameIlikeQuery = Query(
    None,
    title="Query string para filtrar perfis com nomes de exibição que contém esse valor",
    description="Query string para filtrar perfis com nomes de exibição que contém esse valor",
)


class PerfilOutput(BaseModel):

    guid: GUID = Field(example='44ddad94-94ee-4cdc-bce9-b5b126c9a714')
    guid_usuario: GUID = Field(example='44ddad94-94ee-4cdc-bce9-b5b126c9a714')
    nome_exibicao: Optional[str] = Field(example="Nome de exibição do usuário no perfil")
    bio: Optional[str] = Field(example='Texto de apresentação do usuário')
    interesses: List[InteresseOutput]
    cursos: List[CursoOutput]
    phones: List[PerfilPhoneOutput]
    emails: List[PerfilEmailOutput]

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class PaginatedPerfilOutput(PerfilModelOutput):

    items: List[PerfilOutput]
    previous_cursor: Optional[str] = Field(example='previous_cursor_token')
    next_cursor: Optional[str] = Field(example='next_cursor_token')
    previous_url: Optional[str] = Field(example='http://localhost/profiles/?page_size=10&cursor=previous_cursor_token')
    next_url: Optional[str] = Field(example='http://localhost/profiles/?page_size=10&cursor=next_cursor_token')

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

