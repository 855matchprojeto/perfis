from pydantic import Field
from pydantic import BaseModel
from typing import Optional
from uuid import UUID as GUID


class TipoContatoOutput(BaseModel):

    id: int = Field(example=1)
    nome_referencia: str = Field('whatsapp')
    nome_exibicao: Optional[str] = Field('whatsapp')
    descricao: Optional[str] = Field('Descrição sobre o tipo de contato')

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

