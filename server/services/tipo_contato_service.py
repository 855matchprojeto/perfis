from typing import List, Optional
from server.configuration.environment import Environment
from server.repository.tipo_contato_repository import TipoContatoRepository


class TipoContatoService:

    def __init__(self, tipo_contato_repo: Optional[TipoContatoRepository] = None,
                 environment: Optional[Environment] = None):
        self.tipo_contato_repo = tipo_contato_repo
        self.environment = environment

    async def get_all_tipos_contato(self):
        return await self.tipo_contato_repo.find_all_tipos_contato_by_filters([])

