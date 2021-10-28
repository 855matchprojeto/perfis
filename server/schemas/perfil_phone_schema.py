from pydantic import Field
from pydantic import BaseModel
from typing import Optional
from uuid import UUID as GUID
from server.schemas.tipo_contato_schema import TipoContatoOutput


class PerfilPhonePostInput(BaseModel):

    phone: str = Field(example='19999999999')
    id_tipo_contato: Optional[int] = Field(None, example='1')

    def convert_to_dict(self):
        return self.dict()

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class PerfilPhoneUpdateInput(BaseModel):

    phone: Optional[str] = Field(example='19999999999')
    id_tipo_contato: Optional[int] = Field(example='1')

    def convert_to_dict(self):
        return self.dict()

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class PerfilPhoneOutput(BaseModel):

    guid: GUID = Field(example='44ddad94-94ee-4cdc-bce9-b5b126c9a714')
    phone: str = Field(example='19999999999')
    tipo_contato: Optional[TipoContatoOutput]

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

