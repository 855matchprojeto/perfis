from pydantic import Field, BaseModel
from typing import Optional


class CursoOutput(BaseModel):

    id: int = Field(example=1)
    nome_exibicao: str = Field(
        example='Esse campo pode ser usado como uma sugestão de nome de exibição nas telas do app'
    )
    nome_referencia: str = Field(example='Nome usado para referenciar o "Curso" no banco de dados')
    descricao: Optional[str] = Field(example='Descrição sobre o curso')

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True


