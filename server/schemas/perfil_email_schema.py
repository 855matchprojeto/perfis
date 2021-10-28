from pydantic import Field, EmailStr
from pydantic import BaseModel
from typing import Optional
from uuid import UUID as GUID


class PerfilEmailPostInput(BaseModel):

    email: EmailStr = Field(example='teste@unicamp.br')

    def convert_to_dict(self):
        return self.dict()

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class PerfilEmailUpdateInput(BaseModel):

    email: EmailStr = Field(example='teste@unicamp.br')

    def convert_to_dict(self):
        return self.dict()

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


class PerfilEmailOutput(BaseModel):

    guid: GUID = Field(example='44ddad94-94ee-4cdc-bce9-b5b126c9a714')
    email: EmailStr = Field(example='teste@unicamp.br')

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

