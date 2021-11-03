from typing import List, Optional
from server.models.curso_model import Curso
from server.configuration.db import AsyncSession
from server.models.permissao_model import Permissao
from server.models.vinculo_permissao_funcao_model import VinculoPermissaoFuncao
from sqlalchemy import select
from typing import List, Optional
from server.configuration.environment import Environment
from sqlalchemy.orm import selectinload
from sqlalchemy import and_
from server.models.tipo_contato_model import TipoContato


class TipoContatoRepository:

    def __init__(self, db_session: AsyncSession, environment: Optional[Environment] = None):
        self.db_session = db_session
        self.environment = environment

    async def find_all_tipos_contato_by_filters(self, filters) -> List[Curso]:

        stmt = (
            select(TipoContato).
            where(
                *filters
            )
        )

        # Executando a query
        query = await self.db_session.execute(stmt)
        tipos_contato = query.scalars().unique().all()

        return tipos_contato

