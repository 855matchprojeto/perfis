from pydantic import Field
from pydantic import BaseModel
from typing import Optional
from uuid import UUID as GUID
from server.schemas.tipo_contato_schema import TipoContatoOutput


class PerfilPhoneOutput(BaseModel):

    guid: GUID = Field(example='44ddad94-94ee-4cdc-bce9-b5b126c9a714')
    phone: str = Field(example='19999999999')
    tipo_contato: Optional[TipoContatoOutput]

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

