from server.configuration.db import AsyncSession
from server.models.permissao_model import Permissao
from server.models.vinculo_permissao_funcao_model import VinculoPermissaoFuncao
from sqlalchemy import select
from typing import List, Optional
from server.configuration.environment import Environment
from sqlalchemy.orm import selectinload
from sqlalchemy import and_


class PermissaoRepository:

    def __init__(self, db_session: AsyncSession, environment: Optional[Environment] = None):
        self.db_session = db_session
        self.environment = environment

    async def find_permissions_by_roles_list(self, roles: List[int]) -> List[Permissao]:
        stmt = (
            select(Permissao).
            join(
                VinculoPermissaoFuncao,
                and_(
                    VinculoPermissaoFuncao.id_permissao == Permissao.id,
                    VinculoPermissaoFuncao.id_funcao.in_(roles)
                )
            ).options(
                selectinload(Permissao.vinculos_permissao_funcao)
            )
        )
        query = await self.db_session.execute(stmt)
        return query.scalars().all()
