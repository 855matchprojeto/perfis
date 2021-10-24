"""
    Módulo responsável por armazenar input e outputs de modelos
    construídos a partir do pydantic
"""

from pydantic import BaseModel


class PerfilModelInput(BaseModel):
    def convert_to_dict(self):
        raise NotImplementedError


class PerfilModelOutput(BaseModel):
    pass

