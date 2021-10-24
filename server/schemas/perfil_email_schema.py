from pydantic import Field
from pydantic import BaseModel
from typing import Optional
from uuid import UUID as GUID


class PerfilEmailOutput(BaseModel):

    guid: GUID = Field(example='44ddad94-94ee-4cdc-bce9-b5b126c9a714')
    email: str = Field(example='teste@unicamp.br')

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

