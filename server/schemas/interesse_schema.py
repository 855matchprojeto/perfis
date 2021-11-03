from pydantic import Field
from pydantic import BaseModel
from typing import Optional


class InteresseOutput(BaseModel):

    id: int = Field(example=1)
    nome_referencia: str = Field(example='Nome usado para referenciar o "Interesse" no banco de dados')
    nome_exibicao: Optional[str] = Field(
        example='Esse campo pode ser usado como uma sugestão de nome de exibição nas telas do app'
    )
    descricao: Optional[str] = Field(example='Descrição sobre o interesse')

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


